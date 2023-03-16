# from django.template.loader import get_template
# from django.http import HttpResponse
# from django.http import HttpResponse, JsonResponse, request
from datetime import date, datetime

from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.conf import settings
from django.template.loader import render_to_string
from django.http.response import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User

from vacations.models import Requests, Collaborator, Settings

from vacations.forms.requests_form import RequestsForm

from vacations.helpers.days import calculate_days
from vacations.helpers.days_taken import calculate_days_taken
from vacations.helpers.extra_email import create_mails_list, send_notification_mails

import holidays_co
import json
import os
import io
import pandas as pd


# Create your views here.
class RequestsListView(PermissionRequiredMixin, ListView):

    model = Requests
    template_name = 'requests/list.html'
    # context_object_name = 'requests'
    permission_required = 'vacations.view_requests'

    # queryset = Requests.objects.prefetch_related('collaborator', 'leader', 'final_acceptor').all()

    def get_context_data(self, **kwargs):
        ctx = super(RequestsListView, self).get_context_data(**kwargs)

        collaborator = Collaborator.objects.filter(user = self.request.user.id).first()
        if collaborator:
            requests = Requests.objects.filter(collaborator = collaborator.id)

            ctx['requests'] = requests
            ctx['days'] = calculate_days(collaborator.pk)[0]

        else:
            messages.error(self.request, 'Aun no se ha creado información de su usuario, por favor solicite la creación de su información en recursos humanos.')

        # pruebas = Collaborator.objects.raw(
        #     '''
        #     SELECT
        #         col.id,
        #         (15::NUMERIC / 365) * (now()::DATE - entry_at::DATE) - COALESCE(SUM(CASE WHEN req.request_completed THEN req.business_days_taken ELSE 0 END), 0) AS days_available,
        #         COALESCE(SUM(CASE WHEN req.request_completed THEN req.business_days_taken ELSE 0 END), 0) AS days_taken,
        #         SUM(CASE WHEN bon.bonus_state THEN bon.extra_days ELSE 0 END) AS days_extra
        #     FROM vacations_collaborator AS col
        #     LEFT JOIN vacations_requests AS req ON req.collaborator_id = col.id
        #     LEFT JOIN vacations_bonus AS bon ON bon.collaborator_id = col.id
        #     -- WHERE col.id = {}
        #     GROUP BY col.id;
        #     '''
        # )

        # print(pruebas)
        # print('Inicio'.center(30, '-'))
        # for prueba in pruebas:
        #     print(f'{prueba.user}, {prueba.days_available}, {prueba.days_taken}, {prueba.entry_at}, {prueba.days_available + prueba.days_extra}')
        # print('Fin'.center(30, '-'))

        return ctx


class RequestSavannaListView(PermissionRequiredMixin, ListView):

    model = Requests
    template_name = 'requests/sabana.html'
    context_object_name = 'requests'
    permission_required = 'vacations.view_settings'

    # queryset = Requests.objects.prefetch_related('collaborator', 'leader', 'final_acceptor').all()

    # def get_context_data(self, **kwargs):
    #     ctx = super(RequestSavannaListView, self).get_context_data(**kwargs)

        # collaborator = Collaborator.objects.filter(user = self.request.user.id).first()
        # if collaborator:
        #     requests = Requests.objects.filter(collaborator = collaborator.id)
        #     ctx['requests'] = requests

        # pruebas = Collaborator.objects.raw(
        #     '''
        #     SELECT
        #         col.id,
        #         (15::NUMERIC / 365) * (now()::DATE - entry_at::DATE) - COALESCE(SUM(CASE WHEN req.request_completed THEN req.business_days_taken ELSE 0 END), 0) AS days_available,
        #         COALESCE(SUM(CASE WHEN req.request_completed THEN req.business_days_taken ELSE 0 END), 0) AS days_taken,
        #         SUM(CASE WHEN bon.bonus_state THEN bon.extra_days ELSE 0 END) AS days_extra
        #     FROM vacations_collaborator AS col
        #     LEFT JOIN vacations_requests AS req ON req.collaborator_id = col.id
        #     LEFT JOIN vacations_bonus AS bon ON bon.collaborator_id = col.id
        #     -- WHERE col.id = {}
        #     GROUP BY col.id;
        #     '''
        # )

        # print(pruebas)
        # print('Inicio'.center(30, '-'))
        # for prueba in pruebas:
        #     print(f'{prueba.user}, {prueba.days_available}, {prueba.days_taken}, {prueba.entry_at}, {prueba.days_available + prueba.days_extra}')
        # print('Fin'.center(30, '-'))

        # collaborator_id = Collaborator.objects.get(user=self.request.user).id
        # ctx['avalaible_days'] = int(calculate_days(collaborator_id)[0].days_available)

        # return ctx


class RequestsCreateView(PermissionRequiredMixin, CreateView):

    model = Requests
    form_class = RequestsForm
    template_name = 'requests/create.html'
    success_url = reverse_lazy('vacations:requests_list')
    permission_required = 'vacations.add_requests'


    def form_valid(self, form):

        obj = form.save(commit=False)

        collaborator = Collaborator.objects.filter(user = self.request.user.id)
        if collaborator:
            obj.collaborator = Collaborator.objects.get(user = self.request.user.id)
        else:
            messages.error(self.request, 'No puedes registrar solicitudes')
            return redirect('vacations:requests_create')

        settings = Settings.objects.first()
        # print('final_acceptor: ', final_acceptor, type(final_acceptor))

        if settings:
            final_acceptor = settings.final_acceptor
            obj.final_acceptor = final_acceptor

        else:
            messages.error(self.request, 'No hay un aceptador final, no puedes registrar solicitudes')
            return redirect('vacations:requests_create')

        calendar_days, business_days = calculate_days_taken(obj.start_date_vacations, obj.end_date_vacations)
        if calendar_days and business_days > 0:
            obj.calendar_days_taken = calendar_days
            obj.business_days_taken = business_days

        else:
            messages.error(self.request, 'La fecha de fin debe ser superior a la de inicio')
            return redirect('vacations:requests_create')

        obj.save()
        messages.success(self.request, 'Solicitud creada con éxito')
        return super().form_valid(form)


    def get_success_url(self):

        # Send mails to leader, final acceptor and group of users in group_notify_request
        lst_mails = create_mails_list(['collaborator',
                                       'leader', 
                                    #    'final_acceptor',
                                       'group_notify_request'], self.object)

        subject      = 'Solicitud de vacaciones creada'
        collaborator = str(self.object.collaborator)
        mail_message = f'El colaborador {collaborator} ha creado una nueva solicitud de vacaciones'


        # FOR TEST
        # lst_mails = ['daniel.restrepo@phc.com.co']


        send_notification_mails(lst_mails, mail_message, subject, self.object)
        messages.success(self.request, 'Notificaciones enviadas con éxito')        


        return reverse_lazy('vacations:requests_list')


class RequestsDetailView(PermissionRequiredMixin, DetailView):

    model = Requests
    # form_class = RequestsForm
    template_name = 'requests/detail.html'
    context_object_name = 'request'
    # success_url = reverse_lazy('vacations:requests_list')
    permission_required = 'vacations.view_requests'

    # def get_context_data(self, **kwargs):
    #     ctx = super(RequestsDetailView, self).get_context_data(**kwargs)

    #     ctx['form'].fields['leader'].label_from_instance = lambda obj: "%s %s" % (obj.first_name, obj.last_name)
    #     ctx['form'].fields['final_acceptor'].label_from_instance = lambda obj: "%s %s" % (obj.first_name, obj.last_name)

    #     return ctx


# class RequestsSavannaDetailView(PermissionRequiredMixin, DetailView):

#     model = Requests
#     # form_class = RequestsForm
#     template_name = 'requests/detail_sabana.html'
#     context_object_name = 'request'
#     # success_url = reverse_lazy('vacations:requests_list')
#     permission_required = 'vacations.view_requests'

    # def get_context_data(self, **kwargs):
    #     ctx = super(RequestsDetailView, self).get_context_data(**kwargs)

    #     ctx['form'].fields['leader'].label_from_instance = lambda obj: "%s %s" % (obj.first_name, obj.last_name)
    #     ctx['form'].fields['final_acceptor'].label_from_instance = lambda obj: "%s %s" % (obj.first_name, obj.last_name)

    #     return ctx



class RequestsChangeView(PermissionRequiredMixin, UpdateView):

    model = Requests
    form_class = RequestsForm
    template_name = 'requests/change.html'
    success_url = reverse_lazy('vacations:requests_list')
    permission_required = 'vacations.change_requests'


    def get_context_data(self, **kwargs):
        ctx = super(RequestsChangeView, self).get_context_data(**kwargs)

        # ctx['form'].fields['leader'].label_from_instance = lambda obj: "%s %s" % (obj.first_name, obj.last_name)
        # ctx['form'].fields['final_acceptor'].label_from_instance = lambda obj: "%s %s" % (obj.first_name, obj.last_name)

        ctx['object'] = self.object

        return ctx


    def form_valid(self, form):

        obj = form.save(commit=False)

        # Final acceptor is overwrite by none when we update, get and add again
        settings = Settings.objects.first()

        if settings:
            final_acceptor = settings.final_acceptor
            obj.final_acceptor = final_acceptor

        else:
            messages.error(self.request, 'No hay un aceptador final, no puedes actualizar solicitudes')
            return redirect('vacations:requests_change', self.object.id)

        calendar_days, business_days = calculate_days_taken(obj.start_date_vacations, obj.end_date_vacations)
        if calendar_days and business_days > 0:
            obj.calendar_days_taken = calendar_days
            obj.business_days_taken = business_days

        else:
            messages.error(self.request, 'La fecha de fin debe ser superior a la de inicio')
            return redirect('vacations:requests_change', self.object.id)

        obj.accepted_leader = None
        obj.accepted_final_acceptor = None
        obj.request_completed = None

        obj.save()
        messages.success(self.request, 'Solicitud creada con éxito')
        return super().form_valid(form)


    def get_success_url(self):


        lst_mails = create_mails_list(['leader', 
                                       'collaborator', 
                                       'group_notify_request'], self.object)

        subject      = 'Solicitud de vacaciones modificada'

        collaborator = str(self.object.collaborator)
        mail_message = f'El colaborador {collaborator} ha modificado una solicitud previamente creada'


        # FOR TEST
        # lst_mails = ['daniel.restrepo@phc.com.co']


        send_notification_mails(lst_mails, mail_message, subject, self.object)
        messages.success(self.request, 'Notificaciones enviadas con éxito')



        return reverse_lazy('vacations:requests_change', args=[self.object.id])


class RequestsDeleteView(PermissionRequiredMixin, DeleteView):

    model = Requests
    form_class = RequestsForm
    template_name = 'requests/delete.html'
    success_url = reverse_lazy('vacations:requests_list')
    permission_required = 'vacations.delete_requests'
    context_object_name = 'requests'

    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Solicitud eliminada con éxito')
        return super(RequestsDeleteView, self).delete(*args, **kwargs)


def liquidation(request, pk):
    print(pk)

    requests = Requests.objects.get(pk = pk)

    collaborator_obj = requests.collaborator

    salary = collaborator_obj.salary
    vacations_value = (salary/30)*requests.calendar_days_taken
    deduction_value = (vacations_value*8)/100
    total_value = vacations_value - deduction_value

    context = {
        'id_card': collaborator_obj.id_card,
        'name': (collaborator_obj.user.first_name + ' ' + collaborator_obj.user.last_name).upper(),
        'salary': add_points_number(salary),
        'vacations_value': add_points_number(int(vacations_value)),
        'deduction_value': add_points_number(int(deduction_value)),
        'total_value': add_points_number(int(total_value)),
        'requests': requests
    }  

    return render(request, 'requests/liquidation.html', context)


class LeaderStateChangeView(PermissionRequiredMixin, UpdateView):

    model = Requests
    form_class = RequestsForm
    template_name = 'requests/change_leader_state.html'
    success_url = reverse_lazy('vacations:requests_list')
    permission_required = 'vacations.change_requests'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['request'] = self.object

        return context


    def form_valid(self, form):
        obj = form.save(commit=False)

        instance = Requests.objects.get(pk = self.object.id)
        print(f'{instance.accepted_leader}'.center(30, '-'))
        print(f'{obj.accepted_leader}'.center(30, '-'))

        obj.final_acceptor = instance.final_acceptor
        obj.date_leader = datetime.now()
        obj.accepted_final_acceptor = instance.accepted_final_acceptor
        obj.date_final_acceptor = instance.date_final_acceptor
        obj.request_completed = instance.request_completed
        obj.start_date_vacations = instance.start_date_vacations
        obj.end_date_vacations = instance.end_date_vacations
        obj.accepted_liquidation = instance.accepted_liquidation
        obj.path_liquidation = instance.path_liquidation

        messages.success(self.request, 'Estado actualizado con éxito')
        obj.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):

        collaborator   = str(self.object.collaborator)
        leader         = self.object.leader.first_name + ' ' + self.object.leader.last_name
        final_acceptor = self.object.final_acceptor.first_name + ' ' + self.object.final_acceptor.last_name
        accepted_leader = self.object.accepted_leader
        accepted_final_acceptor = self.object.accepted_final_acceptor

        send_notifications = False


        # Send emails based on the people who have accepted the request.
        #   - If the leader accepts, send notification to the final acceptor, the collaborator
        #     and group_notify_request
        if accepted_leader and accepted_final_acceptor is None:

            send_notifications = True

            subject = 'Un lider ha aceptado una solicitud de vacaciones, se procede a notificar el aceptador final'
            mail_message = (f'El lider {leader} ha aceptado la solicitud iniciada por el colaborador {collaborator}, ' +
                            f'se notifica al aceptador final {final_acceptor}')

            lst_mails = create_mails_list(['final_acceptor', 
                                           'collaborator', 
                                           'group_notify_request'], self.object)

        #   - If final acceptor and leader accept, 
        #     send to group_notify_request_accepted, group_notify_request and collaborator
        elif accepted_leader and accepted_final_acceptor:

            send_notifications = True

            subject = 'Un lider y el aceptador final han aceptado una solicitud de vacaciones'
            mail_message = (f'El lider {leader} y el aceptador final {final_acceptor} han aceptado ' +
                            f'la solicitud de vacaciones iniciada por el colaborador {collaborator}, esta se da por aceptada')

            lst_mails = create_mails_list(['group_notify_request_accepted', 
                                           'collaborator', 
                                           'group_notify_request'], self.object)

        #   - The leader input 'Pendiente' in the user interface, do nothing
        elif accepted_leader is None:
            pass

        #   - If the leader rejects, send to group_notify_request and collaborator
        elif not accepted_leader:

            send_notifications = True

            subject = 'Un lider ha rechazado una solicitud de vacaciones, dandola por terminada'
            mail_message = (f'El lider {leader} ha rechazado la solicitud de vacaciones ' +
                            f'iniciada por el colaborador {collaborator}, la solicitud se da por terminada')
            lst_mails = create_mails_list(['collaborator', 
                                           'group_notify_request'], self.object)


        if send_notifications:

            # FOR TEST
            # lst_mails = ['daniel.restrepo@phc.com.co']



            #################### IMPORTANTE PARA ENVIAR CORREOS ####################

            send_notification_mails(lst_mails, mail_message, subject, self.object)
            messages.success(self.request, 'Notificaciones enviadas con éxito')


        return reverse_lazy('vacations:requests_detail', args=[self.object.id])


class FinalAcceptorStateChangeView(PermissionRequiredMixin, UpdateView):

    model = Requests
    form_class = RequestsForm
    template_name = 'requests/change_final_acceptor_state.html'
    success_url = reverse_lazy('vacations:requests_list')
    permission_required = 'vacations.change_requests'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['request'] = self.object

        return context

    def form_valid(self, form):
        obj = form.save(commit=False)

        instance = Requests.objects.get(pk = self.object.id)
        # print(f'{instance.accepted_final_acceptor}'.center(30, '-'))
        # print(f'{obj.accepted_final_acceptor}'.center(30, '-'))

        obj.final_acceptor = instance.final_acceptor
        obj.date_leader = instance.date_leader
        # obj.accepted_final_acceptor = instance.accepted_final_acceptor
        obj.date_final_acceptor = datetime.today()
        obj.request_completed = instance.request_completed
        obj.start_date_vacations = instance.start_date_vacations
        obj.end_date_vacations = instance.end_date_vacations
        obj.accepted_liquidation = instance.accepted_liquidation
        obj.path_liquidation = instance.path_liquidation

        if obj.accepted_final_acceptor:
            obj.request_completed = obj.accepted_final_acceptor
        else:
            # obj.accepted_final_acceptor = instance.accepted_final_acceptor
            obj.request_completed = obj.accepted_final_acceptor

        messages.success(self.request, 'Estado actualizado con éxito')
        obj.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):

        collaborator   = str(self.object.collaborator)
        leader         = self.object.leader.first_name + ' ' + self.object.leader.last_name
        final_acceptor = self.object.final_acceptor.first_name + ' ' + self.object.final_acceptor.last_name        
        accepted_leader = self.object.accepted_leader
        accepted_final_acceptor = self.object.accepted_final_acceptor

        send_notifications = False

        # Send emails based on the people who have accepted the request.
        #   - If the final acceptor accepts, send notification to the leader, the collaborator
        #     and group_notify_request
        if accepted_leader and accepted_final_acceptor is None:

            send_notifications = True

            subject = 'El aceptador final ha aceptado una solicitud de vacaciones, se notifica al lider correspondiente'
            mail_message = (f'El aceptador final {final_acceptor} ha aceptado la solicitud iniciada por el colaborador {collaborator}, ' +
                            f'se notifica al lider correspondiente {leader}')
            lst_mails = create_mails_list(['leader', 
                                           'collaborator', 
                                           'group_notify_request'], self.object)

        #   - If final acceptor and leader accept, 
        #     send to group_notify_request_accepted, group_notify_request and collaborator
        elif accepted_leader and accepted_final_acceptor:

            send_notifications = True

            subject = 'Un lider y el aceptador final han aceptado una solicitud de vacaciones'
            mail_message = (f'El lider {leader} y el aceptador final {final_acceptor} han aceptado ' +
                            f'la solicitud de vacaciones iniciada por el colaborador {collaborator}, esta se da por aceptada')

            lst_mails = create_mails_list(['group_notify_request_accepted', 
                                           'collaborator', 
                                           'group_notify_request'], self.object)

        #   - The final acceptor input 'Pendiente' in the user interface, do nothing
        elif accepted_final_acceptor is None:
            pass

        #   - If the final acceptor rejects, send to group_notify_request, leader and collaborator
        elif not accepted_final_acceptor:

            send_notifications = True

            subject = 'El aceptador final ha rechazado una solicitud de vacaciones, dandola por terminada'
            mail_message = (f'El aceptador final {final_acceptor} ha rechazado la solicitud de vacaciones ' +
                            f'iniciada por el colaborador {collaborator}, la solicitud se da por terminada')

            lst_mails = create_mails_list(['collaborator',
                                           'leader' 
                                           'group_notify_request'], self.object)


        if send_notifications:

            # FOR TEST
            # lst_mails = ['daniel.restrepo@phc.com.co']

            send_notification_mails(lst_mails, mail_message, subject, self.object)
            messages.success(self.request, 'Notificaciones enviadas con éxito')
            

        return reverse_lazy('vacations:requests_detail', args=[self.object.id])


class LiquidationStateChangeView(PermissionRequiredMixin, UpdateView):

    model = Requests
    form_class = RequestsForm
    template_name = 'requests/change_liquidation_state.html'
    success_url = reverse_lazy('vacations:requests_list')
    permission_required = 'vacations.change_requests'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['request'] = self.object

        return context

    def form_valid(self, form):
        obj = form.save(commit=False)

        instance = Requests.objects.get(pk = self.object.id)
        # print(f'{instance.accepted_final_acceptor}'.center(30, '-'))
        # print(f'{obj.accepted_final_acceptor}'.center(30, '-'))

        obj.final_acceptor = instance.final_acceptor
        obj.date_leader = instance.date_leader
        obj.accepted_final_acceptor = instance.accepted_final_acceptor
        obj.date_final_acceptor = instance.date_final_acceptor
        obj.request_completed = instance.request_completed
        obj.start_date_vacations = instance.start_date_vacations
        obj.end_date_vacations = instance.end_date_vacations
        # obj.accepted_liquidation = instance.accepted_liquidation
        obj.path_liquidation = instance.path_liquidation

        messages.success(self.request, 'Actividad actualizada con éxito')
        obj.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):


        collaborator   = str(self.object.collaborator)
        accepted_liquidation = self.object.accepted_liquidation

        send_notifications = False

        # Send emails based on input state of liquidation.
        #   - If the liquidation is accepted, do nothing
        if accepted_liquidation:
            pass

        #   - The collaborator input 'Pendiente' in the user interface, do nothing
        elif accepted_liquidation is None:
            pass

        #   - If the liquidation is rejected, send to group_notify_liquidation_deny
        elif not accepted_liquidation:

            send_notifications = True

            subject = 'Una liquidacion ha sido rechazada'
            mail_message = f'El colaborador {collaborator} ha rechazado una liquidacion de vacaciones'
            lst_mails = create_mails_list(['group_notify_liquidation_deny'], self.object)


        if send_notifications:

            # FOR TEST
            # lst_mails = ['daniel.restrepo@phc.com.co']

            send_notification_mails(lst_mails, mail_message, subject, self.object)
            messages.success(self.request, 'Notificaciones enviadas con éxito')
            

        return reverse_lazy('vacations:requests_detail', args=[self.object.id])


# helper functions
def add_points_number(number):

    str_numb = str(number)
    rev_numb = ''.join(reversed(str_numb))
    str_numb = '.'.join(reversed([rev_numb[i:i+3][::-1] for i in range(0, len(str_numb), 3)]))

    return str_numb


# Views with ONLY development purpose
def _load_historic(request):
    import pandas as pd
    import numpy as np

    import sys
    if sys.version_info[0] < 3: 
        from StringIO import StringIO
    else:
        from io import StringIO    

    # df = pd.read_excel('Historico vacaciones.xlsx', engine='openpyxl')

    # csv_df = df.to_csv()

    # print(csv_df)


    

    csv_df = StringIO(''',Colaborador,Fecha de inicio,Fecha final,dias habiles
0,Manuel Rivera,2017-12-26,2017-12-26,1
1,Manuel Rivera,2018-10-08,2018-10-12,5
2,Manuel Rivera,2018-12-26,2018-12-28,3
3,Manuel Rivera,2019-12-02,2019-12-04,3
4,Manuel Rivera,2019-12-23,2019-12-23,1
5,Manuel Rivera,2019-12-27,2019-12-28,2
6,Manuel Rivera,2020-01-02,2020-01-02,1
7,Manuel Rivera,2020-03-26,2020-03-30,3
8,Manuel Rivera,2020-04-27,2020-04-28,2
9,Manuel Rivera,2020-05-04,2020-05-06,3
10,Manuel Rivera,2020-09-30,2020-09-30,1
11,Manuel Rivera,2020-10-01,2020-10-02,2
12,Manuel Rivera,2020-10-28,2020-10-30,3
13,Manuel Rivera,2021-01-04,2021-01-08,5
14,Manuel Rivera,2021-03-11,2021-03-12,2
15,Manuel Rivera,2021-10-19,2021-10-19,1
16,Manuel Rivera,2021-12-21,2022-01-07,14
17,ALEX IGIRIO,2020-04-02,2020-04-02,1
18,ALEX IGIRIO,2020-04-07,2020-04-08,2
19,ALEX IGIRIO,2021-01-04,2021-01-08,5
20,Daniel Restrepo,2020-05-05,2020-05-07,5
21,Daniel Restrepo,2021-10-11,2021-10-15,5
22,Caterine Londoño,2017-11-07,2017-11-10,4
23,Caterine Londoño,2018-01-02,2018-01-03,2
24,Caterine Londoño,2018-08-27,2018-08-31,5
25,Caterine Londoño,2018-10-26,2018-10-31,4
26,Caterine Londoño,2018-11-01,2018-11-20,10
27,Caterine Londoño,2018-12-26,2018-12-28,3
28,Caterine Londoño,2019-08-26,2019-08-30,5
29,Caterine Londoño,2019-12-02,2019-12-11,5
30,Caterine Londoño,2020-04-06,2020-04-08,3
31,Caterine Londoño,2020-08-27,2020-08-28,2
32,Caterine Londoño,2021-02-15,2021-02-19,5
33,Caterine Londoño,2021-08-26,2021-08-31,4
34,Caterine Londoño,2021-09-01,2021-09-03,3
35,Caterine Londoño,2021-12-24,2021-12-31,6
36,Laura Marin,2017-07-17,2017-07-31,11
37,Laura Marin,2017-08-01,2017-08-03,3
38,Laura Marin,2017-08-21,2017-08-21,1
39,Laura Marin,2017-12-26,2017-12-27,2
40,Laura Marin,2018-12-11,2018-12-28,12
41,Laura Marin,2019-01-02,2019-01-08,5
42,Laura Marin,2018-03-22,2018-03-22,1
43,Laura Marin,2018-07-08,2018-07-09,2
44,Laura Marin,2018-12-10,2018-12-17,6
45,Laura Marin,2020-03-26,2020-03-26,1
46,Laura Marin,2020-03-31,2020-03-31,1
47,Laura Marin,2020-04-29,2020-04-29,1
48,Laura Marin,2020-06-02,2020-06-02,1
49,Laura Marin,2020-07-14,2020-07-14,1
50,Laura Marin,2020-09-15,2020-09-15,1
51,Laura Marin,2020-12-21,2020-12-23,3
52,Laura Marin,2020-12-30,2020-12-30,1
53,Laura Marin,2021-03-10,2021-03-10,1
54,Laura Marin,2021-04-15,2021-04-15,1
55,Laura Marin,2021-10-19,2021-10-19,1
56,Laura Marin,2021-12-13,2021-12-31,13
57,Yaneth Montoya,2013-10-18,2013-10-31,10
58,Yaneth Montoya,2013-11-01,2013-11-18,12
59,Yaneth Montoya,2015-10-05,2015-10-09,5
60,Yaneth Montoya,2016-10-10,2016-10-14,5
61,Yaneth Montoya,2017-01-06,2017-01-06,1
62,Yaneth Montoya,2017-01-10,2017-01-11,2
63,Yaneth Montoya,2018-01-02,2018-01-10,6
64,Yaneth Montoya,2018-04-30,2018-04-30,1
65,Yaneth Montoya,2018-10-12,2018-10-12,1
66,Yaneth Montoya,2019-01-04,2019-01-15,7
67,Yaneth Montoya,2019-02-04,2019-02-13,8
68,Yaneth Montoya,2019-06-21,2019-06-28,5
69,Yaneth Montoya,2019-07-02,2019-07-03,2
70,Yaneth Montoya,2019-12-02,2019-12-03,2
71,Yaneth Montoya,2020-04-24,2020-04-24,1
72,Yaneth Montoya,2020-04-30,2020-04-30,1
73,Yaneth Montoya,2020-05-18,2020-05-18,1
74,Yaneth Montoya,2020-05-22,2020-05-22,1
75,Yaneth Montoya,2020-05-25,2020-05-25,1
76,Yaneth Montoya,2020-09-04,2020-09-04,1
77,Yaneth Montoya,2020-09-17,2020-09-18,2
78,Yaneth Montoya,2020-10-13,2020-10-13,1
79,Yaneth Montoya,2021-01-04,2021-01-15,9
80,Yaneth Montoya,2021-08-06,2021-08-13,6
81,Yaneth Montoya,2021-10-21,2021-10-22,2
82,Yaneth Montoya,2021-12-29,2022-01-07,8
83,CARO RUIZ,2020-03-27,2020-03-27,1
84,CARO RUIZ,2020-04-06,2020-04-08,2
85,CARO RUIZ,2021-06-01,2021-06-11,8
86,CARO RUIZ,2022-01-18,2022-01-19,2
87,Juan Llano,2020-02-13,2020-02-14,2
88,Juan Llano,2020-04-17,2020-04-17,1
89,Juan Llano,2020-08-05,2020-08-06,2
90,Juan Llano,2020-12-21,2020-12-30,6
91,Juan Llano,2021-07-26,2021-07-31,5
92,Juan Llano,2021-10-25,2021-10-28,4
93,Viviana Rueda,2014-09-15,2014-09-19,5
94,Viviana Rueda,2015-10-13,2015-10-23,9
95,Viviana Rueda,2016-07-01,2016-07-01,1
96,Viviana Rueda,2016-07-21,2016-07-22,2
97,Viviana Rueda,2017-02-27,2017-02-28,2
98,Viviana Rueda,2017-03-01,2017-03-03,3
99,Viviana Rueda,2017-07-21,2017-07-21,1
100,Viviana Rueda,2017-07-27,2017-07-27,1
101,Viviana Rueda,2018-02-08,2018-02-28,15
102,Viviana Rueda,2018-03-01,2018-03-13,7
103,Viviana Rueda,2018-09-03,2018-09-10,6
104,Viviana Rueda,2019-03-01,2019-03-05,5
105,Viviana Rueda,2019-08-20,2019-08-30,9
106,Viviana Rueda,2019-12-02,2019-12-06,4
107,Viviana Rueda,2019-12-31,2020-01-06,4
108,Viviana Rueda,2020-03-31,2020-03-31,1
109,Viviana Rueda,2020-04-02,2020-04-02,1
110,Viviana Rueda,2020-04-07,2020-04-07,1
111,Viviana Rueda,2020-05-28,2020-05-28,1
112,Viviana Rueda,2020-06-23,2020-06-23,1
113,Viviana Rueda,2020-10-05,2020-10-09,5
114,Viviana Rueda,2021-01-12,2021-01-22,9
115,Viviana Rueda,2021-03-29,2021-03-29,1
116,Viviana Rueda,2021-07-19,2021-07-23,4
117,Viviana Rueda,2021-09-01,2021-09-02,2
118,Fabio Avella,2012-04-11,2012-04-11,1
119,Fabio Avella,2012-08-27,2012-08-27,1
120,Fabio Avella,2012-10-19,2012-10-26,6
121,Fabio Avella,2012-12-19,2012-12-31,8
122,Fabio Avella,2013-10-18,2013-10-28,7
123,Fabio Avella,2013-12-26,2013-12-31,4
124,Fabio Avella,2014-08-19,2014-08-22,4
125,Fabio Avella,2014-12-29,2014-12-31,3
126,Fabio Avella,2015-01-02,2015-01-02,1
127,Fabio Avella,2015-12-28,2015-12-29,2
128,Fabio Avella,2016-01-04,2016-01-08,5
129,Fabio Avella,2016-03-10,2016-03-11,2
130,Fabio Avella,2016-10-18,2016-10-21,4
131,Fabio Avella,2016-12-26,2016-12-28,3
132,Fabio Avella,2017-01-02,2017-01-05,4
133,Fabio Avella,2017-06-30,2017-06-30,1
134,Fabio Avella,2017-07-04,2017-07-04,1
135,Fabio Avella,2017-10-17,2017-10-31,11
136,Fabio Avella,2017-11-21,2017-11-22,2
137,Fabio Avella,2018-07-18,2018-07-19,2
138,Fabio Avella,2018-08-17,2018-08-31,11
139,Fabio Avella,2018-10-25,2018-10-26,2
140,Fabio Avella,2019-05-08,2019-05-13,4
141,Fabio Avella,2019-12-04,2019-12-08,4
142,Fabio Avella,2020-05-01,2020-05-01,1
143,Fabio Avella,2020-09-28,2020-09-30,3
144,Fabio Avella,2020-10-01,2020-10-02,2
145,Fabio Avella,2021-05-14,2021-05-14,1
146,Fabio Avella,2021-05-18,2021-05-18,1
147,Fabio Avella,2021-05-24,2021-05-26,3
148,Fabio Avella,2021-11-11,2021-11-12,2
149,Camilo Corredor,2019-09-16,2019-09-22,5
150,Camilo Corredor,2020-03-26,2020-03-26,1
151,Camilo Corredor,2020-04-01,2020-04-01,1
152,Camilo Corredor,2020-04-07,2020-04-07,1
153,Camilo Corredor,2020-10-08,2020-10-09,2
154,Camilo Corredor,2021-01-04,2021-01-08,5
155,Camilo Corredor,2021-03-29,2021-03-29,1
156,Camilo Corredor,2021-07-19,2021-07-23,4
157,Camilo Corredor,2021-10-08,2021-10-08,1
158,Camilo Corredor,2021-11-05,2021-11-17,8
159,MARIA ESCOBAR,2021-05-10,2021-05-14,5
160,MARIA ESCOBAR,2021-06-30,2021-07-02,3
161,MARIA ESCOBAR,2022-01-03,2022-01-07,5
162,Valentina Bedoya,2021-12-06,2021-12-27,15
163,DANIEL ALEJANDRO LONDONO,2021-06-24,2021-07-02,7
164,Mateo Ortiz,2022-01-11,2022-01-14,4
165,Camilo Moreno,2019-12-02,2019-12-05,4
166,Camilo Moreno,2020-04-01,2020-04-01,1
167,Camilo Moreno,2020-04-03,2020-04-03,1
168,Camilo Moreno,2020-04-06,2020-04-06,1
169,Camilo Moreno,2020-12-28,2020-12-30,3
170,Camilo Moreno,2021-01-04,2021-01-08,5
171,Camilo Laverde,2020-10-25,2020-10-29,5
''')


    df = pd.read_csv(csv_df, sep=",")

    df['Fecha de inicio'] = pd.to_datetime(df['Fecha de inicio'], format='%Y-%m-%d')
    df['Fecha final']     = pd.to_datetime(df['Fecha final'], format='%Y-%m-%d')
    

    def print_full(x):
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 2000)
        pd.set_option('display.float_format', '{:20,.2f}'.format)
        pd.set_option('display.max_colwidth', None)
        print(x)
        pd.reset_option('display.max_rows')
        pd.reset_option('display.max_columns')
        pd.reset_option('display.width')
        pd.reset_option('display.float_format')
        pd.reset_option('display.max_colwidth')    

    print(df.info())


    name2col = {(colab.user.first_name + ' ' + colab.user.last_name).upper():colab
                 for colab in Collaborator.objects.all()}

    name2obj = {(user.first_name + ' ' + user.last_name).upper():user for user in User.objects.all()}

    l = list(name2obj.keys())
    l.sort()

    # Replace colaborator names for obj
    for i in range(len(df)):
        name = df.at[i, 'Colaborador']
        if name.upper() in name2col.keys():
            df.at[i, 'Colaborador'] = name2col[name.upper()]

    
    # Replace lider's names for ids
    # for name in df['Lider'].unique():
        
    #     if isinstance(name, str): 
    #         ori_name = name
    #         name = name.upper()

    #         for name_bd in name2obj.keys():

    #             if name in name_bd:
    #                 df.loc[df['Lider']==ori_name, 'Lider'] = name2obj[name_bd]

    #                break
    df['Lider'] = None

    df['dias calendario'] = (df['Fecha final'] - df['Fecha de inicio']).dt.days + 1

    df = df.replace({np.nan: None})

    del df['Unnamed: 0']
    # del df['Unnamed: 7']
    # del df['Unnamed: 8']

    print_full(df)
    print(df.columns)

    # Insert objects
    for i in range(len(df)):

        collaborator  = df.at[i, 'Colaborador']
        leader        = df.at[i, 'Lider']
        start         = df.at[i, 'Fecha de inicio']
        end           = df.at[i, 'Fecha final']
        business_days = df.at[i, 'dias habiles']
        calendar_days = df.at[i, 'dias calendario']

        params = {
            'collaborator' :collaborator,
            'start_date_vacations' :start,
            'end_date_vacations'   :end,
            'calendar_days_taken' :calendar_days,
            'business_days_taken' :business_days,
            'request_completed' :True,
            'accepted_liquidation' :True

        }

        if not leader is None:
            params['leader'] = leader
        else:
            params['leader'] = User.objects.get(id=3)


        r = Requests(**params)

        r.save()


    return redirect('dashboard:home')


def _create_colaborators(request):

    for user in User.objects.all():
        c = Collaborator(
                user = user,
                entry_at = date(2000, 1, 1)
        )
        c.save()

    return redirect('dashboard:home')


def download_table(request):

    base = settings.PROJECT_PATH
    path_file = f'{base}/cache/datos_solicitudes.xlsx'

    print(request.body)
    all_data = json.loads(request.body)

    save_data_xlsx(all_data, path_file)

    # sending response
    response = HttpResponse(io.open(path_file, mode="rb").read(), content_type='application/xlsx')
    response['Content-Disposition'] = 'attachment; filename="datos_solicitudes.xlsx"'

    # delete .xlsx file
    os.remove(path_file)

    return response


def save_data_xlsx(all_data:list, path_file:str):
    """Summary
    
    Stores the data of a time series plotted in the front of 
    the query section of the mec in an xlsx file.
    Each time series is on a different excel sheet with its 
    corresponding search parameters and filters used    
    
    Args:
        all_data (list): List with time series data
        path_file (str): Path where save the generate xlsx file
    """
    # Save all data in a excel file
    #   Initialize writer
    writer = pd.ExcelWriter(path_file, engine='xlsxwriter')
    workbook = writer.book

    # Iterate about array from graphed data
    for i, time_serie_data in enumerate(all_data):

        # Add a new sheet with 
        sheet_name =  str(i) + ' ' + time_serie_data['component']['component']
        worksheet = workbook.add_worksheet(sheet_name)
        writer.sheets[sheet_name] = worksheet


        # Add meta data about the query
        worksheet.write_string(0, 0, sheet_name)

        worksheet.write_string(1, 0, 'Metrica:')
        worksheet.write_string(1, 1, time_serie_data['metric']['fields']['metric'])

        worksheet.write_string(2, 0, 'Componente:')
        worksheet.write_string(2, 1, time_serie_data['component']['component'])

        worksheet.write_string(3, 0, 'Unidades:')
        worksheet.write_string(3, 1, time_serie_data['unit'])

        worksheet.write_string(4, 0, 'Periodicidad:')
        worksheet.write_string(4, 1, time_serie_data['period'][1])

        worksheet.write_string(5, 0, 'Intervalo temporal:')
        worksheet.write_string(5, 1, time_serie_data['start_date'][:10])
        worksheet.write_string(5, 2, time_serie_data['limit_date'][:10])

        worksheet.write_string(6, 0, 'Metodo de resampleo:')
        worksheet.write_string(6, 1, time_serie_data['resample'][1])


        # Add inferential statistics
        worksheet.write_string(1, 4, 'Media:')
        worksheet.write_string(1, 5, str(time_serie_data['response']['average']))

        worksheet.write_string(2, 4, 'Mediana:')
        worksheet.write_string(2, 5, str(time_serie_data['response']['average']))

        worksheet.write_string(3, 4, 'Maxima:')
        worksheet.write_string(3, 5, str(time_serie_data['response']['maximum']))

        worksheet.write_string(4, 4, 'Minima:')
        worksheet.write_string(4, 5, str(time_serie_data['response']['minimum']))

        worksheet.write_string(5, 4, 'Percentil 05:')
        worksheet.write_string(5, 5, str(time_serie_data['response']['percentile_05']))

        worksheet.write_string(6, 4, 'Percentil 95:')
        worksheet.write_string(6, 5, str(time_serie_data['response']['percentile_95']))

        worksheet.write_string(7, 4, 'Desviación estandar:')
        worksheet.write_string(7, 5, str(time_serie_data['response']['standard_deviation']))


        # Add filters
        worksheet.write_string(1, 7, 'Filtros:')
        for i, (filter_key, value) in enumerate(time_serie_data['f'].items()):
            worksheet.write_string(1+i, 8, filter_key)
            worksheet.write_string(1+i, 9, value[1])


        # Add info from time series
        #   Values
        worksheet.write_string(9, 0, 'Serie de tiempo:')
        data = {
            'Fecha': time_serie_data['response']['time_array'],
            'Valor': time_serie_data['response']['values_array']
            }
        df = pd.DataFrame(data)
        df['Fecha'] = pd.to_datetime(df['Fecha'], format='%Y-%m-%dT%H:%M:%S')
        df.to_excel(writer, sheet_name=sheet_name, startrow=10, startcol=0, index=False)

        #   Histogram
        worksheet.write_string(9, 4, 'Histograma:')
        bin_edges = time_serie_data['response']['bin_edges']
        processed_bins = [f'{bin_edges[i-1]}-{bin_edges[i]}' for i in range(1, len(bin_edges))]
        data = {
            'Bins': processed_bins,
            'Frecuencia': time_serie_data['response']['frecuency']
            }
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name=sheet_name, startrow=10 , startcol=4, index=False)


        # Adjust width of columns
        for i in range(10):
            worksheet.set_column(i, i, 23)    

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()    