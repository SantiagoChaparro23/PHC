from django.views.generic import ListView, CreateView, DetailView, FormView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from sddp.forms import ProjectsForm
from lessons.old_forms import MarketStudiesForm
from django.http.response import HttpResponseRedirect
# Create your views here.
from sddp.models import Project, Db
from django.http import JsonResponse

# def index(request):
#     print(1234)



class ProjectsListView(PermissionRequiredMixin, ListView):
    model = Project
    template_name = 'projects/list.html'
    context_object_name = 'projects'
    permission_required = 'sddp.view_project'

    queryset = Project.objects.all()


class ProjectCreateView(PermissionRequiredMixin, CreateView):

    model = Project
    form_class = ProjectsForm
    template_name =  'projects/create.html'
    success_url = reverse_lazy('sddp:projects_list')
    permission_required = 'sddp.add_project'


    def form_valid(self, form):
       
        obj = form.save(commit=False)
        obj.created_by = self.request.user
   
        messages.success(self.request, 'Proyecto agregado con exito') 
        obj.save()
        form.process(obj)
   
        return super().form_valid(form)




class ProjectDeleteView(DeleteView):
    model = Project
    template_name = 'projects/delete.html'
    success_url = reverse_lazy('sddp:projects_list')
    context_object_name = 'project'
    queryset = Project.objects.prefetch_related('created_by').all()
    permission_required = 'sddp.delete_project'

    def get_context_data(self, **kwargs):
        object= self.get_object()
        dbs = Db.objects.filter(project_id = object.pk).all()
     
        ctx = super(ProjectDeleteView, self).get_context_data(**kwargs)
        ctx['dbs'] = dbs
        return ctx

    
    def delete(self, *args, **kwargs):
        
        object= self.get_object()
        user = self.request.user
        
        if((user.id is object.created_by.id) or user.has_perm('sddp.delete_projects')):

            messages.success(self.request, 'Proyecto eliminada con exito') 
            return super(ProjectDeleteView, self).delete(*args, **kwargs)
        
        else:
            messages.error(self.request, 'No puedes eliminar este Proyecto') 
            return HttpResponseRedirect(reverse_lazy('sddp:projects_list'))

