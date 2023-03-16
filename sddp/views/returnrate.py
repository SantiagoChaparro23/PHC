from django.views.generic import ListView, CreateView, DetailView, FormView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from sddp.forms import ProjectsForm, ReturnRateForm
from lessons.old_forms import MarketStudiesForm
# Create your views here.
from sddp.models import Project, ReturnRate
from django.http import JsonResponse

# def index(request):
#     print(1234)



class ReturnRateListView(PermissionRequiredMixin, ListView):
    model = ReturnRate
    template_name = 'returnrate/list.html'
    context_object_name = 'rates'
    permission_required = 'sddp.view_returnrate'


class ReturnRateCreateView(PermissionRequiredMixin, CreateView):

    form_class = ReturnRateForm
    template_name =  'returnrate/create.html'
    success_url = reverse_lazy('sddp:returnrate_list')
    permission_required = 'sddp.add_returnrate'


    def form_valid(self, form):
        obj = form.save(commit=False)   
        messages.success(self.request, 'Tasa de retorno agregada con exito') 
        obj.save()
        return super().form_valid(form)


class ReturnRateChangeView(PermissionRequiredMixin, UpdateView):
    model = ReturnRate
    template_name = 'returnrate/change.html'
    success_url = reverse_lazy('sddp:returnrate_list')
    form_class = ReturnRateForm
    context_object_name = 'rate'
    permission_required = 'sddp.change_returnrate'

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Tasa de retorno actualizada con exito') 
        
        return super().form_valid(form)



class ReturnRateDeleteView(PermissionRequiredMixin, DeleteView):
    model = ReturnRate
    template_name = 'returnrate/delete.html'
    success_url = reverse_lazy('sddp:returnrate_list')
    context_object_name = 'rate'
    permission_required = 'sddp.delete_returnrate'

    
    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Tasa de retorno eliminado con exito') 
        return super(ReturnRateDeleteView, self).delete(*args, **kwargs)