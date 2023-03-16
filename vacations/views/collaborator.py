from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http.response import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator
from django.db import connection

from vacations.models import Collaborator, STATE, User

from vacations.forms.collaborator_form import CollaboratorForm

import pandas as pd
from io import BytesIO

# Create your views here.
def download_collaborators(request):
    # query = Collaborator.objects.all().values_list('user', 'entry_at', 'salary', 'state')

    cursor = connection.cursor()

    query = '''
    SELECT
        (SELECT COALESCE(username, '') FROM auth_user WHERE auth_user.id = col.user_id) AS username,
        col.entry_at,
        (15::NUMERIC / 365) * (now()::DATE - entry_at::DATE) AS days_vacations,
        (SELECT COALESCE(SUM(vacations_bonus.extra_days), 0) FROM vacations_bonus WHERE vacations_bonus.collaborator_id = col.id) AS days_extra,
        (SELECT COALESCE(SUM(vacations_requests.business_days_taken), 0) FROM vacations_requests WHERE vacations_requests.collaborator_id = col.id AND vacations_requests.request_completed = TRUE) AS days_taken,
        (
            (15::NUMERIC / 365) * (now()::DATE - entry_at::DATE) +
            (SELECT COALESCE(SUM(vacations_bonus.extra_days), 0) FROM vacations_bonus WHERE vacations_bonus.collaborator_id = col.id) -
            (SELECT COALESCE(SUM(vacations_requests.business_days_taken), 0) FROM vacations_requests WHERE vacations_requests.collaborator_id = col.id AND vacations_requests.request_completed = TRUE)
        ) AS days_available,
        col.state
    FROM vacations_collaborator AS col;
    '''

    cursor.execute(query)

    result_query = cursor.fetchall()

    df = pd.DataFrame(result_query)
    with BytesIO() as b:
        # Use the StringIO object as the filehandle.
        writer = pd.ExcelWriter(b, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Colaboradores', header=('Usuario', 'Fecha ingreso', 'Días vacaciones', 'Días extras', 'Días tomados', 'Días disponibles', 'Estado'), index=False)
        writer.save()
        filename = 'Colaboradores'
        content_type = 'application/vnd.ms-excel'
        response = HttpResponse(b.getvalue(), content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename="' + filename + '.xlsx"'
        return response


class CollaboratorListView(PermissionRequiredMixin, ListView):

    model = Collaborator
    template_name = 'collaborator/list.html'
    # context_object_name = 'collaborators'
    permission_required = 'vacations.view_collaborator'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['states'] = STATE

        users = User.objects.filter(pk__in = Collaborator.objects.values_list('user', flat = True))
        context['users'] = users

        state = self.request.GET.get('state', '')
        user = self.request.GET.get('user', '')

        context['state'] = int(state) if state else ''
        context['user'] = int(user) if user else ''

        if state:
            state = f'col.state = {state}'

        if user:
            user = f'col.user_id = {user}'

        if state or user:
            where = 'WHERE'
        else:
            where = ''

        if state and user:
            too = 'AND'
        else:
            too = ''

        collaborators = Collaborator.objects.raw(
            '''
            SELECT
                col.id,
                (15::NUMERIC / 365) * (now()::DATE - entry_at::DATE) AS days_vacations,
                (SELECT COALESCE(SUM(vacations_bonus.extra_days), 0) FROM vacations_bonus WHERE vacations_bonus.collaborator_id = col.id) AS days_extra,
                (SELECT COALESCE(SUM(vacations_requests.business_days_taken), 0) FROM vacations_requests WHERE vacations_requests.collaborator_id = col.id AND vacations_requests.request_completed = TRUE) AS days_taken,
                (
                    (15::NUMERIC / 365) * (now()::DATE - entry_at::DATE) +
                    (SELECT COALESCE(SUM(vacations_bonus.extra_days), 0) FROM vacations_bonus WHERE vacations_bonus.collaborator_id = col.id) -
                    (SELECT COALESCE(SUM(vacations_requests.business_days_taken), 0) FROM vacations_requests WHERE vacations_requests.collaborator_id = col.id AND vacations_requests.request_completed = TRUE)
                ) AS days_available
            FROM vacations_collaborator AS col
            {} {} {} {};
            '''.format(where, state, too, user)
        )

        # print(collaborators)
        # print('Inicio'.center(30, '-'))
        # for collaborator in collaborators:
        #     print(
        #         f'''{collaborator.user},
        #         {collaborator.entry_at},
        #         {collaborator.days_available},
        #         {collaborator.days_taken},
        #         {collaborator.days_extra}''')
        # print('Fin'.center(30, '-'))

        collaborators_paginator = Paginator(collaborators, 10)

        page_num = self.request.GET.get('page')

        page = collaborators_paginator.get_page(page_num)

        context['count'] = collaborators_paginator.count
        context['page'] = page

        return context


# class CollaboratorSavannaListView(PermissionRequiredMixin, ListView):

#     model = Collaborator
#     template_name = 'collaborator/list.html'
#     # context_object_name = 'collaborators'
#     permission_required = 'vacations.view_collaborator'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         collaborators = Collaborator.objects.raw(
#             '''
#             SELECT
#                 col.id,
#                 (15::NUMERIC / 365) * (now()::DATE - entry_at::DATE) AS days_vacations,
#                 (SELECT COALESCE(SUM(vacations_bonus.extra_days), 0) FROM vacations_bonus WHERE vacations_bonus.collaborator_id = col.id) AS days_extra,
#                 (SELECT COALESCE(SUM(vacations_requests.business_days_taken), 0) FROM vacations_requests WHERE vacations_requests.collaborator_id = col.id AND vacations_requests.request_completed = TRUE) AS days_taken,
#                 (
#                     (15::NUMERIC / 365) * (now()::DATE - entry_at::DATE) +
#                     (SELECT COALESCE(SUM(vacations_bonus.extra_days), 0) FROM vacations_bonus WHERE vacations_bonus.collaborator_id = col.id) -
#                     (SELECT COALESCE(SUM(vacations_requests.business_days_taken), 0) FROM vacations_requests WHERE vacations_requests.collaborator_id = col.id AND vacations_requests.request_completed = TRUE)
#                 ) AS days_available
#             FROM vacations_collaborator AS col;
#             -- WHERE col.state = 1;
#             '''
#         )

#         # print(collaborators)
#         # print('Inicio'.center(30, '-'))
#         # for collaborator in collaborators:
#         #     print(
#         #         f'''{collaborator.user},
#         #         {collaborator.entry_at},
#         #         {collaborator.days_available},
#         #         {collaborator.days_taken},
#         #         {collaborator.days_extra}''')
#         # print('Fin'.center(30, '-'))

#         collaborators_paginator = Paginator(collaborators, 10)

#         page_num = self.request.GET.get('page')

#         page = collaborators_paginator.get_page(page_num)

#         context['count'] = collaborators_paginator.count
#         context['page'] = page
#         return context


class CollaboratorCreateView(PermissionRequiredMixin, CreateView):

    model = Collaborator
    form_class = CollaboratorForm
    template_name = 'collaborator/create.html'
    success_url = reverse_lazy('vacations:collaborators_list')
    permission_required = 'vacations.add_collaborator'

    def form_valid(self, form):
        messages.success(self.request, 'Colaborador creado con éxito')
        return super().form_valid(form)


class CollaboratorUpdateView(PermissionRequiredMixin, UpdateView):

    model = Collaborator
    form_class = CollaboratorForm
    template_name = 'collaborator/change.html'
    success_url = reverse_lazy('vacations:collaborators_list')
    permission_required = 'vacations.change_collaborator'

    def form_valid(self, form):
        obj = form.save(commit=False)
        messages.success(self.request, 'Colaborador actualizado con éxito')
        obj.save()

        return HttpResponseRedirect(self.get_success_url())


class CollaboratorDeleteView(PermissionRequiredMixin, DeleteView):

    model = Collaborator
    template_name = 'collaborator/delete.html'
    success_url = reverse_lazy('vacations:collaborators_list')
    context_object_name = 'collaborator'
    permission_required = 'vacations.delete_collaborator'


    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Colaborador eliminado con éxito')
        return super(CollaboratorDeleteView, self).delete(*args, **kwargs)
