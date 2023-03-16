from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from budgeted_hours.models import Categories

from budgeted_hours.forms.categories_form import CategoriesForm

# Create your views here.
# @method_decorator(login_required, name='dispatch')
class CategoriesListView(PermissionRequiredMixin, ListView):

    model = Categories
    template_name = 'categories/list.html'
    context_object_name = 'categories'
    permission_required = 'budgeted_hours.view_categories'


# @method_decorator(login_required, name='dispatch')
class CategoriesCreateView(PermissionRequiredMixin, CreateView):

    model = Categories
    form_class = CategoriesForm
    template_name = 'categories/create.html'
    success_url = reverse_lazy('budgeted_hours:categories_list')
    permission_required = 'budgeted_hours.add_categories'


    def form_valid(self, form):
        messages.success(self.request, 'Alcance creado con éxito')
        return super().form_valid(form)


# @method_decorator(login_required, name='dispatch')
class CategoriesUpdateView(PermissionRequiredMixin, UpdateView):

    model = Categories
    form_class = CategoriesForm
    template_name = 'categories/detail.html'
    success_url = reverse_lazy('budgeted_hours:categories_list')
    permission_required = 'budgeted_hours.change_categories'


    def form_valid(self, form):
        obj = form.save(commit=False)
        messages.success(self.request, 'Alcance actualizado con éxito')
        obj.save()

        return HttpResponseRedirect(self.get_success_url())


# @method_decorator(login_required, name='dispatch')
# class CategoriesDeleteView(DeleteView):

#     model = Categories
#     template_name = 'categories/delete.html'
#     success_url = reverse_lazy('budgeted_hours:categories_list')
#     context_object_name = 'categories'


#     def delete(self, *args, **kwargs):
#         messages.success(self.request, 'Alcance eliminado con éxito')
#         return super(CategoriesDeleteView, self).delete(*args, **kwargs)
