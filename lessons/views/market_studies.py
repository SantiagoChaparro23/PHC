from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from lessons.models import MarketStudies
from lessons.forms.market_studies_form import MarketStudiesForm

# from lessons.models import Areas, Characteristic, InformationType, MarketStudies, Operators, ConnectionStudies, StudyType
# from django.http import HttpResponse
# from django.contrib.auth.models import User
# import json
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.utils.translation import gettext as _
# from django.utils.decorators import method_decorator
# from django.http import JsonResponse
# from lessons.old_forms import ConnectionStudiesForm, MarketStudiesForm


# Create your views here.
class MarketStudiesListView(PermissionRequiredMixin, ListView):

    model = MarketStudies
    template_name = 'market_studies/list.html'
    context_object_name = 'market_studies'
    permission_required = ''

    # queryset = MarketStudies.objects.prefetch_related('study_type', 'information_type', 'characteristic').all()

    # ordering = ['-id']

    # def get_context_data(self, **kwargs):
    #     ctx = super(MarketStudiesListView, self).get_context_data(**kwargs)

    #     success = bool(self.request.GET.get('success',False))

    #     if success:
    #         messages.success(self.request, 'Archivos agregados con exito')
    #     return ctx


# class MarketStudiesDetailView(DetailView):
#     model = MarketStudies
#     template_name = 'market_studies/detail.html'
#     context_object_name = 'marketStudy'
#     permission_required = 'lessons.detail_connectionstudies'


class MarketStudiesCreateView(PermissionRequiredMixin, CreateView):

    model = MarketStudies
    form_class = MarketStudiesForm
    template_name =  'market_studies/create.html'
    success_url = reverse_lazy('lessons:market_studies_list')
    permission_required = ''

    # def get_context_data(self, **kwargs):
    #     ctx = super(MarketStudiesCreateView, self).get_context_data(**kwargs)

    #     #ctx['form'].fields['date'] = '2020-10-10'
    #     #ctx['form'].fields["characteristic"].queryset = Characteristic.objects

    #     return ctx

    def form_valid(self, form):
        # obj = form.save(commit=False)

        # if(obj.characteristic.name == 'Otro'):
            # characteristic = Characteristic(name=obj.other, information_type=obj.information_type)
            # characteristic.save()
            # obj.characteristic = characteristic
        # obj.created_by = self.request.user
        messages.success(self.request, 'Registro creado con éxito')
        # obj.save()
        return super().form_valid(form)


class MarketStudiesDetailView(PermissionRequiredMixin, DetailView):

    model = MarketStudies
    template_name = 'market_studies/detail.html'
    context_object_name = 'market_studies'
    permission_required = ''


class MarketStudiesChangeView(PermissionRequiredMixin, UpdateView):

    model = MarketStudies
    form_class = MarketStudiesForm
    template_name = 'market_studies/change.html'
    success_url = reverse_lazy('lessons:market_studies_list')
    permission_required = ''

    # def get_context_data(self, **kwargs):
    #     ctx = super(MarketStudiesChangeView, self).get_context_data(**kwargs)

    #     self.object = self.get_object()
    #     study_type_id = self.object.study_type.id
    #     information_type_id = self.object.information_type.id

    #     print(information_type_id)
    #     # ctx['form'].fields["information_type"].queryset = InformationType.objects.filter(study_type=study_type_id)
    #     # ctx['form'].fields["characteristic"].queryset = Characteristic.objects.filter(information_type=information_type_id)

    #     return ctx

    def form_valid(self, form):
        # self.object = form.save()
        # obj = form.save(commit=False)

        # if(obj.characteristic.name == 'Otro'):
            # characteristic = Characteristic(name=obj.other, information_type=obj.information_type)
            # characteristic.save()
            # obj.characteristic = characteristic

        messages.success(self.request, 'Registro actualizado con éxito')
        return super().form_valid(form)


class MarketStudiesDeleteView(PermissionRequiredMixin, DeleteView):

    model = MarketStudies
    template_name = 'market_studies/delete.html'
    success_url = reverse_lazy('lessons:market_studies_list')
    context_object_name = 'market_studies'
    permission_required = ''

    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Registro eliminado con éxito')
        return super().delete(*args, **kwargs)


# def get_information_types(request):

#     study_type = request.GET['study_type']

#     # information_types = InformationType.objects.filter(study_type=study_type).values('id', 'name')

#     characteristics = list()

#     # information_type = information_types.first()
#     # if information_type:
#     #     information_type_id = information_type['id']
#     #     characteristics = Characteristic.objects.filter(information_type=information_type_id).values('id', 'name')

#     data = {
#         # 'information_types': list(information_types),
#         'characteristics': list(characteristics)
#     }

#     return JsonResponse(data)


# def get_characteristics(request):

#     information_type = request.GET['information_type']

#     # characteristics = Characteristic.objects.filter(information_type=information_type).values('id', 'name')

#     data = {
#         # 'characteristics': list(characteristics),
#     }

#     return JsonResponse(data)