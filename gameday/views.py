from django.shortcuts import render
from . import getdata
# Create your views here.

def games(request):
    gms = getdata.mlbgame()
    context = {'contests': gms, 'title': 'Baseball is Fun'}

    return render(request, 'gameday/info.html', context)