from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http.response import HttpResponseRedirect

from vacations.models import Bonus

from vacations.forms.bonus_form import BonusForm

# Create your views here.
class BonusListView(PermissionRequiredMixin, ListView):

    model = Bonus
    template_name = 'bonus/list.html'
    context_object_name = 'bonus'
    permission_required = 'vacations.view_bonus'


class BonusCreateView(PermissionRequiredMixin, CreateView):

    model = Bonus
    form_class = BonusForm
    template_name = 'bonus/create.html'
    success_url = reverse_lazy('vacations:bonus_list')
    permission_required = 'vacations.add_bonus'

    def form_valid(self, form):
        messages.success(self.request, 'Bono creado con éxito')
        return super().form_valid(form)


class BonusUpdateView(PermissionRequiredMixin, UpdateView):

    model = Bonus
    form_class = BonusForm
    template_name = 'bonus/change.html'
    success_url = reverse_lazy('vacations:bonus_list')
    permission_required = 'vacations.change_bonus'

    def form_valid(self, form):
        obj = form.save(commit=False)
        messages.success(self.request, 'Bono actualizado con éxito')
        obj.save()

        return HttpResponseRedirect(self.get_success_url())


class BonusDeleteView(PermissionRequiredMixin, DeleteView):

    model = Bonus
    template_name = 'bonus/delete.html'
    success_url = reverse_lazy('vacations:bonus_list')
    context_object_name = 'bonus'
    permission_required = 'vacations.delete_bonus'


    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Bono eliminado con éxito')
        return super(BonusDeleteView, self).delete(*args, **kwargs)
