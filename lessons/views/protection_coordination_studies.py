from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from lessons.models import ProtectionCoordinationStudies
from lessons.forms.protection_coordination_studies_form import ProtectionCoordinationStudiesForm


# Create your views here.
class ProtectionCoordinationStudiesListView(PermissionRequiredMixin, ListView):

    model = ProtectionCoordinationStudies
    template_name = 'protection_coordination_studies/list.html'
    context_object_name = 'protection_coordination_studies'
    permission_required = ''


class ProtectionCoordinationStudiesCreateView(PermissionRequiredMixin, CreateView):

    model = ProtectionCoordinationStudies
    form_class = ProtectionCoordinationStudiesForm
    template_name = 'protection_coordination_studies/create.html'
    success_url = reverse_lazy('lessons:protection_coordination_studies_list')
    permission_required = ''


    def form_valid(self, form):
        messages.success(self.request, 'Registro creado con éxito')
        return super().form_valid(form)


class ProtectionCoordinationStudiesDetailView(PermissionRequiredMixin, DetailView):

    model = ProtectionCoordinationStudies
    template_name = 'protection_coordination_studies/detail.html'
    context_object_name = 'protection_coordination_studies'
    permission_required = ''


class ProtectionCoordinationStudiesUpdateView(PermissionRequiredMixin, UpdateView):

    model = ProtectionCoordinationStudies
    form_class = ProtectionCoordinationStudiesForm
    template_name = 'protection_coordination_studies/change.html'
    success_url = reverse_lazy('lessons:protection_coordination_studies_list')
    permission_required = ''


    def form_valid(self, form):
        obj = form.save(commit=False)
        messages.success(self.request, 'Registro actualizado con éxito')
        obj.save()

        return HttpResponseRedirect(self.get_success_url())


class ProtectionCoordinationStudiesDeleteView(PermissionRequiredMixin, DeleteView):

    model = ProtectionCoordinationStudies
    template_name = 'protection_coordination_studies/delete.html'
    success_url = reverse_lazy('lessons:protection_coordination_studies_list')
    context_object_name = 'protection_coordination_studies'
    permission_required = ''


    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Registro eliminado con éxito')
        return super().delete(*args, **kwargs)
