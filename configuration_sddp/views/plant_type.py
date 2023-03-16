from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from configuration_sddp.models import PlantType
from configuration_sddp.forms.plant_type_form import PlantTypeForm


class PlantTypeListView(PermissionRequiredMixin, ListView):

    model = PlantType
    template_name = 'plant_type/list.html'
    context_object_name = 'plant_type'
    permission_required = ''


class PlantTypeCreateView(PermissionRequiredMixin, CreateView):

    model = PlantType
    form_class = PlantTypeForm
    template_name = 'plant_type/create.html'
    success_url = reverse_lazy('configuration_sddp:plant_type_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro creado con éxito')
        return super().form_valid(form)


class PlantTypeUpdateView(PermissionRequiredMixin, UpdateView):

    model = PlantType
    form_class = PlantTypeForm
    template_name = 'plant_type/change.html'
    success_url = reverse_lazy('configuration_sddp:plant_type_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro actualizado con éxito')
        return super().form_valid(form)


class PlantTypeDeleteView(PermissionRequiredMixin, DeleteView):

    model = PlantType
    template_name = 'plant_type/delete.html'
    success_url = reverse_lazy('configuration_sddp:plant_type_list')
    context_object_name = 'plant_type'
    permission_required = ''

    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Registro eliminado con éxito')
        return super().delete(*args, **kwargs)
