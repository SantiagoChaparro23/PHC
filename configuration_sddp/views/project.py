from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from configuration_sddp.models import Project
from configuration_sddp.forms.project_form import ProjectForm

from datetime import datetime


class ProjectListView(PermissionRequiredMixin, ListView):

    model = Project
    template_name = 'project/list.html'
    context_object_name = 'project'
    permission_required = ''


class ProjectCreateView(PermissionRequiredMixin, CreateView):

    model = Project
    form_class = ProjectForm
    template_name = 'project/create.html'
    success_url = reverse_lazy('configuration_sddp:project_list')
    permission_required = ''

    def form_valid(self, form):

        obj = form.save(commit=False)

        unix = int(datetime.now().timestamp())
        obj.file.name = f'{unix}_{obj.file.name}'
        obj.save()

        message = form.processExcel(obj)
        messages.error(self.request, message) if message else messages.success(self.request, 'Datos importados con éxito')

        messages.success(self.request, 'Registro creado con éxito')
        return super().form_valid(form)


class ProjectUpdateView(PermissionRequiredMixin, UpdateView):

    model = Project
    form_class = ProjectForm
    template_name = 'project/change.html'
    success_url = reverse_lazy('configuration_sddp:project_list')
    permission_required = ''

    def form_valid(self, form):

        obj = form.save(commit=False)

        if self.request.FILES:
            unix = int(datetime.now().timestamp())
            obj.file.name = f'{unix}_{obj.file.name}'
            obj.save()

            message = form.processExcel(obj)
            messages.error(self.request, message) if message else messages.success(self.request, 'Datos importados con éxito')

        messages.success(self.request, 'Registro actualizado con éxito')
        return super().form_valid(form)


class ProjectDeleteView(PermissionRequiredMixin, DeleteView):

    model = Project
    template_name = 'project/delete.html'
    success_url = reverse_lazy('configuration_sddp:project_list')
    context_object_name = 'project'
    permission_required = ''

    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Registro eliminado con éxito')
        return super().delete(*args, **kwargs)
