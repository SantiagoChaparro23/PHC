from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
# from django.utils.decorators import method_decorator
# from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import PermissionRequiredMixin

from budgeted_hours.models import TraceabilityBudgetedHours, TraceabilityBudgetedHoursHistory

# from budgeted_hours.forms.activity_form import ActivitiesForm

# Create your views here.
# @method_decorator(login_required, name='dispatch')
class TraceabilityBudgetedHoursListView(PermissionRequiredMixin, ListView):

    model = TraceabilityBudgetedHours
    template_name = 'traceability_budgeted_hours/list.html'
    context_object_name = 'traceabilitybudgetedhours'
    permission_required = 'budgeted_hours.view_traceabilitybudgetedhours'


# @method_decorator(login_required, name='dispatch')
class TraceabilityBudgetedHoursDetailView(PermissionRequiredMixin, DetailView):

    model = TraceabilityBudgetedHours
    template_name = 'traceability_budgeted_hours/detail.html'
    # context_object_name = 'traceabilitybudgetedhours'
    permission_required = 'budgeted_hours.view_traceabilitybudgetedhours'


    def get_context_data(self, **kwargs):
        context = super(TraceabilityBudgetedHoursDetailView, self).get_context_data(**kwargs)

        traceability_history = TraceabilityBudgetedHoursHistory.objects.filter(budgeted_hours = self.object.id)[:10]
        context['traceability_history'] = traceability_history

        return context


# @method_decorator(login_required, name='dispatch')
# class ActivitiesCreateView(CreateView):

#     model = Activities
#     form_class = ActivitiesForm
#     template_name = 'activities/create.html'
#     success_url = reverse_lazy('budgeted_hours:activity_list')


#     def form_valid(self, form):
#         messages.success(self.request, 'Actividad creada con exito')
#         return super().form_valid(form)


# @method_decorator(login_required, name='dispatch')
# class ActivitiesUpdateView(UpdateView):

#     model = Activities
#     form_class = ActivitiesForm
#     template_name = 'activities/detail.html'
#     success_url = reverse_lazy('budgeted_hours:activity_list')


#     def form_valid(self, form):
#         obj = form.save(commit=False)
#         messages.success(self.request, 'Actividad actualizada con exito')
#         obj.save()

#         return HttpResponseRedirect(self.get_success_url())


# @method_decorator(login_required, name='dispatch')
# class ActivitiesDeleteView(DeleteView):

#     model = Activities
#     template_name = 'activities/delete.html'
#     success_url = reverse_lazy('budgeted_hours:activity_list')
#     context_object_name = 'activities'


#     def delete(self, *args, **kwargs):
#         messages.success(self.request, 'Actividad eliminada con exito')
#         return super(ActivitiesDeleteView, self).delete(*args, **kwargs)
