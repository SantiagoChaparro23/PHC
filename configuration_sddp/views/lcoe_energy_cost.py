from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from configuration_sddp.models import LcoeEnergyCost
from configuration_sddp.forms.lcoe_energy_cost_form import LcoeEnergyCostForm


class LcoeEnergyCostListView(PermissionRequiredMixin, ListView):

    model = LcoeEnergyCost
    template_name = 'lcoe_energy_cost/list.html'
    context_object_name = 'lcoe_energy_cost'
    permission_required = ''


class LcoeEnergyCostCreateView(PermissionRequiredMixin, CreateView):

    model = LcoeEnergyCost
    form_class = LcoeEnergyCostForm
    template_name = 'lcoe_energy_cost/create.html'
    success_url = reverse_lazy('configuration_sddp:lcoe_energy_cost_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro creado con éxito')
        return super().form_valid(form)


class LcoeEnergyCostUpdateView(PermissionRequiredMixin, UpdateView):

    model = LcoeEnergyCost
    form_class = LcoeEnergyCostForm
    template_name = 'lcoe_energy_cost/change.html'
    success_url = reverse_lazy('configuration_sddp:lcoe_energy_cost_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro actualizado con éxito')
        return super().form_valid(form)


class LcoeEnergyCostDeleteView(PermissionRequiredMixin, DeleteView):

    model = LcoeEnergyCost
    template_name = 'lcoe_energy_cost/delete.html'
    success_url = reverse_lazy('configuration_sddp:lcoe_energy_cost_list')
    context_object_name = 'lcoe_energy_cost'
    permission_required = ''

    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Registro eliminado con éxito')
        return super().delete(*args, **kwargs)
