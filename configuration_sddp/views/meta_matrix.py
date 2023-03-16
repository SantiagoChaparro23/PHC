from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from configuration_sddp.models import MetaMatrix
from configuration_sddp.forms.meta_matrix_form import MetaMatrixForm


class MetaMatrixListView(PermissionRequiredMixin, ListView):

    model = MetaMatrix
    template_name = 'meta_matrix/list.html'
    context_object_name = 'meta_matrix'
    permission_required = ''


class MetaMatrixCreateView(PermissionRequiredMixin, CreateView):

    model = MetaMatrix
    form_class = MetaMatrixForm
    template_name = 'meta_matrix/create.html'
    success_url = reverse_lazy('configuration_sddp:meta_matrix_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro creado con éxito')
        return super().form_valid(form)


class MetaMatrixUpdateView(PermissionRequiredMixin, UpdateView):

    model = MetaMatrix
    form_class = MetaMatrixForm
    template_name = 'meta_matrix/change.html'
    success_url = reverse_lazy('configuration_sddp:meta_matrix_list')
    permission_required = ''

    def form_valid(self, form):
        messages.success(self.request, 'Registro actualizado con éxito')
        return super().form_valid(form)


class MetaMatrixDeleteView(PermissionRequiredMixin, DeleteView):

    model = MetaMatrix
    template_name = 'meta_matrix/delete.html'
    success_url = reverse_lazy('configuration_sddp:meta_matrix_list')
    context_object_name = 'meta_matrix'
    permission_required = ''

    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Registro eliminado con éxito')
        return super().delete(*args, **kwargs)
