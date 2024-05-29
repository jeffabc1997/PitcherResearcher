from django.shortcuts import render
from . import getdata
from .models import Game
from datetime import datetime
# Create your views here.

def games(request):
    getdata.mlbgame()
    current_datetime = datetime.now() # Time zone: western time in US
    date = current_datetime.strftime("%Y-%m-%d")
    games = Game.objects.filter(game_date=date)
    # for g in games:
    #     print('view: ', g.away_pitcher_id.fullName, g.away_team_id.name)
    context = {'contests': games, 'title': 'Baseball is Fun'}
    return render(request, 'gameday/info.html', context)