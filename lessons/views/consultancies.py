from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from lessons.models import Consultancies
from lessons.forms.consultancies_form import ConsultanciesForm


# Create your views here.
class ConsultanciesListView(PermissionRequiredMixin, ListView):

    model = Consultancies
    template_name = 'consultancies/list.html'
    context_object_name = 'consultancies'
    permission_required = ''


class ConsultanciesCreateView(PermissionRequiredMixin, CreateView):

    model = Consultancies
    form_class = ConsultanciesForm
    template_name = 'consultancies/create.html'
    success_url = reverse_lazy('lessons:consultancies_list')
    permission_required = ''


    def form_valid(self, form):
        messages.success(self.request, 'Registro creado con éxito')
        return super().form_valid(form)


class ConsultanciesDetailView(PermissionRequiredMixin, DetailView):

    model = Consultancies
    template_name = 'consultancies/detail.html'
    context_object_name = 'consultancies'
    permission_required = ''


class ConsultanciesUpdateView(PermissionRequiredMixin, UpdateView):

    model = Consultancies
    form_class = ConsultanciesForm
    template_name = 'consultancies/change.html'
    success_url = reverse_lazy('lessons:consultancies_list')
    permission_required = ''


    def form_valid(self, form):
        obj = form.save(commit=False)
        messages.success(self.request, 'Registro actualizado con éxito')
        obj.save()

        return HttpResponseRedirect(self.get_success_url())


class ConsultanciesDeleteView(PermissionRequiredMixin, DeleteView):

    model = Consultancies
    template_name = 'consultancies/delete.html'
    success_url = reverse_lazy('lessons:consultancies_list')
    context_object_name = 'consultancies'
    permission_required = ''


    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Registro eliminado con éxito')
        return super().delete(*args, **kwargs)
