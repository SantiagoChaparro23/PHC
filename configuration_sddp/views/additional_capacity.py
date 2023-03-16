from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from configuration_sddp.models import AdditionalCapacity
from configuration_sddp.forms.additional_capacity_form import AdditionalCapacityForm


class AdditionalCapacityListView(PermissionRequiredMixin, ListView):

    model = AdditionalCapacity
    template_name = 'additional_capacity/list.html'
    context_object_name = 'additional_capacity'
    permission_required = ''


class AdditionalCapacityCreateView(PermissionRequiredMixin, CreateView):

    model = AdditionalCapacity
    form_class = AdditionalCapacityForm
    template_name = 'additional_capacity/create.html'
    success_url = reverse_lazy('configuration_sddp:additional_capacity_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro creado con éxito')
        return super().form_valid(form)


class AdditionalCapacityUpdateView(PermissionRequiredMixin, UpdateView):

    model = AdditionalCapacity
    form_class = AdditionalCapacityForm
    template_name = 'additional_capacity/change.html'
    success_url = reverse_lazy('configuration_sddp:additional_capacity_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro actualizado con éxito')
        return super().form_valid(form)


class AdditionalCapacityDeleteView(PermissionRequiredMixin, DeleteView):

    model = AdditionalCapacity
    template_name = 'additional_capacity/delete.html'
    success_url = reverse_lazy('configuration_sddp:additional_capacity_list')
    context_object_name = 'additional_capacity'
    permission_required = ''

    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Registro eliminado con éxito')
        return super().delete(*args, **kwargs)
