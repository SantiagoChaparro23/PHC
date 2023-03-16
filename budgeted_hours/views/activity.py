from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from budgeted_hours.models import Activities, BudgetedHours, CategoriesVersions, TemplatesBudgetedHours, Categories, Hours, HoursTemplates
from django.db import connection

from budgeted_hours.forms.activity_form import ActivitiesForm

# Create your views here.
# @method_decorator(login_required, name='dispatch')
class ActivitiesListView(PermissionRequiredMixin, ListView):

    model = Activities
    template_name = 'activities/list.html'
    context_object_name = 'activities'
    permission_required = 'budgeted_hours.view_activities'


# @method_decorator(login_required, name='dispatch')
class ActivitiesCreateView(PermissionRequiredMixin, CreateView):

    model = Activities
    form_class = ActivitiesForm
    template_name = 'activities/create.html'
    permission_required = 'budgeted_hours.add_activities'


    def get_success_url(self):
        cursor = connection.cursor()
        cursor.execute('''
            SELECT
                budgeted_hours_id,
                category_id,
                category_version_id
            FROM
                budgeted_hours_hours AS bh
                INNER JOIN budgeted_hours_activities AS ba ON ba.id = bh.activity_id
            WHERE
                ba.service_type_id = {}
            GROUP BY
                budgeted_hours_id,
                category_id,
                category_version_id;
        '''.format(self.object.service_type.id))

        query_budgeted_hours = cursor.fetchall()
        print(query_budgeted_hours)
        print(type(query_budgeted_hours))

        if query_budgeted_hours:
            for i in query_budgeted_hours:
                # print('budgeted_hours_id', i[0], 'category_id', i[1])
                budgeted_hours = BudgetedHours.objects.get(pk=i[0])
                # activity = Activities.objects.get(pk=self.object.id)
                category = Categories.objects.get(pk=i[1])
                category_version = CategoriesVersions.objects.get(pk = i[2])

                instance = Hours(
                    budgeted_hours = budgeted_hours,
                    activity = self.object,
                    category = category,
                    category_version = category_version
                )
                instance.save()

        cursor.execute('''
            SELECT
                templates_budgeted_hours_id
            FROM
                budgeted_hours_hourstemplates AS bh
                INNER JOIN budgeted_hours_activities AS ba ON ba.id = bh.activity_id
            WHERE
                ba.service_type_id = {}
            GROUP BY
                templates_budgeted_hours_id;
        '''.format(self.object.service_type.id))

        query_templates_budgeted_hours = cursor.fetchall()

        if query_templates_budgeted_hours:
            for i in query_templates_budgeted_hours:
                # print('templates_budgeted_hours_id', i[0])
                templates_budgeted_hours = TemplatesBudgetedHours.objects.get(pk=i[0])
                # activity = Activities.objects.get(pk=self.object.id)

                instance = HoursTemplates(
                    templates_budgeted_hours = templates_budgeted_hours,
                    activity = self.object
                )
                instance.save()

        cursor.close()

        return reverse_lazy('budgeted_hours:activity_list')


    def form_valid(self, form):
        messages.success(self.request, 'Actividad creada con éxito')
        return super().form_valid(form)


# @method_decorator(login_required, name='dispatch')
class ActivitiesUpdateView(PermissionRequiredMixin, UpdateView):

    model = Activities
    form_class = ActivitiesForm
    template_name = 'activities/detail.html'
    success_url = reverse_lazy('budgeted_hours:activity_list')
    permission_required = 'budgeted_hours.change_activities'


    def form_valid(self, form):
        obj = form.save(commit=False)
        messages.success(self.request, 'Actividad actualizada con éxito')
        obj.save()

        return HttpResponseRedirect(self.get_success_url())


# @method_decorator(login_required, name='dispatch')
class ActivitiesDeleteView(PermissionRequiredMixin, DeleteView):

    model = Activities
    template_name = 'activities/delete.html'
    success_url = reverse_lazy('budgeted_hours:activity_list')
    context_object_name = 'activities'
    permission_required = 'budgeted_hours.delete_activities'


    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Actividad eliminada con éxito')
        return super(ActivitiesDeleteView, self).delete(*args, **kwargs)
