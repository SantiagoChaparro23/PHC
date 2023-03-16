from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from configuration_sddp.models import GrowingRate
from configuration_sddp.forms.growing_rate_form import GrowingRateForm


class GrowingRateListView(PermissionRequiredMixin, ListView):

    model = GrowingRate
    template_name = 'growing_rate/list.html'
    context_object_name = 'growingrate'
    permission_required = ''


class GrowingRateCreateView(PermissionRequiredMixin, CreateView):

    model = GrowingRate
    form_class = GrowingRateForm
    template_name = 'growing_rate/create.html'
    success_url = reverse_lazy('configuration_sddp:growing_rate_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro creado con éxito')
        return super().form_valid(form)


class GrowingRateUpdateView(PermissionRequiredMixin, UpdateView):

    model = GrowingRate
    form_class = GrowingRateForm
    template_name = 'growing_rate/change.html'
    success_url = reverse_lazy('configuration_sddp:growing_rate_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro actualizado con éxito')
        return super().form_valid(form)


class GrowingRateDeleteView(PermissionRequiredMixin, DeleteView):

    model = GrowingRate
    template_name = 'growing_rate/delete.html'
    success_url = reverse_lazy('configuration_sddp:growing_rate_list')
    context_object_name = 'growingrate'
    permission_required = ''

    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Registro eliminado con éxito')
        return super().delete(*args, **kwargs)
