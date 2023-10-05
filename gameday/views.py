from django.shortcuts import render
from . import getdata
# Create your views here.

def games(request):
    context = {'contests': getdata.mlbgame(), 'title': 'Baseball is Fun'}
    return render(request, 'gameday/info.html', context)