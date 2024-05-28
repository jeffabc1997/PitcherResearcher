from django.db import models

# Create your models here.

# Need to Learn how to use multiple constructors
# and need to know how to make a custom Field
class Team(models.Model):
    name = models.CharField(max_length=64, default="NullTeam") # from mlb api
    id = models.IntegerField(default=0, primary_key=True) 
    # score = models.IntegerField(default=0) # mlb api
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    pct = models.DecimalField(default=0, decimal_places=3, max_digits=5)
    OPS = models.DecimalField(default=0, decimal_places=3, max_digits=5)
    wRCp = models.IntegerField(default=0)
    wOBA = models.DecimalField(default=0, decimal_places=3, max_digits=5)
    team_abbrev = models.CharField(max_length=16, default="NullAbbrev")
class Pitcher(models.Model):
    fullName = models.CharField(max_length=64, default="TBD") # mlb-api
    id = models.IntegerField(default=0, primary_key=True)
    IP = models.DecimalField(default=0, decimal_places=0, max_digits=5) # from BRef
    # whip = models.DecimalField(default=0, decimal_places=2)
    Win = models.IntegerField(default=0)
    Loss = models.IntegerField(default=0)
    # so9 = models.DecimalField(default=0, decimal_places=2)
    # bb9 = models.DecimalField(default=0, decimal_places=2)
    ERA =  models.DecimalField(default=0, decimal_places=2, max_digits=5)
    xERA = models.DecimalField(default=0, decimal_places=2, max_digits=5) # from fanGraphs
    xFIPm = models.IntegerField(default=0)
    # hardhit_pct = models.DecimalField(default=0, decimal_places=3)
    # barrel_pct = models.DecimalField(default=0, decimal_places=3)
    def __str__(self):
        return str(self.id) + " " + self.name
class Game(models.Model):

    game_id = models.IntegerField(primary_key=True) # PK
    game_date = models.DateField(auto_now=False, auto_now_add=False,default="1900-01-01") # from mlb officialDate
    
#     away_team = Team()
#     away_pitcher = Pitcher()
#     home_team = Team()
#     home_pitcher = Pitcher()
    # away_team = models.CharField(max_length=32, default="NullTeam") # from mlb api
    away_team_id = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_team_id', default=0)
    away_team_score = models.IntegerField(default=0) # mlb api
    # away_team_win = models.IntegerField(default=0)
    # away_team_lose = models.IntegerField(default=0)
    # away_team_pct = models.DecimalField(default=0, decimal_places=3)
    # away_team_ops = models.DecimalField(default=0, decimal_places=3)
    # away_team_wrcp = models.IntegerField(default=0)
    # away_team_woba = models.DecimalField(default=0, decimal_places=3)

    # away_pitcher = models.CharField(max_length=64, default="TBD") # mlb-api
    away_pitcher_id = models.ForeignKey(Pitcher, on_delete=models.CASCADE, related_name='away_pitcher_id', default=-1) # mlb ID
#     # away_pitcher_ip = models.DecimalField(default=0, decimal_places=0) # from BRef
#     # away_pitcher_whip = models.DecimalField(default=0, decimal_places=2)
#     # away_pitcher_win = models.IntegerField(default=0)
#     # away_pitcher_lose = models.IntegerField(default=0)
#     # away_pitcher_so9 = models.DecimalField(default=0, decimal_places=2)
#     # # away_pitcher_bb9 = models.DecimalField(default=0, decimal_places=2)
#     # away_pitcher_xera = models.DecimalField(default=0, decimal_places=2) # from fanGraphs
#     # away_pitcher_xfipm = models.IntegerField(default=0)
#     # away_pitcher_hardhitpct = models.DecimalField(default=0, decimal_places=3)
#     # away_pitcher_barrelpct = models.DecimalField(default=0, decimal_places=3)

    # home_team = models.CharField(max_length=32, default="NullTeam")
    home_team_id = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_team_id', default=0)
    home_team_score = models.IntegerField(default=0)
#     # home_team_ops = models.DecimalField(default=0, decimal_places=3)
    
    # home_pitcher = models.CharField(max_length=64)
    home_pitcher_id = models.ForeignKey(Pitcher, on_delete=models.CASCADE, related_name='home_pitcher_id', default=-1) # mlb ID
#     # home_pitcher_ip = models.DecimalField(decimal_places=1)
#     # home_pitcher_xera = models.DecimalField(decimal_places=2)
#     # home_pitcher_xfipm = models.IntegerField(default=0)
#     date_created = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.game_id)

