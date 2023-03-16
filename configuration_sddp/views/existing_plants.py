from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from configuration_sddp.models import ExistingPlants
from configuration_sddp.forms.existing_plants_form import ExistingPlantsForm


class ExistingPlantsListView(PermissionRequiredMixin, ListView):

    model = ExistingPlants
    template_name = 'existing_plants/list.html'
    context_object_name = 'existing_plants'
    permission_required = ''


class ExistingPlantsCreateView(PermissionRequiredMixin, CreateView):

    model = ExistingPlants
    form_class = ExistingPlantsForm
    template_name = 'existing_plants/create.html'
    success_url = reverse_lazy('configuration_sddp:existing_plants_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro creado con éxito')
        return super().form_valid(form)


class ExistingPlantsUpdateView(PermissionRequiredMixin, UpdateView):

    model = ExistingPlants
    form_class = ExistingPlantsForm
    template_name = 'existing_plants/change.html'
    success_url = reverse_lazy('configuration_sddp:existing_plants_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro actualizado con éxito')
        return super().form_valid(form)


class ExistingPlantsDeleteView(PermissionRequiredMixin, DeleteView):

    model = ExistingPlants
    template_name = 'existing_plants/delete.html'
    success_url = reverse_lazy('configuration_sddp:existing_plants_list')
    context_object_name = 'existing_plants'
    permission_required = ''

    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Registro eliminado con éxito')
        return super().delete(*args, **kwargs)
