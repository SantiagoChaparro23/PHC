
from django.shortcuts import render, redirect


def profile_url(request):

    profile_url = f'pictures/{request.user.pk}.jpg'

     
   
    return {'profile_url': profile_url}