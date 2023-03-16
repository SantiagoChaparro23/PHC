from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth import logout
import requests
from django.shortcuts import redirect, reverse
from django.conf import settings
from .forms import LoginForm
import os

def login_view(request):

    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('dashboard:home'))

    form = LoginForm(use_required_attribute=False)
    
    if request.method == 'POST':
    
        form = LoginForm(request.POST, use_required_attribute=False)
        if form.is_valid():

            email = form.cleaned_data['email']
            email = email.lower()
            password = form.cleaned_data['password']
            user = authenticate(username=email, password=password)

            if user:
                login(request, user)
                return HttpResponseRedirect(reverse('dashboard:home'))
              
            else:   
                messages.error(request, 'Usuario no encontrado!') 
               



    context = {
        'form': form
    }

    return render(request, 'users/login.html', context)



def logout_view(request):
    logout(request) 
    return HttpResponseRedirect(reverse('users:login'))


def microsoft_login(request):
    authorize_url = settings.MICROSOFT_PROVIDER['authorize'];
    client_id = settings.MICROSOFT_PROVIDER['client_id'];
    callback = settings.MICROSOFT_PROVIDER['callback'];

    url = f'{authorize_url}?client_id={client_id}&redirect_uri={callback}&scope=User.Read&response_type=code&state=HAvWVLjuFYzS'


    return HttpResponseRedirect(url)
    return HttpResponse(url)

def microsoft_request_token(request):

    token_url = settings.MICROSOFT_PROVIDER['token'];
    client_id = settings.MICROSOFT_PROVIDER['client_id'];
    secret = settings.MICROSOFT_PROVIDER['secret'];
    callback = settings.MICROSOFT_PROVIDER['callback'];

    code = request.GET.get('code', None)

    if code:

        payload=f'client_id={client_id}&scope=user.read&code={code}&redirect_uri={callback}&grant_type=authorization_code&client_secret={secret}'

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.request("POST", token_url, headers=headers, data=payload)
       
        if response.status_code == 200:
            json = response.json()

            access_token = json['access_token']

            url = "https://graph.microsoft.com/v1.0/me"

            payload={}
            headers = {'Authorization': f'Bearer {access_token}'}
           
            response = requests.request("GET", url, headers=headers, data=payload)

            if response.status_code == 200:
                try:
                    json = response.json()
                    mail = json['mail']
                    
                    mail = mail.lower()
                    print(mail)
                    user = User.objects.get(email__exact=mail)
                    if user:
                        print('entro a crear image')
                        savePicture(user, access_token)
                        login(request, user)
                        return HttpResponseRedirect(reverse('dashboard:home'))
                    messages.error(request, f'No tienes permiso para ingresar con el correo {mail}') 
                except Exception as e:
                    print('error')
                    print(e)
                    pass
               
    
    
    return HttpResponseRedirect(reverse('users:login'))



def savePicture(user, access_token):
    try:
        base = settings.PROJECT_PATH
        uri = f"{base}/static/pictures/{user.pk}.jpg"
        print(uri)
        if not os.path.exists(uri):
            url = 'https://graph.microsoft.com/v1.0/me/photo/$value'
            payload={}

            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.request("GET", url, headers=headers, data=payload)
            img_blob = response.content

            # if not os.path.isdir("static/pictures"):
            #     os.mkdir("static/pictures")

            with open(uri, 'wb') as img_file:
                img_file.write(img_blob)

    except Exception as e:
        print('error')
        print(e)
        pass

def microsoft_token(request):

   
    base = settings.PROJECT_PATH
    print(base)
    #print(os.path.exists("static/pictures/7.jpg"))

    # mail = 'daniel.londono@phc.com.co'
    # user = User.objects.get(email__exact=mail)
    # access_token = 'eyJ0eXAiOiJKV1QiLCJub25jZSI6IkJ4RU1wOElmR1c2bEFSMmhycVhDdmFBTEtvWDdkQWxBNi1wZ1QzNG5nYVkiLCJhbGciOiJSUzI1NiIsIng1dCI6Im5PbzNaRHJPRFhFSzFqS1doWHNsSFJfS1hFZyIsImtpZCI6Im5PbzNaRHJPRFhFSzFqS1doWHNsSFJfS1hFZyJ9.eyJhdWQiOiIwMDAwMDAwMy0wMDAwLTAwMDAtYzAwMC0wMDAwMDAwMDAwMDAiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC82NmQ1NmMxZC1kMDBmLTQ2ODYtOWEyOC1lYjk2ZDFlYWY1YmIvIiwiaWF0IjoxNjIyNzEzNjc1LCJuYmYiOjE2MjI3MTM2NzUsImV4cCI6MTYyMjcxNzU3NSwiYWNjdCI6MCwiYWNyIjoiMSIsImFjcnMiOlsidXJuOnVzZXI6cmVnaXN0ZXJzZWN1cml0eWluZm8iLCJ1cm46bWljcm9zb2Z0OnJlcTEiLCJ1cm46bWljcm9zb2Z0OnJlcTIiLCJ1cm46bWljcm9zb2Z0OnJlcTMiLCJjMSIsImMyIiwiYzMiLCJjNCIsImM1IiwiYzYiLCJjNyIsImM4IiwiYzkiLCJjMTAiLCJjMTEiLCJjMTIiLCJjMTMiLCJjMTQiLCJjMTUiLCJjMTYiLCJjMTciLCJjMTgiLCJjMTkiLCJjMjAiLCJjMjEiLCJjMjIiLCJjMjMiLCJjMjQiLCJjMjUiXSwiYWlvIjoiQVNRQTIvOFRBQUFBUDY3VXliTWQxaGZ0bHJYOFZDekhhbmhGRURZeDRrRndnekRRaE91OFAvVT0iLCJhbXIiOlsicHdkIl0sImFwcF9kaXNwbGF5bmFtZSI6ImRhdGNvcmUiLCJhcHBpZCI6IjQwOGU1YjMyLTUxYjUtNDhjOS05YTJjLTJkYmI1MTBiYjAzYyIsImFwcGlkYWNyIjoiMSIsImZhbWlseV9uYW1lIjoiTG9uZG_DsW8iLCJnaXZlbl9uYW1lIjoiRGFuaWVsIiwiaWR0eXAiOiJ1c2VyIiwiaXBhZGRyIjoiMTkwLjI0OC4xMDQuNTAiLCJuYW1lIjoiRGFuaWVsICBMb25kb8OxbyIsIm9pZCI6ImVmNzc2YmRlLTgxZTEtNDdmNS1hZDJjLTMwNWYyMDE1NmVkZSIsInBsYXRmIjoiNSIsInB1aWQiOiIxMDAzMjAwMTEzNkQzRkVGIiwicmgiOiIwLkFTVUFIV3pWWmdfUWhrYWFLT3VXMGVyMXV6SmJqa0MxVWNsSW1pd3R1MUVMc0R3bEFJby4iLCJzY3AiOiJVc2VyLlJlYWQgcHJvZmlsZSBvcGVuaWQgZW1haWwiLCJzaWduaW5fc3RhdGUiOlsia21zaSJdLCJzdWIiOiJ3aWVvN2NlZGIzTTRlNFFoQlhKYUsxbFJSSU4xbEFIT0wyS1BfSXkwX0dzIiwidGVuYW50X3JlZ2lvbl9zY29wZSI6IlNBIiwidGlkIjoiNjZkNTZjMWQtZDAwZi00Njg2LTlhMjgtZWI5NmQxZWFmNWJiIiwidW5pcXVlX25hbWUiOiJkYW5pZWwubG9uZG9ub0BwaGMuY29tLmNvIiwidXBuIjoiZGFuaWVsLmxvbmRvbm9AcGhjLmNvbS5jbyIsInV0aSI6IkdnWHZsOWhNZzBHNmF4TVlKdGJjQWciLCJ2ZXIiOiIxLjAiLCJ3aWRzIjpbImI3OWZiZjRkLTNlZjktNDY4OS04MTQzLTc2YjE5NGU4NTUwOSJdLCJ4bXNfc3QiOnsic3ViIjoicTEyMGNxalp0YWF1NEhlc2ZZUENhODY1RWE0S1gwc0xhdXFwbTQxbkhCNCJ9LCJ4bXNfdGNkdCI6MTQ3NTY5Njc4N30.VccpXToK6kay7KIYz6Bsj_My0AZFhNi-GL3A7lngKRYy61T5qNle78ocm_rd5uyETT_92eoY6sMYAUFFPhIuL_puH4f-hLNkRyAQJUXuNQJz1sr-ZEPLR5BJBbpZhVzmfwpe9XWFI3c5UlzsG4m1cxyLNqfqzbfnjlkcn0Ml_CxO9R6mldsxVZSi5K58p1dp0hBr7EVYPPqrML9eNg2Jp1BFQgilzEDMRrDBwOd2bhFnO0S5AKjQAn5t9Jgw46h9kcHZlo0S2bo8jLQ9d1159L3WnG9N0SJmSbQwow120Ea-eZ26JfpxTOjCg5XDmm1Dv3aphmr0XPI45DuOn6wQVw'

    # savePicture(user, access_token)

    return HttpResponse('response')
    
    url = 'https://graph.microsoft.com/v1.0/me/photo/$value'
   
    payload={}
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.request("GET", url, headers=headers, data=payload)

    user = User.objects.get(email__exact=mail)
    img_blob = response.content
    with open('storage/pictures/picture.jpg', 'wb') as img_file:
         img_file.write(img_blob)

    return HttpResponse(response)
    # messages.error(request, 'No tienes permiso para ingresar') 
    # return HttpResponseRedirect(reverse('users:login'))

    # mail = 'daniel.londono@phc.com.co'
    # try:
    #     user = User.objects.get(email__exact=mail)
    #     print(user)
    #     if user:
    #         login(request, user)
    #         return HttpResponseRedirect(reverse('dashboard:home'))
    # except Exception:
    #     messages.error(request, 'No tienes permiso para ingresar') 
    #     return HttpResponseRedirect(reverse('users:login'))
    
    