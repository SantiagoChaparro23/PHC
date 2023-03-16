from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.utils import translation
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.decorators import method_decorator
import logging
from django.views.generic import ListView, CreateView, DetailView, FormView, UpdateView, DeleteView

from imports.models import UrlsFilesMetric, UrlsFilesMetricTask

from imports.formats import Format1, Format2

from dashboard.forms.files_metric_form import UrlsFilesMetricForm

from datetime import datetime





def set_language(request):
    language = request.GET.get('lang', settings.LANGUAGE_CODE)
    translation.activate(language)
    return redirect('/')


@method_decorator(login_required, name='dispatch')
class UrlsFilesMetricListView(ListView):

    model = UrlsFilesMetric
    template_name = 'files_metric/list.html'
    context_object_name = 'urls_files_metrics'


 
    ordering = ['-year_file', 'pk']


@method_decorator(login_required, name='dispatch')
class UrlsFilesMetricCreateView(CreateView):

    model = UrlsFilesMetric
    form_class = UrlsFilesMetricForm
    template_name = 'files_metric/create.html'
    success_url = reverse_lazy('dashboard:files_metrics_list')


    def form_valid(self, form):
        return super().form_valid(form)
        messages.success(self.request, 'Datos de archivo de metrica creados con exito')


@method_decorator(login_required, name='dispatch')
class UrlsFilesMetricDetailView(UpdateView):

    model = UrlsFilesMetric
    form_class = UrlsFilesMetricForm
    template_name = 'files_metric/detail.html'
    success_url = reverse_lazy('dashboard:files_metrics_list')


    def form_valid(self, form):
        obj = form.save(commit=False)
        messages.success(self.request, 'Datos de archivo de metrica actualizados con exito')
        obj.save()

        return HttpResponseRedirect(self.get_success_url())


@method_decorator(login_required, name='dispatch')
class UrlsFilesMetricDeleteView(DeleteView):

    model = UrlsFilesMetric
    template_name = 'files_metric/delete.html'
    success_url = reverse_lazy('dashboard:files_metrics_list')
    context_object_name = 'urls_files_metrics'


    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Datos de archivo de metrica eliminados con exito')
        return super(UrlsFilesMetricDeleteView, self).delete(*args, **kwargs)






class UrlsFilesMetricProcessView(DetailView):

    model = UrlsFilesMetric


    def get(self , request , *args , **kwargs):

   
        self.object = self.get_object() 
       
        
        switcher = {
            1: Format1,
            2: Format2
        }
        
        f =  switcher.get(self.object.metric.format)      
       
        if f:

            
            error = False
            try:
                start = datetime.now().timestamp()

                f(self.object.url_file, self.object.metric.name_table)

                end = datetime.now().timestamp()

                messages.success(self.request, 'Importación realizada con exito') 
                
            except Exception as e:
                logging.error(f"Error procesando metrica {self.object.pk}", extra=dict(metric=self.object.url_file))
                messages.error(self.request, 'Error al tratar de hacer la importacion') 
                error = True
                raise e

        
            seconds = int(end-start)

            task = UrlsFilesMetricTask(metric_id=self.object.pk, has_error=error, seconds=seconds)
            task.save()

            UrlsFilesMetric.objects.filter(pk=self.object.id).update(processing_time=seconds, last_update=datetime.now())
            


        else:
            messages.error(self.request, 'Error al tratar de hacer la importacion') 
        
        
        return HttpResponseRedirect(reverse('dashboard:files_metrics_list'))



