from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http.response import HttpResponseRedirect

from vacations.models import Settings

from vacations.forms.settings_form import SettingsForm
from django.contrib.auth.models import User

# Create your views here.
class SettingsUpdateView(PermissionRequiredMixin, UpdateView):

    model = Settings
    form_class = SettingsForm
    template_name = 'settings/change.html'
    # success_url = reverse_lazy('vacations:settings_change')
    context_object_name = 'settings'
    permission_required = 'vacations.change_settings'

    def get_context_data(self, **kwargs):
        ctx = super(SettingsUpdateView, self).get_context_data(**kwargs)

        ctx['form'].fields['final_acceptor'].label_from_instance = lambda obj: "%s %s" % (obj.first_name, obj.last_name)

        ctx['users'] = User.objects.all()

        print(self.object.group_notify_days_max)

        ctx['group_notify_days_max']         = [int(elm) for elm in eval(self.object.group_notify_days_max)]
        ctx['group_notify_request']          = [int(elm) for elm in eval(self.object.group_notify_request)]
        ctx['group_notify_request_pending']  = [int(elm) for elm in eval(self.object.group_notify_request_pending)]
        ctx['group_notify_request_accepted'] = [int(elm) for elm in eval(self.object.group_notify_request_accepted)]
        ctx['group_notify_request_deny_final_acceptor'] = [int(elm) for elm in eval(self.object.group_notify_request_deny_final_acceptor)]
        ctx['group_notify_liquidation_deny'] = [int(elm) for elm in eval(self.object.group_notify_liquidation_deny)]

        return ctx    

    def get_success_url(self):

        self.object.group_notify_days_max         = self.request.POST.getlist('notify_to[]')
        self.object.group_notify_request          = self.request.POST.getlist('notify_request_to[]')
        self.object.group_notify_request_pending  = self.request.POST.getlist('notify_pending_request_to[]')
        self.object.group_notify_request_accepted = self.request.POST.getlist('notify_acepted_request_to[]')
        self.object.group_notify_request_deny_final_acceptor = self.request.POST.getlist('notify_rejected_request_to[]')
        self.object.group_notify_liquidation_deny = self.request.POST.getlist('notify_rejected_liquitys_to[]')

        self.object.save()   

        return reverse_lazy('vacations:settings_change', args=[self.object.id])

    def form_valid(self, form):
        obj = form.save(commit=False)
        messages.success(self.request, 'Configuración actualizada con éxito')
        obj.save()

        return HttpResponseRedirect(self.get_success_url())


class SettingsDetailView(PermissionRequiredMixin, DetailView):
    model = Settings
    template_name = 'settings/detail.html'
    context_object_name = 'settings'
    permission_required = 'vacations.view_settings'

    def get_context_data(self, **kwargs):

        ctx = super(SettingsDetailView, self).get_context_data(**kwargs)

        ctx['users'] = User.objects.all()

        ctx['group_notify_days_max']         = self.__get_names_list(self.object.group_notify_days_max)
        ctx['group_notify_request']          = self.__get_names_list(self.object.group_notify_request)
        ctx['group_notify_request_pending']  = self.__get_names_list(self.object.group_notify_request_pending)
        ctx['group_notify_request_accepted'] = self.__get_names_list(self.object.group_notify_request_accepted)
        ctx['group_notify_request_deny_final_acceptor'] = self.__get_names_list(self.object.group_notify_request_deny_final_acceptor)
        ctx['group_notify_liquidation_deny'] = self.__get_names_list(self.object.group_notify_liquidation_deny)

        return ctx

    @staticmethod
    def __get_names_list(str_list):
        return [User.objects.filter(id=id_user)[0].first_name + ' ' + User.objects.filter(id=id_user)[0].last_name
                 for id_user in eval(str_list)]
