from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from configuration_sddp.models import GraphYear
from configuration_sddp.forms.graph_year_form import GraphYearForm


class GraphYearListView(PermissionRequiredMixin, ListView):

    model = GraphYear
    template_name = 'graph_year/list.html'
    context_object_name = 'graph_year'
    permission_required = ''


class GraphYearCreateView(PermissionRequiredMixin, CreateView):

    model = GraphYear
    form_class = GraphYearForm
    template_name = 'graph_year/create.html'
    success_url = reverse_lazy('configuration_sddp:graph_year_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro creado con éxito')
        return super().form_valid(form)


class GraphYearUpdateView(PermissionRequiredMixin, UpdateView):

    model = GraphYear
    form_class = GraphYearForm
    template_name = 'graph_year/change.html'
    success_url = reverse_lazy('configuration_sddp:graph_year_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro actualizado con éxito')
        return super().form_valid(form)


class GraphYearDeleteView(PermissionRequiredMixin, DeleteView):

    model = GraphYear
    template_name = 'graph_year/delete.html'
    success_url = reverse_lazy('configuration_sddp:graph_year_list')
    context_object_name = 'graph_year'
    permission_required = ''

    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Registro eliminado con éxito')
        return super().delete(*args, **kwargs)
