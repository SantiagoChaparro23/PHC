from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from documents.models import Templates
from documents.forms.templates_form import TemplatesForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages

# Create your views here.
class DocumentsListView(PermissionRequiredMixin, ListView):
    
    model = Templates
    template_name: str = 'documents/list.html'
    context_object_name = 'documents'
    permission_required = 'documents.view_templates'
    
class DocumentsCreateView(PermissionRequiredMixin, CreateView):
    
    model = Templates
    form_class = TemplatesForm
    template_name = 'documents/create.html'
    success_url = reverse_lazy('documents:documents_list')
    permission_required = 'documents.add_templates'
    
    
    def form_valid ( self , form ) :
        messages.success ( self.request , ' Registro creado con éxito ' )
        return super ( ) . form_valid ( form )

class DocumentsUpdateView(PermissionRequiredMixin,UpdateView):
    
    model = Templates 
    form_class = TemplatesForm
    template_name = 'documents/change.html'
    success_url = reverse_lazy('documents:documents_list')
    permission_required = 'documents.change_templates'

    def form_valid ( self , form ) :
        messages.success ( self.request , ' Registro actualizado con éxito ' )
        return super ( ) . form_valid ( form )
    
    
class DocumentsDeleteView(PermissionRequiredMixin, DeleteView):
    
    model = Templates
    template_name = 'documents/delete.html'
    success_url = reverse_lazy('documents:documents_list')
    context_object_name = 'documents'
    permission_required = 'documents.delete_templates'


    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Registro eliminado con éxito')
        return super().delete(*args, **kwargs)
    

class DocumentsDetailView(PermissionRequiredMixin, DetailView):
    
    model = Templates
    template_name = 'documents/detail.html'
    context_object_name = 'documents'
    permission_required = 'documents.view_templates'
    