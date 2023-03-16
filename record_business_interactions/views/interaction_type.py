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

from record_business_interactions.forms import InteractionTypeForm
from record_business_interactions.models import InteractionType


class InteractionTypeListView(PermissionRequiredMixin, ListView):

    model = InteractionType
    template_name = 'interaction_type/list.html'
    context_object_name = 'interaction_type'

    ordering = ['-id']

    permission_required = 'record_business_interactions.view_interactiontype'


class InteractionTypeCreateView(PermissionRequiredMixin, CreateView):

    model = InteractionType
    form_class = InteractionTypeForm
    template_name = 'interaction_type/create.html'
    success_url = reverse_lazy('record_business_interactions:interaction_type_list')

    permission_required = 'record_business_interactions.add_interactiontype'


class InteractionTypeChangeView(PermissionRequiredMixin, UpdateView):

    model = InteractionType
    template_name = 'interaction_type/change.html'
    success_url = reverse_lazy('record_business_interactions:interaction_type_list')
    form_class = InteractionTypeForm

    permission_required = 'record_business_interactions.change_interactiontype'


class InteractionTypeDeleteView(PermissionRequiredMixin, DeleteView):

    model = InteractionType
    template_name = 'interaction_type/delete.html'
    success_url = reverse_lazy('record_business_interactions:interaction_type_list')
    context_object_name = 'interaction_type'

    permission_required = 'record_business_interactions.delete_interactiontype'

