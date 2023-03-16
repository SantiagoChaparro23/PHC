from django.views.generic import ListView, CreateView, DetailView, FormView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from sddp.forms import ProjectsForm, DbsForm
from lessons.old_forms import MarketStudiesForm
# Create your views here.
from sddp.models import Project, Db, MarginalCostDemand
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.http.response import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import redirect, reverse
from django.db import connection

class DbsListView(PermissionRequiredMixin, ListView):
    model = Db
    template_name = 'dbs/list.html'
    context_object_name = 'dbs'
    permission_required = 'sddp.view_db'
    queryset = Db.objects.prefetch_related('project', 'created_by').all()

    

  

class DbsCreateView(PermissionRequiredMixin, CreateView):

    model = Db
    form_class = DbsForm
    template_name =  'dbs/create.html'
    success_url = reverse_lazy('sddp:dbs_list')
    permission_required = 'sddp.add_db'


    def get_context_data(self, **kwargs):
        ctx = super(DbsCreateView, self).get_context_data(**kwargs)
        return ctx

    


    def form_valid(self, form):
       
        obj = form.save(commit=False)
        obj.created_by = self.request.user
   
        messages.success(self.request, 'Base de datos agregada con exito') 
        obj.save()
        form.process_cmgdem(obj)
        if obj.genpltproy_file:
            form.process_genpltproy(obj)
   
        return super().form_valid(form)




class DbsDeleteView(DeleteView):
    model = Db
    template_name = 'dbs/delete.html'
    success_url = reverse_lazy('sddp:dbs_list')
    context_object_name = 'db'
    queryset = Db.objects.prefetch_related('project', 'created_by').all()
    permission_required = 'sddp.delete_db'

    def get_context_data(self, **kwargs):
        object= self.get_object()
        count = MarginalCostDemand.objects.filter(db_id=object.pk).count()
        
        ctx = super(DbsDeleteView, self).get_context_data(**kwargs)
        ctx['count'] = count
        return ctx

    
    def delete(self, *args, **kwargs):
        
        object= self.get_object()
        user = self.request.user
        
        if((user.id is object.created_by.id) or user.has_perm('sddp.delete_dbs')):

            messages.success(self.request, 'Base de datos eliminada con exito') 
            return super(DbsDeleteView, self).delete(*args, **kwargs)
        
        else:
            messages.error(self.request, 'No puedes eliminar esta base de datos') 
            return HttpResponseRedirect(reverse_lazy('sddp:dbs_list'))
        