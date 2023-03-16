from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.utils import translation
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.decorators import method_decorator

from django.views.generic import ListView, CreateView, DetailView, FormView, UpdateView, DeleteView
# from django.db import connection

from imports.models import Metric

from dashboard.forms.metric_form import MetricForm


def set_language(request):
    language = request.GET.get('lang', settings.LANGUAGE_CODE)
    translation.activate(language)
    return redirect('/')


@method_decorator(login_required, name='dispatch')
class MetricListView(ListView):

    model = Metric
    template_name = 'metrics/list.html'
    context_object_name = 'metrics'

    ordering = ['metric']


@method_decorator(login_required, name='dispatch')
class MetricCreateView(CreateView):

    model = Metric
    form_class = MetricForm
    template_name = 'metrics/create.html'
    success_url = reverse_lazy('dashboard:metrics_list')


    def form_valid(self, form):
        messages.success(self.request, 'Métrica creada con exito')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class MetricDetailView(UpdateView):

    model = Metric
    form_class = MetricForm
    template_name = 'metrics/detail.html'
    success_url = reverse_lazy('dashboard:metrics_list')


    def form_valid(self, form):
        obj = form.save(commit=False)
        messages.success(self.request, 'Métrica actualizada con exito')
        obj.save()

        return HttpResponseRedirect(self.get_success_url())


@method_decorator(login_required, name='dispatch')
class MetricDeleteView(DeleteView):

    model = Metric
    template_name = 'metrics/delete.html'
    success_url = reverse_lazy('dashboard:metrics_list')
    context_object_name = 'metric'


    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Métrica eliminada con exito')
        return super(MetricDeleteView, self).delete(*args, **kwargs)
