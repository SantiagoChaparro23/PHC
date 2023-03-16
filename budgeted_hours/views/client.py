# from django.db.models.aggregates import Count
from django.http import request
from django.shortcuts import render, redirect
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

# from django.core.exceptions import PermissionDenied

import pandas as pd

from budgeted_hours.models import Client
from budgeted_hours.forms.client_form import ClientForm

# Create your views here.
# @method_decorator(login_required, name='dispatch')
class ClientListView(PermissionRequiredMixin, ListView):

    model = Client
    template_name = 'client/list.html'
    context_object_name = 'clients'
    permission_required = 'budgeted_hours.view_client'


def client_import(request):
    if request.method == 'POST':
        try:
            df_ini = pd.read_excel(request.FILES['file'], engine = 'openpyxl')
            df = pd.DataFrame()
            clients = Client.objects.all()

            dict_names = {
                'Name': 'client'
            }

            for name_col in dict_names.keys():
                if name_col not in df_ini.columns:
                    raise NameError(f'La columna "{name_col}" no se encuentra en el archivo')

            df['client'] = df_ini['Name']

            # df.rename(columns=dict_names, inplace=True)
            df = df.astype(str)
            df.replace(to_replace=["nan", " - "], value=[None, None], inplace=True)
            # print(df)

            for index, row in df.iterrows():
                # print(row[0])
                count = 0
                for client in clients:
                    if row[0].upper() == client.client.upper():
                        count = 1

                if count == 0:
                    instance = Client(
                        client = row[0].upper()
                    )
                    instance.save()

            messages.success(request, 'Importación realizada con éxito')
            return redirect('budgeted_hours:clients_list')

        except Exception as e:
            # print(e)
            messages.error(request, 'Error de importación: ' + str(e))
            return redirect('budgeted_hours:client_import')

    else:
        return render(request, 'import_file/import_file.html')


# @method_decorator(login_required, name='dispatch')
class ClientCreateView(PermissionRequiredMixin, CreateView):

    model = Client
    form_class = ClientForm
    template_name = 'client/create.html'
    success_url = reverse_lazy('budgeted_hours:clients_list')
    permission_required = 'budgeted_hours.add_client'


    def form_valid(self, form):
        messages.success(self.request, 'Cliente creado con éxito')
        return super().form_valid(form)


# @method_decorator(login_required, name='dispatch')
class ClientDetailView(PermissionRequiredMixin, UpdateView):

    model = Client
    form_class = ClientForm
    template_name = 'client/detail.html'
    success_url = reverse_lazy('budgeted_hours:clients_list')
    permission_required = 'budgeted_hours.change_client'
    # permission_denied_message = 'No cuenta con permiso'
    # raise_exception = True


    # def get_permission_denied_message(self):
    #     return self.permission_denied_message


    # def handle_no_permission(self):
    #     print(self.raise_exception)
    #     # print(self.request.user.is_authenticated)
    #     if self.raise_exception: # or self.request.user.is_authenticated:
    #         # raise PermissionDenied(self.get_permission_denied_message())
    #         messages.error(self.request, self.permission_denied_message)
    #         return redirect('budgeted_hours:clients_list')


    def form_valid(self, form):
        obj = form.save(commit=False)
        messages.success(self.request, 'Cliente actualizado con éxito')
        obj.save()

        return HttpResponseRedirect(self.get_success_url())


# @method_decorator(login_required, name='dispatch')
class ClientDeleteView(PermissionRequiredMixin, DeleteView):

    model = Client
    template_name = 'client/delete.html'
    success_url = reverse_lazy('budgeted_hours:clients_list')
    context_object_name = 'client'
    permission_required = 'budgeted_hours.delete_client'


    def delete(self, *args, **kwargs):
        messages.success(self.request, 'Cliente eliminado con éxito')
        return super(ClientDeleteView, self).delete(*args, **kwargs)
