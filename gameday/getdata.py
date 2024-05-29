import statsapi
import pybaseball
from datetime import datetime, timezone, timedelta
import math
from .models import Game, Team, Pitcher
# Should put this function else where
# Add abbreviation name for teams
teamAbbrev = {'Arizona Diamondbacks': 'ARI', 'Atlanta Braves': 'ATL', 'Baltimore Orioles': 'BAL', 'Boston Red Sox': 'BOS', 'Chicago Cubs': 'CHC', 'Cincinnati Reds': 'CIN', \
              'Cleveland Guardians': 'CLE', 'Colorado Rockies': 'COL', 'Chicago White Sox': 'CWS', 'Detroit Tigers': 'DET', 'Houston Astros': 'HOU', 'Kansas City Royals': 'KC', \
              'Los Angeles Angels': 'LAA', 'Los Angeles Dodgers': 'LAD', 'Miami Marlins': 'MIA', 'Milwaukee Brewers': 'MIL', 'Minnesota Twins': 'MIN', 'New York Mets': 'NYM', \
              'New York Yankees': 'NYY', 'Oakland Athletics': 'OAK', 'Philadelphia Phillies': 'PHI', 'Pittsburgh Pirates': 'PIT', 'San Diego Padres': 'SD', 'Seattle Mariners': 'SEA', \
              'San Francisco Giants': 'SF', 'St. Louis Cardinals': 'STL', 'Tampa Bay Rays': 'TB', 'Texas Rangers': 'TEX', 'Toronto Blue Jays': 'TOR', 'Washington Nationals': 'WSH'}
teamtoFgId = {'Arizona Diamondbacks': 15, 'Atlanta Braves': 16, 'Baltimore Orioles': 2, 'Boston Red Sox': 3, 'Chicago Cubs': 17, 'Cincinnati Reds': 18, \
              'Cleveland Guardians': 5, 'Colorado Rockies': 19, 'Chicago White Sox': 4, 'Detroit Tigers': 6, 'Houston Astros': 21, 'Kansas City Royals': 7, \
              'Los Angeles Angels': 1, 'Los Angeles Dodgers': 22, 'Miami Marlins': 20, 'Milwaukee Brewers': 23, 'Minnesota Twins': 8, 'New York Mets': 25, \
              'New York Yankees': 9, 'Oakland Athletics': 10, 'Philadelphia Phillies': 26, 'Pittsburgh Pirates': 27, 'San Diego Padres': 29, 'Seattle Mariners': 11, \
              'San Francisco Giants': 30, 'St. Louis Cardinals': 28, 'Tampa Bay Rays': 12, 'Texas Rangers': 13, 'Toronto Blue Jays': 14, 'Washington Nationals': 24}

thisYear = 2024
baseballRefPitcher = pybaseball.pitching_stats_bref(thisYear)
allPitcherStats = pybaseball.pitching_stats(thisYear, qual = 1)
allTeamBatStats = pybaseball.team_batting(thisYear, thisYear, ind=0)
def findpitcher(mlbid):
    global allPitcherStats, baseballRefPitcher
    # df = pybaseball.pitching_stats(2023, qual = 1) # all pitching stats
    # put only 1 player in this function for the right order
    statDict = {}
    brefOK = True
    try: 
        brefPlayer = baseballRefPitcher.loc[baseballRefPitcher['mlbID'] == str(mlbid)].to_dict('records')[0]
        statDict['Win'] = int(brefPlayer['W']) if not math.isnan(brefPlayer['W']) else 0
        statDict['Loss'] = int(brefPlayer['L']) if not math.isnan(brefPlayer['L']) else 0
        statDict['IP'] = round(brefPlayer['IP'],2) if not math.isnan(brefPlayer['IP']) else 0
        statDict['ERA'] = round(brefPlayer['ERA'], 2)# "{:.2f}".format(brefPlayer['ERA'])
        statDict['WHIP'] = round(brefPlayer['WHIP'],2)# "{:.2f}".format(brefPlayer['WHIP'])
        # statDict['SO9'] = round(brefPlayer['SO9'], 2)#"{:.2f}".format(brefPlayer['SO9'])
    except:
        brefOK = False # we can try these data in Fangraph
        print(f"No data in Baseball Reference. MLB ID: {mlbid}")

    try: # try if we have data in Fangraph API   
        key = pybaseball.playerid_reverse_lookup([mlbid], key_type='mlbam')
        fgid = key['key_fangraphs'].values[0] # fangraphs ID 
        aPlayer = allPitcherStats.loc[allPitcherStats['IDfg'] == fgid].to_dict('records')[0]
        if brefOK == False:
            statDict['Win'] = aPlayer['W']
            statDict['Loss'] = aPlayer['L']
            statDict['IP'] = round(aPlayer['IP'], 2)
            statDict['ERA'] = round(aPlayer['ERA'], 2)# "{:.2f}".format(aPlayer['ERA'])
        statDict['xFIPm'] = aPlayer['xFIP-'] # beware that xFIP- is renamed to xFIPm
        statDict['xERA'] = round(aPlayer['xERA'], 2)
    except:
        print(f"MLB ID:{mlbid} not found in Fangraph API.")

    return statDict

def findTeamStats(name):
    global allTeamBatStats, teamtoFgId
    battingOfTeam = allTeamBatStats.loc[allTeamBatStats['teamIDfg'] == teamtoFgId[name], ["OPS", "wOBA", "wRC+"]]
    battingOfTeam = battingOfTeam.rename(columns={'wRC+': 'wRCp'}) # html can't parse '+'
    battingdict = battingOfTeam.to_dict('records')[0]
    battingdict['wOBA'] = round(battingdict['wOBA'], 3) #"{:.3f}".format(battingdict['wOBA'])
    battingdict['OPS'] = round(battingdict['OPS'], 3) #"{:.3f}".format(battingdict['OPS'])
    return battingdict
# getting the year from the current date and time
def mlbgame():
    obj_tbd, created = Pitcher.objects.update_or_create(
            id=-1, defaults={'fullName': 'TBD',}
        )
    current_datetime = datetime.now() # Time zone: western time in US
    date = current_datetime.strftime("%m/%d/%Y")
    
    # date = "09/30/2023"
    params = {
        "sportId": 1,
        "date": date,
        "hydrate": "probablePitcher(note)",
    }
    schedule = statsapi.get("schedule", params) # Future Progress: can update schedule for probable pitcher without process termination
    if schedule['totalGames'] == 0:
        return

    gamethatday = schedule["dates"][0]["games"]
    # print(gamethatday)

    existed_games = Game.objects.filter(game_date=current_datetime.strftime("%Y-%m-%d"))
    pitcher_updated = True
    for ex in existed_games:
        if ex.away_pitcher_id.id == -1 or ex.home_pitcher_id.id == -1: # if there is a TBD pitcher, we need to update the game data
            pitcher_updated = False
            break
    if pitcher_updated: # we don't need to update the game data
        return
    
    home_pitcher_dic = {} # replace gamethatday with information we need from the API
    away_pitcher_dic = {}
    for i in range(len(gamethatday)): # update data in gamethatday
        try:
            home_pitcher_dic.update(findpitcher(gamethatday[i]['teams']['home']['probablePitcher']['id']))
            home_pitcher_dic['id'] = gamethatday[i]['teams']['home']['probablePitcher']['id'] # MLB ID
            home_pitcher_dic['fullName'] = gamethatday[i]['teams']['home']['probablePitcher']['fullName']
            # print('home pitcher', home_pitcher_dic)

        except:
            # if can't find a pitcher, give it TBD
            home_pitcher_dic['id'] = -1
            home_pitcher_dic['fullName'] = 'TBD'
            print('home pitcher not found', home_pitcher_dic)

        try:
            away_pitcher_dic.update(findpitcher(gamethatday[i]['teams']['away']['probablePitcher']['id']))
            away_pitcher_dic['id'] = gamethatday[i]['teams']['away']['probablePitcher']['id']
            away_pitcher_dic['fullName'] = gamethatday[i]['teams']['away']['probablePitcher']['fullName']

        except:
            away_pitcher_dic['id'] = -1
            away_pitcher_dic['fullName'] = 'TBD'
            print('away pitcher not found', away_pitcher_dic)
        home_team_dic = {'team_abbrev': teamAbbrev[gamethatday[i]['teams']['home']['team']['name']], 'team_id': gamethatday[i]['teams']['home']['team']['id'], 
                         'team_name': gamethatday[i]['teams']['home']['team']['name'], 'win': gamethatday[i]['teams']['home']['leagueRecord']['wins'], 
                         'loss': gamethatday[i]['teams']['home']['leagueRecord']['losses'], 'win_pct': gamethatday[i]['teams']['home']['leagueRecord']['pct']}
        away_team_dic = {'team_abbrev': teamAbbrev[gamethatday[i]['teams']['away']['team']['name']], 'team_id': gamethatday[i]['teams']['away']['team']['id'], 
                         'team_name': gamethatday[i]['teams']['away']['team']['name'], 'win': gamethatday[i]['teams']['away']['leagueRecord']['wins'],
                         'loss': gamethatday[i]['teams']['away']['leagueRecord']['losses'], 'win_pct': gamethatday[i]['teams']['away']['leagueRecord']['pct']}
        
        try:
            home_team_dic['score'] = gamethatday[i]['teams']['home']['score'] # if the game doesn't start, there is no score
        except:
            home_team_dic['score'] = 0
        try:
            away_team_dic['score'] = gamethatday[i]['teams']['away']['score']
        except:
            away_team_dic['score'] = 0

        home_team_dic.update(findTeamStats(home_team_dic['team_name'])) # update the team's batting stats
        away_team_dic.update(findTeamStats(away_team_dic['team_name']))

        try:
            obj_home_pitcher, created = Pitcher.objects.update_or_create(
                id=home_pitcher_dic['id'],
                defaults={
                    'fullName': home_pitcher_dic['fullName'],'IP': home_pitcher_dic['IP'],
                    'Win': home_pitcher_dic['Win'], 'Loss': home_pitcher_dic['Loss'], 'ERA': home_pitcher_dic['ERA'],
                    'xERA': home_pitcher_dic['xERA'], 'xFIPm': home_pitcher_dic['xFIPm']
                }
            )
        except:
            print('home pitcher not created',home_pitcher_dic)
        # if created:
        #     print(f'Created new record: {obj_home_pitcher}')
        # else:
        #     print(f'Updated existing record: {obj_home_pitcher}')
        try:
            obj_away_pitcher, created = Pitcher.objects.update_or_create(
                id=away_pitcher_dic['id'],
                defaults={ 'fullName': away_pitcher_dic['fullName'],'IP': away_pitcher_dic['IP'],
                    'Win': away_pitcher_dic['Win'], 'Loss': away_pitcher_dic['Loss'], 'ERA': away_pitcher_dic['ERA'],
                    'xERA': away_pitcher_dic['xERA'], 'xFIPm': away_pitcher_dic['xFIPm']
                }
            )
        except:
            print('away pitcher not created', away_pitcher_dic)
        # if created:
        #     print(f'Created new record: {obj_away_pitcher}')
        # else:
        #     print(f'Updated existing record: {obj_away_pitcher}')
        obj_away_team, created = Team.objects.update_or_create(
            id=away_team_dic['team_id'],
            defaults={'team_abbrev': away_team_dic['team_abbrev'], 'name': away_team_dic['team_name'],
                'wins': away_team_dic['win'], 'losses': away_team_dic['loss'], 'pct': away_team_dic['win_pct'],
                'OPS': away_team_dic['OPS'], 'wOBA': away_team_dic['wOBA'], 'wRCp': away_team_dic['wRCp']
            }
        )
        obj_home_team, created = Team.objects.update_or_create(
            id=home_team_dic['team_id'],
            defaults={'team_abbrev': home_team_dic['team_abbrev'], 'name': home_team_dic['team_name'],
                'wins': home_team_dic['win'], 'losses': home_team_dic['loss'], 'pct': home_team_dic['win_pct'],
                'OPS': home_team_dic['OPS'], 'wOBA': home_team_dic['wOBA'], 'wRCp': home_team_dic['wRCp']
            }
        )
        if home_pitcher_dic['id'] == -1:
            obj_home_pitcher = obj_tbd
        if away_pitcher_dic['id'] == -1:
            obj_away_pitcher = obj_tbd
        obj_game, created = Game.objects.update_or_create(
            game_id=gamethatday[i]['gamePk'],
            defaults={'game_date': gamethatday[i]['officialDate'],
                'away_pitcher_id': obj_away_pitcher, 'home_pitcher_id': obj_home_pitcher,
                'away_team_id': obj_away_team, 'home_team_id': obj_home_team,
                'home_team_score': home_team_dic['score'], 'away_team_score': away_team_dic['score'],
            }
        )
        
        # if created:
        #     print(f'Created new record: {obj}')
        # else:
        #     print(f'Updated existing record: {obj}')
    # print("in getdata: ",gamethatday)
    # print("test view")
    # return gamethatday