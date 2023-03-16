from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from budgeted_hours.models import Softwares

from budgeted_hours.forms.software_form import SoftwaresForm

# Create your views here.
# @method_decorator(login_required, name='dispatch')
class SoftwaresListView(PermissionRequiredMixin, ListView):

    model = Softwares
    template_name = 'software/list.html'
    context_object_name = 'softwares'
    permission_required = 'budgeted_hours.view_softwares'


# @method_decorator(login_required, name='dispatch')
class SoftwaresCreateView(PermissionRequiredMixin, CreateView):

    model = Softwares
    form_class = SoftwaresForm
    template_name = 'software/create.html'
    success_url = reverse_lazy('budgeted_hours:softwares_list')
    permission_required = 'budgeted_hours.add_softwares'


    def form_valid(self, form):
        messages.success(self.request, 'Software creado con éxito')
        return super().form_valid(form)


# @method_decorator(login_required, name='dispatch')
class SoftwaresUpdateView(PermissionRequiredMixin, UpdateView):

    model = Softwares
    form_class = SoftwaresForm
    template_name = 'software/detail.html'
    success_url = reverse_lazy('budgeted_hours:softwares_list')
    permission_required = 'budgeted_hours.change_softwares'


    def form_valid(self, form):
        obj = form.save(commit=False)
        messages.success(self.request, 'Software actualizado con éxito')
        obj.save()

        return HttpResponseRedirect(self.get_success_url())


# @method_decorator(login_required, name='dispatch')
class SoftwaresDeleteView(PermissionRequiredMixin, DeleteView):

    model = Softwares
    template_name = 'software/delete.html'
    success_url = reverse_lazy('budgeted_hours:softwares_list')
    context_object_name = 'softwares'
    permission_required = 'budgeted_hours.delete_softwares'


    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Software eliminado con éxito')
        return super(SoftwaresDeleteView, self).delete(*args, **kwargs)
