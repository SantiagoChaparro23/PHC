from django.http import HttpResponse

from django.contrib.auth.models import User
import json

from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, DetailView, FormView, UpdateView, DeleteView
from django.http import JsonResponse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import connection

from lessons.old_forms import RelatedAreaForm
from lessons.models import RelatedArea


class RelatedAreaListView(PermissionRequiredMixin, ListView):

    model = RelatedArea
    template_name = 'related_area/list.html'
    context_object_name = 'related_area'

    ordering = ['-id']

    permission_required = 'lessons.view_commercialrelatedarea'


class RelatedAreaCreateView(PermissionRequiredMixin, CreateView):

    model = RelatedArea
    form_class = RelatedAreaForm
    template_name = 'related_area/create.html'
    success_url = reverse_lazy('lessons:related_area_list')

    permission_required = 'lessons.add_commercialrelatedarea'


class RelatedAreaChangeView(PermissionRequiredMixin, UpdateView):

    model = RelatedArea
    template_name = 'related_area/change.html'
    success_url = reverse_lazy('lessons:related_area_list')
    form_class = RelatedAreaForm

    permission_required = 'lessons.change_commercialrelatedarea'


class RelatedAreaDeleteView(PermissionRequiredMixin, DeleteView):

    model = RelatedArea
    template_name = 'related_area/delete.html'
    success_url = reverse_lazy('lessons:related_area_list')
    context_object_name = 'related_area'

    permission_required = 'lessons.delete_commercialrelatedarea'
