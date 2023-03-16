from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from markers.models import Team
from markers.forms.team_form import TeamForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages


class TeamListView(PermissionRequiredMixin, ListView):


    model = Team
    template_name: str = 'team/list.html'
    context_object_name = 'team'
    permission_required = 'markers.view_team'
    


class TeamCreateView(PermissionRequiredMixin, CreateView):
    
    model = Team
    form_class = TeamForm
    template_name = 'team/create.html'
    success_url = reverse_lazy('markers:team_list')
    permission_required = 'markers.add_team'
    
    
    def form_valid ( self , form ) :
        messages.success ( self.request , ' Registro creado con éxito ' )
        return super ( ) . form_valid ( form )


class TeamUpdateView(PermissionRequiredMixin, UpdateView):
    
    model = Team 
    form_class = TeamForm
    template_name = 'team/change.html'
    success_url = reverse_lazy('markers:team_list')
    permission_required = 'markers.change_team'

    def form_valid ( self , form ) :
        messages.success ( self.request , ' Registro actualizado con éxito ' )
        return super ( ) . form_valid ( form )


    
class TeamDeleteView(PermissionRequiredMixin, DeleteView):
    
    model = Team
    template_name = 'team/delete.html'
    success_url = reverse_lazy('markers:team_list')
    context_object_name = 'team'
    permission_required = 'markers.delete_team'


    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Registro eliminado con éxito')
        return super().delete(*args, **kwargs)
    

class TeamDetailView(PermissionRequiredMixin, DetailView):
    
    model = Team
    template_name = 'team/detail.html'
    context_object_name = 'team'
    permission_required = 'markers.view_team'