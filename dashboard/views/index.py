from imports.models import NetEffectiveCapacity
from django.http import JsonResponse
import json
from django.utils.translation import gettext as _
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required

from dashboard.helpers.charts import (
    dailyContributionsByMonth,
    monthlyBagPrices,
    yearlyBagPrices,
    maximumNationalOfferPrice,
    generation, 
    netEffectiveCapacity,
    calculateMarginalPlant, 
    check_and_defaults_marginal_plant,
    check_and_defaults_net_effective_capacity,
    usefulDailyVolumePercentage
)

@login_required
def index(request):

    user =  request.user

    context = {'user':user}

    return render(request, 'dashboard/home.html', context)



@login_required
def standar(request):
    
    monthly_bag_prices_chart, girl_phenomenons, boy_phenomenons = monthlyBagPrices()

    daily_contributions_by_month = dailyContributionsByMonth()
    
    yearly_bag_prices_chart = yearlyBagPrices()

    maximum_national_offer_price_chart = maximumNationalOfferPrice()

    date_neteffectivecapacity = check_and_defaults_net_effective_capacity(request)
    net_effective_capacity_chart = netEffectiveCapacity(date_neteffectivecapacity)

    start, end, amount_plants, margin_error = check_and_defaults_marginal_plant(request)
    marginal_plant_chart = calculateMarginalPlant(start, end, amount_plants, margin_error)

    useful_percentage_chart = usefulDailyVolumePercentage() 


    context = {

        'net_effective_capacity':{
            'chart': json.dumps(net_effective_capacity_chart),
            'date': date_neteffectivecapacity,
        },

        'monthly_bag_prices': {
            'chart': json.dumps(monthly_bag_prices_chart), 
            'girl': json.dumps(girl_phenomenons), 
            'boy': json.dumps(boy_phenomenons)
        },

        'yearly_bag_prices': {
            'chart': json.dumps(yearly_bag_prices_chart)
        },        
        
        'maximum_national_offer_price': {
            'chart': json.dumps(maximum_national_offer_price_chart)
        },

      
        'marginal_plant':{
            'chart': json.dumps(marginal_plant_chart),
            'start': start,
            'end': end,
            'amount_plants': amount_plants
        },

        'useful_percentage_chart':{
            'chart': json.dumps(useful_percentage_chart)
        },

        'daily_contributions_by_month':{
            'chart': json.dumps(daily_contributions_by_month)
        }    
    }   

    print(context['daily_contributions_by_month'])

    return render(request, 'dashboard/standar.html', context)



def generation_api(request):

    generation_chart, colors_generation, names_traces  = generation()

    context = {
        'chart': json.dumps(generation_chart),
        'names_traces': json.dumps(names_traces),
        'colors_generation': json.dumps(colors_generation),
    }


    return JsonResponse(context)