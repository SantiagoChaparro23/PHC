from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from budgeted_hours.models import Operator

from budgeted_hours.forms.operator_form import OperatorForm

# Create your views here.
# @method_decorator(login_required, name='dispatch')
class OperatorListView(PermissionRequiredMixin, ListView):

    model = Operator
    template_name = 'operator/list.html'
    context_object_name = 'operators'
    permission_required = 'budgeted_hours.view_operator'


# @method_decorator(login_required, name='dispatch')
class OperatorCreateView(PermissionRequiredMixin, CreateView):

    model = Operator
    form_class = OperatorForm
    template_name = 'operator/create.html'
    success_url = reverse_lazy('budgeted_hours:operators_list')
    permission_required = 'budgeted_hours.add_operator'


    def form_valid(self, form):
        messages.success(self.request, 'Operador creado con éxito')
        return super().form_valid(form)


# @method_decorator(login_required, name='dispatch')
class OperatorUpdateView(PermissionRequiredMixin, UpdateView):

    model = Operator
    form_class = OperatorForm
    template_name = 'operator/detail.html'
    success_url = reverse_lazy('budgeted_hours:operators_list')
    permission_required = 'budgeted_hours.change_operator'


    def form_valid(self, form):
        obj = form.save(commit=False)
        messages.success(self.request, 'Operador actualizado con éxito')
        obj.save()

        return HttpResponseRedirect(self.get_success_url())


# @method_decorator(login_required, name='dispatch')
class OperatorDeleteView(PermissionRequiredMixin, DeleteView):

    model = Operator
    template_name = 'operator/delete.html'
    success_url = reverse_lazy('budgeted_hours:operators_list')
    context_object_name = 'operator'
    permission_required = 'budgeted_hours.delete_operator'


    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Operador eliminado con éxito')
        return super(OperatorDeleteView, self).delete(*args, **kwargs)
