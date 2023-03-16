from datetime import datetime, timezone, timedelta

from django.http import HttpResponse

from django.contrib.auth.models import User
import json

from django.core.exceptions import ValidationError
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, DetailView, FormView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import connection
from django.core.paginator import Paginator


from configuration_sddp.models import Project
from configuration_sddp.old_forms import ProjectsForm



class ProjectListView(PermissionRequiredMixin, ListView):

    model = Project
    template_name = 'project/list.html'
    context_object_name = 'projects'
    permission_required = 'configuration_sddp.view_project'

    ordering = ['name']

    paginate_by = 20


class ProjectCreateView(PermissionRequiredMixin, CreateView):

    model = Project
    form_class = ProjectsForm
    template_name =  'project/create.html'
    success_url = reverse_lazy('configuration_sddp:project_list')
    permission_required = 'configuration_sddp.add_project'


    def form_valid(self, form):

        obj = form.save(commit=False)
        obj.created_by = self.request.user

        messages.success(self.request, 'Proyecto agregado con exito')
        obj.save()
        form.process(obj)

        return super().form_valid(form)
