from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http.response import HttpResponseRedirect

from vacations.models import DaysCaused

from vacations.forms.days_caused_form import DaysCausedForm

# Create your views here.
class DaysCausedListView(PermissionRequiredMixin, ListView):

    model = DaysCaused
    template_name = 'days_caused/list.html'
    context_object_name = 'days_caused'
    permission_required = 'vacations.view_days_caused'


class DaysCausedCreateView(PermissionRequiredMixin, CreateView):

    model = DaysCaused
    form_class = DaysCausedForm
    template_name = 'days_caused/create.html'
    success_url = reverse_lazy('vacations:days_caused_list')
    permission_required = 'vacations.add_days_caused'

    def form_valid(self, form):
        messages.success(self.request, 'Elemento de días causados creado con éxito')
        return super().form_valid(form)


class DaysCausedUpdateView(PermissionRequiredMixin, UpdateView):

    model = DaysCaused
    form_class = DaysCausedForm
    template_name = 'days_caused/change.html'
    success_url = reverse_lazy('vacations:days_caused_list')
    permission_required = 'vacations.change_days_caused'

    def form_valid(self, form):
        obj = form.save(commit=False)
        messages.success(self.request, 'Elemento de días causados actualizado con éxito')
        obj.save()

        return HttpResponseRedirect(self.get_success_url())


class DaysCausedDeleteView(PermissionRequiredMixin, DeleteView):

    model = DaysCaused
    template_name = 'days_caused/delete.html'
    success_url = reverse_lazy('vacations:days_caused_list')
    context_object_name = 'days_caused'
    permission_required = 'vacations.delete_days_caused'


    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Elemento de días causados eliminado con éxito')
        return super(DaysCausedDeleteView, self).delete(*args, **kwargs)
