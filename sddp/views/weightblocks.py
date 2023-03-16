from django.views.generic import ListView, CreateView, DetailView, FormView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from sddp.forms import WeightBlocksForm

# Create your views here.
from sddp.models import Project, WeightBlocks



class WeightBlocksListView(PermissionRequiredMixin, ListView):
    model = WeightBlocks
    template_name = 'weightblocks/list.html'
    context_object_name = 'weightblock'
    permission_required = 'sddp.view_weightblocks'


class WeightBlocksCreateView(PermissionRequiredMixin, CreateView):

    form_class = WeightBlocksForm
    template_name =  'weightblocks/create.html'
    success_url = reverse_lazy('sddp:weightblocks_list')
    permission_required = 'sddp.add_weightblocks'


    def form_valid(self, form):
        obj = form.save(commit=False)   
        messages.success(self.request, 'Peso bloque agregado con exito') 
        obj.save()
        return super().form_valid(form)


class WeightBlocksChangeView(PermissionRequiredMixin, UpdateView):
    model = WeightBlocks
    template_name = 'weightblocks/change.html'
    success_url = reverse_lazy('sddp:weightblocks_list')
    form_class = WeightBlocksForm
    context_object_name = 'weightblock'
    permission_required = 'sddp.change_weightblocks'

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Peso bloque actualizada con exito') 
        
        return super().form_valid(form)



class WeightBlocksDeleteView(PermissionRequiredMixin, DeleteView):
    model = WeightBlocks
    template_name = 'weightblocks/delete.html'
    success_url = reverse_lazy('sddp:weightblocks_list')
    context_object_name = 'weightblock'
    permission_required = 'sddp.delete_weightblocks'

    
    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Peso bloque eliminado con exito') 
        return super(WeightBlocksDeleteView, self).delete(*args, **kwargs)