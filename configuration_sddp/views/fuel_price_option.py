from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from configuration_sddp.models import FuelPriceOption
from configuration_sddp.forms.fuel_price_option_form import FuelPriceOptionForm


class FuelPriceOptionListView(PermissionRequiredMixin, ListView):

    model = FuelPriceOption
    template_name = 'fuel_price_option/list.html'
    context_object_name = 'fuelpriceoption'
    permission_required = ''


class FuelPriceOptionCreateView(PermissionRequiredMixin, CreateView):

    model = FuelPriceOption
    form_class = FuelPriceOptionForm
    template_name = 'fuel_price_option/create.html'
    success_url = reverse_lazy('configuration_sddp:fuel_price_option_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro creado con éxito')
        return super().form_valid(form)


class FuelPriceOptionUpdateView(PermissionRequiredMixin, UpdateView):

    model = FuelPriceOption
    form_class = FuelPriceOptionForm
    template_name = 'fuel_price_option/change.html'
    success_url = reverse_lazy('configuration_sddp:fuel_price_option_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro actualizado con éxito')
        return super().form_valid(form)


class FuelPriceOptionDeleteView(PermissionRequiredMixin, DeleteView):

    model = FuelPriceOption
    template_name = 'fuel_price_option/delete.html'
    success_url = reverse_lazy('configuration_sddp:fuel_price_option_list')
    context_object_name = 'fuelpriceoption'
    permission_required = ''

    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Registro eliminado con éxito')
        return super().delete(*args, **kwargs)
