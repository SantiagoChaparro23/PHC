from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from lessons.models import ElectricalStudies
from lessons.forms.electrical_studies_form import ElectricalStudiesForm
from django.db.models import Q


# Create your views here.
class ElectricalStudiesListView(PermissionRequiredMixin, ListView):

    model = ElectricalStudies
    template_name = 'electrical_studies/list.html'
    context_object_name = 'electrical_studies'
    permission_required = ''

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)

    #     query = self.request.GET.get('q','')

    #     if query:
    #         electrical_studies = ElectricalStudies.objects.filter(
    #             Q(client__client__icontains = query) |
    #             Q(budgeted_hours__code__icontains = query)
    #         ).all()

    #         context['electrical_studies'] = electrical_studies

    #     return context


class ElectricalStudiesCreateView(PermissionRequiredMixin, CreateView):

    model = ElectricalStudies
    form_class = ElectricalStudiesForm
    template_name = 'electrical_studies/create.html'
    success_url = reverse_lazy('lessons:electrical_studies_list')
    permission_required = ''


    def form_valid(self, form):
        messages.success(self.request, 'Registro creado con éxito')
        return super().form_valid(form)


class ElectricalStudiesDetailView(PermissionRequiredMixin, DetailView):

    model = ElectricalStudies
    template_name = 'electrical_studies/detail.html'
    context_object_name = 'electrical_studies'
    permission_required = ''


class ElectricalStudiesUpdateView(PermissionRequiredMixin, UpdateView):

    model = ElectricalStudies
    form_class = ElectricalStudiesForm
    template_name = 'electrical_studies/change.html'
    success_url = reverse_lazy('lessons:electrical_studies_list')
    permission_required = ''


    def form_valid(self, form):
        obj = form.save(commit=False)
        messages.success(self.request, 'Registro actualizado con éxito')
        obj.save()

        return HttpResponseRedirect(self.get_success_url())


class ElectricalStudiesDeleteView(PermissionRequiredMixin, DeleteView):

    model = ElectricalStudies
    template_name = 'electrical_studies/delete.html'
    success_url = reverse_lazy('lessons:electrical_studies_list')
    context_object_name = 'electrical_studies'
    permission_required = ''


    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Registro eliminado con éxito')
        return super().delete(*args, **kwargs)
