import json

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
from django.db import connection

from imports.models import NationalBagPrice, NationalBagPriceCustomDates, NetEffectiveCapacity

from dashboard.forms.phenomenon_form import PhenomenonForm




def lang_context_processor(request):
    return {'LANG': request.LANGUAGE_CODE}



def set_language(request):
    language = request.GET.get('lang', settings.LANGUAGE_CODE)
    translation.activate(language)
    request.session[translation.LANGUAGE_SESSION_KEY] = language
    return redirect('/')



@method_decorator(login_required, name='dispatch')
class PhenomenonListView(ListView):

    model = NationalBagPriceCustomDates
    template_name = 'phenomenons/list.html'
    context_object_name = 'phenomenons'

    ordering = ['date']


@method_decorator(login_required, name='dispatch')
class PhenomenonCreateView(CreateView):
    model = NationalBagPriceCustomDates
    form_class = PhenomenonForm
    template_name = 'phenomenons/create.html'
    success_url = reverse_lazy('dashboard:phenomenon_list')


    def form_valid(self, form):
        messages.success(self.request, 'Fenómeno creado con exito') 
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class PhenomenonDetailView(UpdateView):
    model = NationalBagPriceCustomDates
    template_name = 'phenomenons/detail.html'
   
    success_url = reverse_lazy('dashboard:phenomenon_list')
    form_class = PhenomenonForm

    
    def form_valid(self, form):
        # self.object = form.save()
        obj = form.save(commit=False)
        messages.success(self.request, 'Fenómeno actualizado con exito') 
        obj.save()

        return HttpResponseRedirect(self.get_success_url())


@method_decorator(login_required, name='dispatch')
class PhenomenonDeleteView(DeleteView):
    model = NationalBagPriceCustomDates
    template_name = 'phenomenons/delete.html'
    success_url = reverse_lazy('dashboard:phenomenon_list')
    context_object_name = 'phenomenon'

    
    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Fenómeno eliminado con exito') 
        return super(PhenomenonDeleteView, self).delete(*args, **kwargs)


    