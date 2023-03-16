from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from markers.models import Match
from markers.forms.match_form import MatchForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages


class MatchListView(PermissionRequiredMixin, ListView):


    model = Match
    template_name: str = 'match/list.html'
    context_object_name = 'match'
    permission_required = 'markers.view_match'
    


class MatchCreateView(PermissionRequiredMixin, CreateView):
    
    model = Match
    form_class = MatchForm
    template_name = 'match/create.html'
    success_url = reverse_lazy('markers:match_list')
    permission_required = 'markers.add_match'
    
    
    def form_valid ( self , form ) :
        messages.success ( self.request , ' Registro creado con éxito ' )
        return super ( ) . form_valid ( form )


class MatchUpdateView(PermissionRequiredMixin, UpdateView):
    
    model = Match 
    form_class = MatchForm
    template_name = 'match/change.html'
    success_url = reverse_lazy('markers:match_list')
    permission_required = 'markers.change_match'

    def form_valid ( self , form ) :
        messages.success ( self.request , ' Registro actualizado con éxito ' )
        return super ( ) . form_valid ( form )


    
class MatchDeleteView(PermissionRequiredMixin, DeleteView):
    
    model = Match
    template_name = 'match/delete.html'
    success_url = reverse_lazy('markers:match_list')
    context_object_name = 'match'
    permission_required = 'markers.delete_match'


    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Registro eliminado con éxito')
        return super().delete(*args, **kwargs)
    
class MatchDetailView(PermissionRequiredMixin, DetailView):
    
    model = Match
    template_name = 'match/detail.html'
    context_object_name = 'match'
    permission_required = 'markers.view_match'