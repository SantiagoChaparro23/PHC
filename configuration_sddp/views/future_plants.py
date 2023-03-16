from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from configuration_sddp.models import FuturePlants
from configuration_sddp.forms.future_plants_form import FuturePlantsForm


class FuturePlantsListView(PermissionRequiredMixin, ListView):

    model = FuturePlants
    template_name = 'future_plants/list.html'
    context_object_name = 'future_plants'
    permission_required = ''


class FuturePlantsCreateView(PermissionRequiredMixin, CreateView):

    model = FuturePlants
    form_class = FuturePlantsForm
    template_name = 'future_plants/create.html'
    success_url = reverse_lazy('configuration_sddp:future_plants_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro creado con éxito')
        return super().form_valid(form)


class FuturePlantsUpdateView(PermissionRequiredMixin, UpdateView):

    model = FuturePlants
    form_class = FuturePlantsForm
    template_name = 'future_plants/change.html'
    success_url = reverse_lazy('configuration_sddp:future_plants_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro actualizado con éxito')
        return super().form_valid(form)


class FuturePlantsDeleteView(PermissionRequiredMixin, DeleteView):

    model = FuturePlants
    template_name = 'future_plants/delete.html'
    success_url = reverse_lazy('configuration_sddp:future_plants_list')
    context_object_name = 'future_plants'
    permission_required = ''

    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Registro eliminado con éxito')
        return super().delete(*args, **kwargs)
