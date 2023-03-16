from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from configuration_sddp.models import MaxNewCapacity
from configuration_sddp.forms.max_new_capacity_form import MaxNewCapacityForm


class MaxNewCapacityListView(PermissionRequiredMixin, ListView):

    model = MaxNewCapacity
    template_name = 'max_new_capacity/list.html'
    context_object_name = 'max_new_capacity'
    permission_required = ''


class MaxNewCapacityCreateView(PermissionRequiredMixin, CreateView):

    model = MaxNewCapacity
    form_class = MaxNewCapacityForm
    template_name = 'max_new_capacity/create.html'
    success_url = reverse_lazy('configuration_sddp:max_new_capacity_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro creado con éxito')
        return super().form_valid(form)


class MaxNewCapacityUpdateView(PermissionRequiredMixin, UpdateView):

    model = MaxNewCapacity
    form_class = MaxNewCapacityForm
    template_name = 'max_new_capacity/change.html'
    success_url = reverse_lazy('configuration_sddp:max_new_capacity_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro actualizado con éxito')
        return super().form_valid(form)


class MaxNewCapacityDeleteView(PermissionRequiredMixin, DeleteView):

    model = MaxNewCapacity
    template_name = 'max_new_capacity/delete.html'
    success_url = reverse_lazy('configuration_sddp:max_new_capacity_list')
    context_object_name = 'max_new_capacity'
    permission_required = ''

    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Registro eliminado con éxito')
        return super().delete(*args, **kwargs)
