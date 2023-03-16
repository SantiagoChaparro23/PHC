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

from record_business_interactions.forms import VisitRecordForm, VisitRecordValidateForm
from record_business_interactions.models import VisitRecord, InteractionType, Settings
from budgeted_hours.models import Client


class VisitRecordListView(PermissionRequiredMixin, ListView):

    model = VisitRecord
    template_name = 'visit_record/list.html'
    context_object_name = 'visit_record'
    permission_required = 'record_business_interactions.view_visitrecord'

    queryset = VisitRecord.objects.prefetch_related('user', 'client', 'interaction_type').all()

    ordering = ['-id']

    paginate_by = 20



class VisitRecordDetailView(PermissionRequiredMixin, DetailView):
    model = VisitRecord
    template_name = 'visit_record/detail.html'
    context_object_name = 'visit_record'
    permission_required = 'record_business_interactions.view_visitrecord'


class VisitRecordCreateView(PermissionRequiredMixin, CreateView):

    model = VisitRecord
    form_class = VisitRecordForm
    template_name =  'visit_record/create.html'
    success_url = reverse_lazy('record_business_interactions:visit_record_list')
    queryset = VisitRecord.objects.prefetch_related('user', 'client','interaction_type').all()
    permission_required = 'record_business_interactions.add_visitrecord'

    def get_context_data(self, **kwargs):
        ctx = super(VisitRecordCreateView, self).get_context_data(**kwargs)

        ctx['form'].fields["interaction_type"].label_from_instance = lambda obj: "%s" % (obj.name)
        ctx['form'].fields['user'].label_from_instance = lambda obj: "%s %s" % (obj.first_name, obj.last_name)       

        return ctx

    def get_initial(self):
        initial = super(VisitRecordCreateView, self).get_initial()
        initial['date_record'] = datetime.now()
        return initial

    def form_valid(self, form):
        """
            We do machete here, django datetimes ever use timezone, we dont need save this
            in utc so we apply a offset
        """

        # raise ValidationError(_('Invalid value'))

        print('validation . . . .')

        obj = form.save(commit=False)

        # Set timezone with Colombia offset, we add two times this offset because in save moment
        # postgres quit the offset, but we add for comparison purpose in clean method from form
        datetime_record = datetime.now().replace(tzinfo=timezone(timedelta(hours=-5))) - timedelta(hours=10)

        obj.date_record = datetime_record
        
        return super().form_valid(form)
        # return 'not valid'


class VisitRecordChangeView(PermissionRequiredMixin, UpdateView):
    model = VisitRecord
    template_name = 'visit_record/change.html'
    success_url = reverse_lazy('record_business_interactions:visit_record_list')
    form_class = VisitRecordForm
    permission_required = 'record_business_interactions.change_visitrecord'

    def get_context_data(self, **kwargs):
        ctx = super(VisitRecordChangeView, self).get_context_data(**kwargs)

        ctx['form'].fields["interaction_type"].label_from_instance = lambda obj: "%s" % (obj.name)
        ctx['form'].fields['user'].label_from_instance = lambda obj: "%s %s" % (obj.first_name, obj.last_name)

        return ctx


class VisitRecordValidateView(PermissionRequiredMixin, UpdateView):
    model = VisitRecord
    template_name = 'visit_record/validate.html'
    success_url = reverse_lazy('record_business_interactions:visit_record_list')
    form_class = VisitRecordValidateForm
    permission_required = 'record_business_interactions.change_visitrecord_validate'

    def get_context_data(self, **kwargs):
        ctx = super(VisitRecordValidateView, self).get_context_data(**kwargs)

        ctx['form'].fields["interaction_type"].label_from_instance = lambda obj: "%s" % (obj.name)
        ctx['form'].fields['user'].label_from_instance = lambda obj: "%s %s" % (obj.first_name, obj.last_name)

        return ctx


class VisitRecordDeleteView(PermissionRequiredMixin, DeleteView):
    model = VisitRecord
    template_name = 'visit_record/delete.html'
    success_url = reverse_lazy('record_business_interactions:visit_record_list')
    context_object_name = 'visit_record'
    permission_required = 'record_business_interactions.delete_visitrecord'
    queryset = VisitRecord.objects.prefetch_related('user', 'client','interaction_type').all()

    def get_context_data(self, **kwargs):
        ctx = super(VisitRecordDeleteView, self).get_context_data(**kwargs)

        ctx['interaction_type'] = self.object.interaction_type.name
        ctx['user'] = f"{self.object.user.first_name} {self.object.user.last_name}"

        return ctx    

