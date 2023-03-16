from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from configuration_sddp.models import Demand
from configuration_sddp.forms.demand_form import DemandForm


class DemandListView(PermissionRequiredMixin, ListView):

    model = Demand
    template_name = 'demand/list.html'
    context_object_name = 'demand'
    permission_required = ''


class DemandCreateView(PermissionRequiredMixin, CreateView):

    model = Demand
    form_class = DemandForm
    template_name = 'demand/create.html'
    success_url = reverse_lazy('configuration_sddp:demand_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro creado con éxito')
        return super().form_valid(form)


class DemandUpdateView(PermissionRequiredMixin, UpdateView):

    model = Demand
    form_class = DemandForm
    template_name = 'demand/change.html'
    success_url = reverse_lazy('configuration_sddp:demand_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro actualizado con éxito')
        return super().form_valid(form)


class DemandDeleteView(PermissionRequiredMixin, DeleteView):

    model = Demand
    template_name = 'demand/delete.html'
    success_url = reverse_lazy('configuration_sddp:demand_list')
    context_object_name = 'demand'
    permission_required = ''

    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Registro eliminado con éxito')
        return super().delete(*args, **kwargs)
