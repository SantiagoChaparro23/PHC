from datetime import datetime
from django.db.models import Q
from django.shortcuts import redirect
from django.contrib.auth.models import User

from vacations.models import Settings, Requests

from vacations.helpers.extra_email import create_mails_list, send_notification_mails, send_reminder_mails
from vacations.helpers.days import calculate_days

def daily_routine(request):

    print('daily_routine')

    # Use days since 1970/01/01 as base for send mails using modules
    unix_date = datetime.utcnow().timestamp()
    unix_days = unix_date//86400

    # ---------------------------------------------------------------------
    # Notifications by max accumulated days -------------------------------
    # ---------------------------------------------------------------------

    notify_days_max = Settings.objects.first().notify_days_max

    if int(unix_days%notify_days_max) == 0:

        max_days = Settings.objects.first().days_max

        list_collaborators_to_notify_max_days = [collaborator for collaborator in calculate_days() 
                                            if collaborator.days_available >= max_days]

        print(max_days, list_collaborators_to_notify_max_days)

        #   Email users
        group_users_obligatory = create_mails_list(['group_notify_request', 'final_acceptor'])

        for collaborator in list_collaborators_to_notify_max_days:

            subject = 'Un colaborador supera la cantidad maxima de dias de vacaciones acumulados permitidos '
            mail_message = (f'El colaborador con correo {str(collaborator)} tiene una cantidad de {collaborator.days_available} ' +
                            f'dias de vacaciones que superan el maximo permitido de {max_days}')

            lst_mails = [collaborator]
            lst_mails.extend(group_users_obligatory)

            # FOR TEST
            # lst_mails = ['daniel.restrepo@phc.com.co']        

            send_reminder_mails(lst_mails, mail_message, subject)


    # ---------------------------------------------------------------------
    # Notifications by pending orders -------------------------------------
    # ---------------------------------------------------------------------

    days_notify_request_pending = Settings.objects.first().notify_request_pending

    if int(unix_days%days_notify_request_pending) == 0:

        pending_requests = get_pending_requests()

        leaders_to_notify = list(set([pending_req.leader for pending_req in pending_requests]))

        # add final aceptor and group_notify_request_pending
        group_users_obligatory = create_mails_list(['group_notify_request_pending'])

        

        subject = 'Existen colaboradores pendientes de aceptacion en sus solicitudes de vacaciones'
        mail_message = ('Existen colaboradores pendientes de aceptacion en sus solicitudes de vacaciones')

        lst_mails = group_users_obligatory + leaders_to_notify

        # FOR TEST
        # lst_mails = ['daniel.restrepo@phc.com.co']        

        # send_reminder_mails(lst_mails, mail_message, subject)


    # ---------------------------------------------------------------------
    # Notifications to all users when a collaborator go to vacations ------
    # ---------------------------------------------------------------------

    # Get list from all users and send mail
    lst_mails = [user.username for user in User.objects.all()]

    for request in get_request_to_start():

        subject = f'{str(request.collaborator)} inicia su periodo de vacaciones el dia de hoy' 
        mail_message = (f'Se les informa a todos que {str(request.collaborator)} inicia su periodo ' +
                        f'de vacaciones que va desde el dia {str(request.start_date_vacations)} ' +
                        f'hasta el dia {str(request.end_date_vacations)}')

        print(lst_mails)

        # FOR TEST
        # lst_mails = ['daniel.restrepo@phc.com.co']

        send_notification_mails(lst_mails, mail_message, subject)           

    return redirect('dashboard:home')


def get_pending_requests():

    pending_requests = Requests.objects.filter(Q(accepted_leader__isnull=True)|
                                               Q(accepted_final_acceptor__isnull=True))

    return pending_requests

def get_request_to_start():

    current_date = datetime.now().date()

    starting_vacation_request = Requests.objects.filter(start_date_vacations = current_date, request_completed = True)
    return starting_vacation_request
