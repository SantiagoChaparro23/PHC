from django.views.generic import TemplateView
from django.http import HttpResponse

from lessons.models import (
    ElectricalStudies,
    Consultancies,
    ProtectionCoordinationStudies,
    ConnectionStudies,
    MarketStudies,
    LESSON_TYPE,
    SUBCATEGORY
)

from io import BytesIO
import pandas as pd
import numpy as np


class ReportsTemplateView(TemplateView):

    template_name =  'reports/reports.html'

    def post(self, request):

        electrical_studies = ElectricalStudies.objects.select_related(
            'budgeted_hours',
            'client',
            'created_by'
        ).values(
            'title',
            'created_at',
            'budgeted_hours__code',
            'client__client',
            'created_by__username',
            'lesson_type',
            'description',
            'action_plan',
        )
        consultancies = Consultancies.objects.select_related(
            'budgeted_hours',
            'client',
            'created_by'
        ).values(
            'title',
            'created_at',
            'budgeted_hours__code',
            'client__client',
            'created_by__username',
            'lesson_type',
            'description',
            'action_plan',
        )
        protection_coordination_studies = ProtectionCoordinationStudies.objects.select_related(
            'budgeted_hours',
            'client',
            'created_by'
        ).values(
            'title',
            'created_at',
            'budgeted_hours__code',
            'client__client',
            'created_by__username',
            'lesson_type',
            'description',
            'action_plan',
            'subcategory',
            'subcategory_description',
            'element_type',
            'element_type_description',
            'protection',
            'relay_brand',
            'relay_brand_description',
            'relay_model',
        )
        connection_studies = ConnectionStudies.objects.select_related(
            'budgeted_hours',
            'client',
            'created_by',
            'zone',
            'operator',
            'area'
        ).values(
            'title',
            'created_at',
            'budgeted_hours__code',
            'client__client',
            'created_by__username',
            'zone__name',
            'operator__name',
            'area__name',
            'lesson_type',
            'subcategory',
            'description',
            'action_plan',
        )
        market_studies = MarketStudies.objects.select_related(
            'budgeted_hours',
            'client',
            'created_by'
        ).values(
            'title',
            'created_at',
            'budgeted_hours__code',
            'client__client',
            'created_by__username',
            'study_type',
            'lesson_type',
            'subcategory',
            'description',
            'action_plan',
        )

        df_electrical_studies = pd.DataFrame(list(electrical_studies))
        df_consultancies = pd.DataFrame(list(consultancies))
        df_protection_coordination_studies = pd.DataFrame(list(protection_coordination_studies))
        df_connection_studies = pd.DataFrame(list(connection_studies))
        df_market_studies = pd.DataFrame(list(market_studies))

        print(LESSON_TYPE)
        df_conventions1 = pd.DataFrame({'pr': LESSON_TYPE})
        df_conventions2 = pd.DataFrame({'pr2': SUBCATEGORY})

        df_conventions = pd.concat([df_conventions1, df_conventions2], ignore_index=True, axis=1)
        print(df_conventions)


        with BytesIO() as b:
            writer = pd.ExcelWriter(b, engine='xlsxwriter')
            df_conventions.to_excel(writer, sheet_name='Convenciones', index=False)
            df_electrical_studies.to_excel(writer, sheet_name='electrical_studies', header=["Sequence", "Start", "End", "Coverage", "Sequence", "Start", "End", "Coverage"], index=False)
            df_consultancies.to_excel(writer, sheet_name='consultancies', index=False)
            df_protection_coordination_studies.to_excel(writer, sheet_name='protection_coordination_studies', index=False)
            df_connection_studies.to_excel(writer, sheet_name='connection_studies', index=False)
            df_market_studies.to_excel(writer, sheet_name='market_studies', index=False)
            writer.save()

            filename = 'Reporte_lecciones'
            content_type = 'application/vnd.ms-excel'
            response = HttpResponse(b.getvalue(), content_type=content_type)
            response['Content-Disposition'] = 'attachment; filename="' + filename + '.xlsx"'
            return response
