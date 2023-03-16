from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from configuration_sddp.models import Fuel
from configuration_sddp.forms.fuel_form import FuelForm


class FuelListView(PermissionRequiredMixin, ListView):

    model = Fuel
    template_name = 'fuel/list.html'
    context_object_name = 'fuel'
    permission_required = ''


class FuelCreateView(PermissionRequiredMixin, CreateView):

    model = Fuel
    form_class = FuelForm
    template_name = 'fuel/create.html'
    success_url = reverse_lazy('configuration_sddp:fuel_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro creado con éxito')
        return super().form_valid(form)


class FuelUpdateView(PermissionRequiredMixin, UpdateView):

    model = Fuel
    form_class = FuelForm
    template_name = 'fuel/change.html'
    success_url = reverse_lazy('configuration_sddp:fuel_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro actualizado con éxito')
        return super().form_valid(form)


class FuelDeleteView(PermissionRequiredMixin, DeleteView):

    model = Fuel
    template_name = 'fuel/delete.html'
    success_url = reverse_lazy('configuration_sddp:fuel_list')
    context_object_name = 'fuel'
    permission_required = ''

    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Registro eliminado con éxito')
        return super().delete(*args, **kwargs)
