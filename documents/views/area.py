from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from documents.models import Area
from documents.forms.area_form import AreaForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages


class AreaListView(PermissionRequiredMixin, ListView):
    
    model = Area
    template_name: str = 'area/list.html'
    context_object_name = 'area'
    permission_required = 'documents.view_area'
    
class AreaCreateView(PermissionRequiredMixin, CreateView):
    
    model = Area
    form_class = AreaForm
    template_name = 'area/create.html'
    success_url = reverse_lazy('documents:area_list')
    permission_required = 'documents.add_area'
    
    
    def form_valid ( self , form ) :
        messages.success ( self.request , ' Registro creado con éxito ' )
        return super ( ) . form_valid ( form )

class AreaUpdateView(PermissionRequiredMixin, UpdateView):
    
    model = Area 
    form_class = AreaForm
    template_name = 'area/change.html'
    success_url = reverse_lazy('documents:area_list')
    permission_required = 'documents.change_area'

    def form_valid ( self , form ) :
        messages.success ( self.request , ' Registro actualizado con éxito ' )
        return super ( ) . form_valid ( form )
    
    
class AreaDeleteView(PermissionRequiredMixin, DeleteView):
    
    model = Area
    template_name = 'area/delete.html'
    success_url = reverse_lazy('documents:area_list')
    context_object_name = 'area'
    permission_required = 'documents.delete_area'


    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Registro eliminado con éxito')
        return super().delete(*args, **kwargs)
    

            
              