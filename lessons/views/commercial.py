from django.http import HttpResponse

from django.contrib.auth.models import User
import json

from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, DetailView, FormView, UpdateView, DeleteView
from django.http import JsonResponse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import connection

from lessons.models import (Commercial, 
                            PreventiveActions, 
                            CommercialLesson, 
                            RelatedArea, 
                            PreventiveActionsCommercialLesson,
                            CommercialRelatedArea,
                            CommercialUser)

from lessons.old_forms import CommercialForm
from lessons.models import RelatedArea


class CommercialListView(PermissionRequiredMixin, ListView):

    model = Commercial
    template_name = 'commercial/list.html'
    context_object_name = 'commercial'
    permission_required = 'lessons.view_commercial'

    queryset = Commercial.objects.prefetch_related('business_manager', 'client',  'service_type').all()

    ordering = ['-id']


class CommercialDetailView(PermissionRequiredMixin, DetailView):
    model = Commercial
    template_name = 'commercial/detail.html'
    context_object_name = 'commercial'
    permission_required = 'lessons.view_commercial'

    queryset = Commercial.objects.prefetch_related('business_manager', 'client',  'service_type').all()

    def get_context_data(self, **kwargs):

        ctx = super(CommercialDetailView, self).get_context_data(**kwargs)

        self.object = self.get_object()
        id_commercial = self.object.id

        ctx = get_data_commercial(id_commercial, ctx)

        return ctx


class CommercialCreateView(PermissionRequiredMixin, CreateView):

    model = Commercial
    form_class = CommercialForm
    template_name =  'commercial/create.html'
    # success_url = reverse_lazy('lessons:connection_studies_list')
    permission_required = 'lessons.add_commercial'


    def get_success_url(self):

        id_commercial = self.object.id

        save_all_lessons(self)

        return reverse_lazy('lessons:commercial_list')

    def get_context_data(self, **kwargs):
        ctx = super(CommercialCreateView, self).get_context_data(**kwargs)
     
        ctx['form'].fields['business_manager'].label_from_instance = lambda obj: "%s %s" % (obj.first_name, obj.last_name)
        ctx['users'] = User.objects.all()
        ctx['related_area'] = RelatedArea.objects.all()

        return ctx

    def form_valid(self, form):
        return super().form_valid(form)


class CommercialChangeView(PermissionRequiredMixin, UpdateView):
    model = Commercial
    template_name = 'commercial/change.html'
    success_url = reverse_lazy('lessons:commercial_list')
    form_class = CommercialForm
    permission_required = 'lessons.change_commercial'

    def get_context_data(self, **kwargs):
        ctx = super(CommercialChangeView, self).get_context_data(**kwargs)

        self.object = self.get_object()
        id_commercial = self.object.id
        # print('id_commercial: ', id_commercial)

        ctx = get_data_commercial(id_commercial, ctx)

        ctx['users'] = User.objects.all()
        ctx['related_area'] = RelatedArea.objects.all()        

        return ctx

    def get_success_url(self):

        id_commercial = self.object.id

        # Delete all lessons negatives/positives/preventives
        delete_all_lessons(id_commercial)

        # Add again
        save_all_lessons(self)

        return reverse_lazy('lessons:commercial_list')


class CommercialDeleteView(PermissionRequiredMixin, DeleteView):
    model = Commercial
    template_name = 'commercial/delete.html'
    success_url = reverse_lazy('lessons:commercial_list')
    context_object_name = 'commercial'
    permission_required = 'lessons.delete_commercial'

    def get_success_url(self):

        id_commercial = self.object.id

        # Delete all lessons negatives/positives/preventives
        delete_all_lessons(id_commercial)

        return reverse_lazy('lessons:commercial_list')    
    
    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Leccion comercial eliminada con exito') 
        return super(CommercialDeleteView, self).delete(*args, **kwargs)


def get_data_commercial(id_commercial, ctx):


    cursor = connection.cursor()

    # Get negative and positive lessons
    cursor.execute(f"""
        SELECT * FROM public.lessons_commerciallesson
        WHERE commercial_id = {id_commercial}

        ORDER BY lessons_commerciallesson.id ASC
    """)

    neg_pos_lessons = cursor.fetchall()

    ctx['negative_lessons'] = [{'id':n_p[0], 'description':n_p[2], 'positive':n_p[3], 'general':n_p[1]}                                     
                                    for n_p in neg_pos_lessons if n_p[3] != True]

    ctx['positive_lessons'] = [{'id':n_p[0], 'description':n_p[2], 'positive':n_p[3], 'general':n_p[1]}                                    
                                    for n_p in neg_pos_lessons if n_p[3] == True]        


    # Get preventive lessons 
    cursor.execute(f"""
        SELECT lessons_preventiveactions.id, lessons_preventiveactions.description FROM lessons_preventiveactions
        WHERE lessons_preventiveactions.commercial_id = {id_commercial}

        ORDER BY lessons_preventiveactions.id ASC
    """)

    preventive_actions = cursor.fetchall()
    ctx['preventive_actions'] = [{'id':p_a[0], 'description':p_a[1]} for p_a in preventive_actions]


    # Get commercial users
    cursor.execute(f"""
        SELECT auth_user.id, first_name, last_name FROM auth_user

        INNER JOIN lessons_commercialuser
        ON lessons_commercialuser.user_id = auth_user.id

        WHERE lessons_commercialuser.commercial_id = {id_commercial}
    """)

    ctx['comm_users'] = cursor.fetchall()
    ctx['select_comm_users'] = [row[0] for row in ctx['comm_users']]


    # Get relations between preventiveactions and with positive and negative lessons
    cursor.execute(f"""
        SELECT commercial_lesson_id, preventive_action_id FROM public.lessons_preventiveactionscommerciallesson

        INNER JOIN lessons_commerciallesson
        ON lessons_commerciallesson.id = lessons_preventiveactionscommerciallesson.commercial_lesson_id

        WHERE lessons_commerciallesson.commercial_id = {id_commercial}
    """)

    rel_prev_comm_les = cursor.fetchall()

    rel_prev_comm_les = [[rpcl[0], rpcl[1]] for rpcl in rel_prev_comm_les]

    tables_preventive = list()
    for prev in ctx['preventive_actions']:

        prev_id = prev['id']

        sub_table_neg = list()
        sub_table_pos = list()
        
        for dct_neg in ctx['negative_lessons']:

            lesson_id = dct_neg['id']
            # sub_table_neg.append([lesson_id, prev_id] in rel_prev_comm_les)
            sub_table_neg.append([lesson_id, [lesson_id, prev_id] in rel_prev_comm_les])


        for dct_pos in ctx['positive_lessons']:

            lesson_id = dct_pos['id']
            sub_table_pos.append([lesson_id, [lesson_id, prev_id] in rel_prev_comm_les])


        tables_preventive.append([sub_table_neg, sub_table_pos])

        prev['neg_sub_table'] = sub_table_neg
        prev['pos_sub_table'] = sub_table_pos

    ctx['tables_preventive'] = tables_preventive


    # Get related areas
    cursor.execute(f"""
        SELECT lessons_relatedarea.id, name FROM lessons_relatedarea

        INNER JOIN lessons_commercialrelatedarea
        ON lessons_commercialrelatedarea.related_area_id = lessons_relatedarea.id

        WHERE lessons_commercialrelatedarea.commercial_id = {id_commercial}
    """)

    ctx['related_areas'] = cursor.fetchall()
    ctx['select_related_areas'] = [row[0] for row in ctx['related_areas']]
  

    return ctx


def save_all_lessons(self):

        print()
        print()
        print(self.request.POST)

        # The form elements (Commercial model) are saved automaticaly, save the other elements
        #   Get the id from the last
        id_commercial = self.object.id


        # Create preventive lesson
        preventive_list = []
        for description in self.request.POST.getlist('preventive_table_desc[]'):
            p = PreventiveActions(
                    description=description,
                    commercial_id=id_commercial,
                )
            p.save()

            # print('p: ', p.id, description)

            preventive_list.append(p)


        # Create all commercial lessons, negatives/positives
        negative_list = []
        for negative_general, negative_detail in zip(self.request.POST.getlist('negative_table_general_desc[]'), 
                                                     self.request.POST.getlist('negative_table_detail_desc[]')):

            print('negative - - -')
            print(negative_general, negative_detail)            

            c = CommercialLesson(
                    general=negative_general,
                    description=negative_detail,
                    positive=False,
                    commercial_id=id_commercial,
                )

            c.save()

            negative_list.append(c)

        positive_list = []
        for positive_general, positive_detail in zip(self.request.POST.getlist('positive_table_general_desc[]'), 
                                                     self.request.POST.getlist('positive_table_detail_desc[]')):

            print('positive - - -')
            print(positive_general, positive_detail)                    

            c = CommercialLesson(
                    general=positive_general,
                    description=positive_detail,
                    positive=True,
                    commercial_id=id_commercial,
                )

            c.save()

            positive_list.append(c)

        # Add relations
        #   Between preventive actions and lessons negatives/positives
        # print('negative_list:', negative_list)
        # print('preventive_list:', preventive_list)
        for idx_preventive in range(len(self.request.POST.getlist('preventive_table_desc[]'))):
            for idx_neg in range(len(self.request.POST.getlist('negative_table_general_desc[]'))):
                #   negatives
                # print()
                # print(idx_preventive, idx_neg, f'prev_neg_{idx_preventive+1}_{idx_neg+1}_checkbox')
                # print(type(self.request.POST.get(f'prev_neg_{idx_preventive+1}_{idx_neg+1}_checkbox')))
                # print()
                if (self.request.POST.get(f'prev_neg_{idx_preventive+1}_{idx_neg+1}_checkbox') == 'True'):

                    # print('NEGATIVE', idx_neg)

                    PreventiveActionsCommercialLesson(
                        commercial_lesson_id=negative_list[idx_neg].id,
                        preventive_action_id=preventive_list[idx_preventive].id
                    ).save()

                    # pc.save()

            for idx_pos in range(len(self.request.POST.getlist('positive_table_general_desc[]'))):
                #   positives
                if (self.request.POST.get(f'prev_pos_{idx_preventive+1}_{idx_pos+1}_checkbox') == 'True'):

                    PreventiveActionsCommercialLesson(
                        commercial_lesson_id=positive_list[idx_pos].id,
                        preventive_action_id=preventive_list[idx_preventive].id
                    ).save()

                    # pc.save()


        # Save related areas
        for idx_relat_area in self.request.POST.getlist('related_areas_name[]'):

            cra = CommercialRelatedArea(
                    commercial_id=id_commercial, 
                    related_area_id=idx_relat_area
            )

            cra.save()

        # Save users 
        for idx_user in self.request.POST.getlist('users_name[]'):

            cu = CommercialUser(
                    commercial_id=id_commercial,
                    user_id=idx_user
            )

            cu.save()


def delete_all_lessons(id_commercial):

    # Delete first and after add again, this simplify all cases for add/update/delete
    # particular elements
    cursor = connection.cursor()

    #   Get list of ids elements to delete, we do this first for not violates foreign key constraint 
    #       Get lessons_commerciallesson
    cursor.execute(f"""
        SELECT lessons_commerciallesson.id FROM lessons_commerciallesson
        WHERE commercial_id = {id_commercial}
    """)

    ids_lessons_commerciallesson = [row[0] for row in cursor.fetchall()]


    #       Get lessons_preventiveactionscommerciallesson
    cursor.execute(f"""
        SELECT lessons_preventiveactionscommerciallesson.id 
        FROM lessons_preventiveactionscommerciallesson

        INNER JOIN lessons_commerciallesson
        ON lessons_commerciallesson.id = lessons_preventiveactionscommerciallesson.commercial_lesson_id

        WHERE lessons_commerciallesson.commercial_id = {id_commercial}
    """)

    ids_lessons_preventiveactionscommerciallesson = [row[0] for row in cursor.fetchall()]


    #       Get lessons_commerciallesson
    cursor.execute(f"""
        SELECT lessons_preventiveactions.id FROM lessons_preventiveactions
        WHERE commercial_id = {id_commercial}
    """)

    ids_lessons_preventiveactions = [row[0] for row in cursor.fetchall()]



    #   Delete lessons_preventiveactionscommerciallesson
    cursor.execute(f"""
        DELETE FROM lessons_preventiveactionscommerciallesson 
        WHERE lessons_preventiveactionscommerciallesson.id 
        IN ({str(ids_lessons_preventiveactionscommerciallesson)[1:-1]})
    """)

    #   Delete lessons_preventiveactions
    cursor.execute(f"""
        DELETE FROM lessons_preventiveactions 
        WHERE lessons_preventiveactions.id 
        IN ({str(ids_lessons_preventiveactions)[1:-1]})
    """)        

    #   Delete lessons_commerciallesson
    cursor.execute(f"""
        DELETE FROM lessons_commerciallesson 
        WHERE lessons_commerciallesson.id 
        IN ({str(ids_lessons_commerciallesson)[1:-1]})
    """)

    #   Delete users
    cursor.execute(f"""
        DELETE FROM lessons_commercialuser
        WHERE commercial_id = {id_commercial}
    """)    

    #   Delete related areas
    cursor.execute(f"""
        DELETE FROM lessons_commercialrelatedarea 
        WHERE commercial_id = {id_commercial}
    """)    

