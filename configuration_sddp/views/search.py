# from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from configuration_sddp.models import Project, GraphYear, AdditionalCapacity, MetaMatrix, MaxNewCapacity, LcoeEnergyCost, Demand, ExistingPlants, FuturePlants


class SearchTemplateView(PermissionRequiredMixin, TemplateView):

    template_name = 'search/search.html'
    permission_required = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['project'] = Project.objects.values_list('id', 'name')

        pk = self.request.GET.get('q')
        context['pk'] = pk
        if pk:
            context['graph_year'] = GraphYear.objects.filter(project = pk)
            context['additional_capacity'] = AdditionalCapacity.objects.filter(project = pk)
            context['meta_matrix'] = MetaMatrix.objects.filter(project = pk)
            context['max_new_capacity'] = MaxNewCapacity.objects.filter(project = pk)
            context['lcoe_energy_cost'] = LcoeEnergyCost.objects.filter(project = pk)
            context['demand'] = Demand.objects.filter(project = pk)
            context['existing_plants'] = ExistingPlants.objects.filter(project = pk).select_related('plant_type', 'fuel')
            context['future_plants'] = FuturePlants.objects.filter(project = pk).select_related('plant_type', 'fuel')

        # import logging
        # l = logging.getLogger('django.db.backends')
        # l.setLevel(logging.DEBUG)
        # l.addHandler(logging.StreamHandler())

        return context
