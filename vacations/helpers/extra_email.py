from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.conf import settings

from vacations.models import Settings
from helpers.email import sendEmail


def create_mails_list(lst_requirements:list, request_object=None) -> list:
    """Summary
    
    Args:
        lst_requirements (list): List where elements can be the next requirements:
                                    'collaborator'
                                    'leader'
                                    'final_acceptor'
                                    'group_notify_days_max'
                                    'group_notify_request'
                                    'group_notify_request_pending'
                                    'group_notify_request_accepted'
                                    'group_notify_request_deny_final_acceptor'
                                    'group_notify_liquidation_deny'
                                - Each element add the mail or group of mail users
                                  to the mails_list to return 
    
        request_object (None, optional): request_object from model Request
    
    Returns:
        list: List of mails
    
    Raises:
        NotImplementedError: If the lst_requirements have a requirement that not are in the list
    """
    lst_mails = list()

    for requirement in lst_requirements:

        if requirement == 'collaborator':
            lst_mails.append(request_object.collaborator
                                           .user
                                           .username)            

        elif requirement == 'leader':
            lst_mails.append(request_object.leader.username)

        elif requirement == 'final_acceptor':
            lst_mails.append(Settings.objects.first()
                                             .final_acceptor
                                             .username)            

        elif requirement == 'group_notify_days_max':

            for id_user in eval(Settings.objects.first().group_notify_days_max):

                lst_mails.append(User.objects.get(id=id_user)
                                             .username)

        elif requirement == 'group_notify_request':

            for id_user in eval(Settings.objects.first().group_notify_request):
                lst_mails.append(User.objects.get(id=id_user)
                                             .username)

        elif requirement == 'group_notify_request_pending':

            for id_user in eval(Settings.objects.first().group_notify_request_pending):
                lst_mails.append(User.objects.get(id=id_user)
                                             .username)            

        elif requirement == 'group_notify_request_accepted':

            for id_user in eval(Settings.objects.first().group_notify_request_accepted):
                lst_mails.append(User.objects.get(id=id_user)
                                             .username)            

        elif requirement == 'group_notify_request_deny_final_acceptor':

            for id_user in eval(Settings.objects.first().group_notify_request_deny_final_acceptor):
                lst_mails.append(User.objects.get(id=id_user)
                                             .username)

        elif requirement == 'group_notify_liquidation_deny':

            for id_user in eval(Settings.objects.first().group_notify_liquidation_deny):
                lst_mails.append(User.objects.get(id=id_user)
                                             .username)

        else:
            pass
            # raise NotImplementedError(f'Requirement for create_mails_list {requirement} not implemented')

    # Delete duplicated mails
    lst_mails = list(set(lst_mails))

    return lst_mails


def send_notification_mails(lst_mails:list, mail_message:str, subject:str, object = None):

    # Send mails with notification 
    context = {
        'message': mail_message,
        'object': object,
        'URL_SITE': settings.URL_SITE
    }

    body = render_to_string('emails/template_vacations.html', context)


    for mail in lst_mails:
        email = sendEmail(subject, body, mail)


def send_reminder_mails(lst_mails:list, mail_message:str, subject:str, object = None):

    # Send mails with notification 
    context = {
        'message': mail_message,
        'object': object,
        'URL_SITE': settings.URL_SITE
    }

    body = render_to_string('emails/vacations_reminder.html', context)


    for mail in lst_mails:
        email = sendEmail(subject, body, mail)