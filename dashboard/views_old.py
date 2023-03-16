from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.utils import translation
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.decorators import method_decorator

from django.views.generic import ListView, CreateView, DetailView, FormView, UpdateView, DeleteView
from django.db import connection

from imports.models import BagPrice, BagPriceCustomDates

from .forms import PhenomenonForm



# @login_required
def home_view(request):

    
    cursor = connection.cursor()
    cursor.execute('''
        SELECT 
            CONCAT(to_char(date_trunc('year', date), 'YYYY'), '-', to_char(date_trunc('month', date), 'MM')) AS year,
            ROUND(sum(hour_0+hour_1+hour_2+hour_3+hour_4+hour_5+hour_6+hour_7+hour_8+hour_9+hour_10+hour_11+hour_12+hour_13+hour_14+hour_15+hour_16+hour_17+hour_18+hour_19+hour_20+hour_21+hour_22+hour_23)) AS monthly_sum
        FROM imports_bagprice 
        GROUP BY year
        ORDER BY year
            ''')
    chart1 = cursor.fetchall()
    print(chart1)
    

    context = {
        'hello': _('Hello world'),
        'country': _('country'),
        'chart1': chart1
    }


    return render(request, 'dashboard/home.html', context)


def lang_context_processor(request):
    return {'LANG': request.LANGUAGE_CODE}



def set_language(request):
    language = request.GET.get('lang', settings.LANGUAGE_CODE)
    translation.activate(language)
    request.session[translation.LANGUAGE_SESSION_KEY] = language
    return redirect('/')



@method_decorator(login_required, name='dispatch')
class PhenomenonListView(ListView):

    model = BagPriceCustomDates
    template_name = 'phenomenons/list.html'
    context_object_name = 'phenomenons'

    ordering = ['date']
   

@method_decorator(login_required, name='dispatch')
class PhenomenonCreateView(CreateView):
    model = BagPriceCustomDates
    form_class = PhenomenonForm
    template_name = 'phenomenons/create.html'
    success_url = reverse_lazy('dashboard:phenomenon_list')


    def form_valid(self, form):
        messages.success(self.request, 'Fenómeno creado con exito') 
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class PhenomenonDetailView(UpdateView):
    model = BagPriceCustomDates
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
    model = BagPriceCustomDates
    template_name = 'phenomenons/delete.html'
    success_url = reverse_lazy('dashboard:phenomenon_list')
    context_object_name = 'phenomenon'

    
    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Fenómeno eliminado con exito') 
        return super(PhenomenonDeleteView, self).delete(*args, **kwargs)


    