import os
import uuid
import json

import pandas as pd

from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core import serializers

# Create your views here.
from sddp.models import Project, Db, ReturnRate
from django.http import JsonResponse
from django.conf import settings

from sddp.operating_profit_calculator import (OperatingProfitCalculations, 
                                              OperatingProfitCalculator, 
                                              PreparerFinalDataOperatingProfits,
                                              OperatingProfitDataWriter)


class TemplateView(PermissionRequiredMixin, TemplateView):
    permission_required = 'sddp.view_project'
    template_name = 'operationalbenefits/index.html'

    def get_context_data(self, **kwargs):
        ctx = super(TemplateView, self).get_context_data(**kwargs)

        return_rates = ReturnRate.objects.all().values('year', 'value')
        ctx['rates'] = list(return_rates)

        projects = Project.objects.prefetch_related('dbs').all()
        projects = serializers.serialize('json', projects)

        print(projects)
        ctx['projects'] = projects

        return ctx


def get_dbs(request):
    
    project_id = request.GET['project_id']

    dbs = Db.objects.filter(project_id=project_id).values('id', 'name', 'plant')
  
    data = {
        'dbs': list(dbs),
    }

    return JsonResponse(data)


def get_operationalbenefits(request):

    # Code for calculate operating profits are in spanish, tranlate parameters
    json_data = json.loads(request.body)

    opc = calculate_operational_benefits(json_data)

    # Save data in final dict
    data = dict()

    data['graphics'] = dict()
    for k, df in opc.graphics.items():
        data['graphics'][k] = df.astype(str).to_dict(orient='list')

    data['tables'] = dict()
    for k, df in opc.tables.items():
        data['tables'][k] = df.astype(str).to_dict(orient='list')

    return JsonResponse(data)


def download_operationalbenefits(request):

    import io

    from django.http import HttpResponse


    # Code for calculate operating profits are in spanish, tranlate parameters
    json_data = json.loads(request.body)

    opc = calculate_operational_benefits(json_data)

    # Code for save data in .zip file
    unique_code = uuid.uuid1()  
    base = settings.PROJECT_PATH

    path_name = f'{base}/cache/beneficios_operativos_{unique_code}.zip'    
    opdw = OperatingProfitDataWriter()
    opdw.write_data(opc, path_name)

    # sending response 
    response = HttpResponse(io.open(path_name, mode="rb").read(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="beneficios_operativos.zip"'

    # delete .zip file
    os.remove(path_name)

    return response

# Common code 
def calculate_operational_benefits(json_data):


    #   Build df for rates
    df_rates = pd.DataFrame.from_dict(json_data['rates'])
    df_rates.columns = ['Año', 'Tasa reconocida']

    #   Assemble dict parameters compatible with code from OperatingProfitCalculator
    parameters = {
        'AÑO_CALCULOS'            : json_data['year'],
        'USDCOP'                  : float(json_data['trm']),
        'FECHA_ENTRADA_OPERACION' : pd.Timestamp(json_data['start_date']),
        'FECHA_LIMITE_OPERACION'  : pd.Timestamp(json_data['limit_date']),
        'FACTOR_DEMANDA'          : json_data['demand_factor'],
        'ID_BD_CASO_BASE'         : json_data['base_db'],
        'ID_BD_PROYECTO'          : json_data['db'],
        'DF_TASAS_RECONOCIDAS'    : df_rates,
        'ID_PROYECTO'             : json_data['project_id'],
        'PLANTA_PROYECTO'         : json_data['plant']
    }

    # Calculate operating profits
    #   Initialize container for final results from calculations
    opc = OperatingProfitCalculations()
    #   Perform calculates
    #       First step create raw data
    op_calculator = OperatingProfitCalculator()
    opc = op_calculator.calculate_operating_profit(parameters, opc)
    #       Second step create table and graphic data, ready to return
    pfdop = PreparerFinalDataOperatingProfits()
    opc = pfdop.prepare_final_data(parameters, opc)

    return opc