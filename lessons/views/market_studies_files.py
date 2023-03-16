# from lessons.models import MarketStudiesFiles
from django.utils.translation import gettext as _
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, DetailView, FormView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
import zipfile
import os
from django.conf import settings
import glob
import io

from lessons.old_forms import MarketStudiesFilesForm
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime


@method_decorator(csrf_exempt, name='dispatch')
class MarketStudiesFilesChangeView(PermissionRequiredMixin, UpdateView):
    template_name = 'market_studies_files/change.html'
    # model = MarketStudiesFiles
    context_object_name = 'file'
    success_url = reverse_lazy('lessons:market_studies_list')
    form_class = MarketStudiesFilesForm
    permission_required = 'lessons.change_marketstudies'

    def handle_uploaded_file(self, f, tmp_folder):
        with open(f'{tmp_folder}/{f.name}', 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    
    def form_valid(self, form):
        request = self.request 
        unix = int(datetime.now().timestamp())

    
        base = settings.PROJECT_PATH

        tmp_folder = f'{base}/storage/marketstudies/{unix}'
        
        os.makedirs(tmp_folder)

        files = []

        for filename, file in request.FILES.items():
            files.append(str(file))
            self.handle_uploaded_file(file, tmp_folder)

        
        type = self.object.get_type();
        object = self.object
        filename = f'{base}/static/market_studies/{object.file_name}-{unix}.zip'

        command = f'zip -r -j {filename} {tmp_folder}'
        print(command)
        os.system(command)
        


        obj = form.save(commit=False)

        files = '<br>'.join(files)
        print(files)
        obj.files = files
        obj.file = f'static/market_studies/{object.file_name}-{unix}.zip'


        obj.save()

        messages.success(self.request, 'Archivos agregados con exito') 
        return super().form_valid(form)








