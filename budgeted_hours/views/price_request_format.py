from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
# from django.utils.decorators import method_decorator
# from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from budgeted_hours.models import PriceRequestFormat, BudgetedHours

from budgeted_hours.forms.price_request_format_form import PriceRequestFormatForm

# Create your views here.
# @method_decorator(login_required, name='dispatch')
class PriceRequestFormatListView(PermissionRequiredMixin, ListView):

    model = PriceRequestFormat
    template_name = 'price_request_format/list.html'
    context_object_name = 'PriceRequestFormat'
    permission_required = 'budgeted_hours.view_pricerequestformat'


# @method_decorator(login_required, name='dispatch')
class PriceRequestFormatCreateView(PermissionRequiredMixin, CreateView):

    model = PriceRequestFormat
    form_class = PriceRequestFormatForm
    template_name = 'price_request_format/create.html'
    success_url = reverse_lazy('budgeted_hours:price_request_format_list')
    permission_required = 'budgeted_hours.add_pricerequestformat'


    def form_valid(self, form):
        messages.success(self.request, 'Formato solicitud de precio creado con éxito')
        return super().form_valid(form)


# @method_decorator(login_required, name='dispatch')
class PriceRequestFormatUpdateView(PermissionRequiredMixin, UpdateView):

    model = PriceRequestFormat
    form_class = PriceRequestFormatForm
    template_name = 'price_request_format/detail.html'
    success_url = reverse_lazy('budgeted_hours:price_request_format_list')
    permission_required = 'budgeted_hours.change_pricerequestformat'


    def get_context_data(self, **kwargs):
        context = super(PriceRequestFormatUpdateView, self).get_context_data(**kwargs)

        budgeted_hours = BudgetedHours.objects.filter(code = self.object.budgeted_hours).all()
        if budgeted_hours:
            budgeted_hours = BudgetedHours.objects.get(pk = budgeted_hours[0].id)
            context["budgeted_hours"] = budgeted_hours

        return context


    def form_valid(self, form):
        obj = form.save(commit=False)
        messages.success(self.request, 'Formato solicitud de precio actualizado con éxito')
        obj.save()

        return HttpResponseRedirect(self.get_success_url())


# @method_decorator(login_required, name='dispatch')
class PriceRequestFormatDeleteView(PermissionRequiredMixin, DeleteView):

    model = PriceRequestFormat
    template_name = 'price_request_format/delete.html'
    success_url = reverse_lazy('budgeted_hours:price_request_format_list')
    context_object_name = 'PriceRequestFormat'
    permission_required = 'budgeted_hours.delete_pricerequestformat'


    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Formato solicitud de precio eliminado con éxito')
        return super(PriceRequestFormatDeleteView, self).delete(*args, **kwargs)
