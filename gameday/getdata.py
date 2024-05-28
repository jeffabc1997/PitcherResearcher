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
    # statlist = []
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
        

        # customize the information we want to display on webpage
        # statlist.append({'Win': aPlayer['W'].values[0], 'Loss': aPlayer['L'].values[0], \
        #                      'IP': aPlayer['IP'].values[0], 'ERA': aPlayer['ERA'].values[0], \
        #                      'xFIPm': aPlayer['xFIP-'].values[0], 'xERA': aPlayer['xERA'].values[0]}) 

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
            id=-1,
            defaults={
                'fullName': 'TBD',
            }
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
        return {}
    gamethatday = schedule["dates"][0]["games"]
    # print(gamethatday)
    homeids = []
    awayids =[]

    for g in gamethatday: # get starting pitcher ID
        try:
            homeids.append(g['teams']['home']['probablePitcher']['id'])
            # print(g['teams']['home']['probablePitcher']['id'], g['teams']['home']['probablePitcher']['fullName'])
        except:
            print("home probablePitcher Key not found")
            homeids.append(-1)
        try:
            awayids.append(g['teams']['away']['probablePitcher']['id'])
            # print(g['teams']['away']['probablePitcher']['id'], g['teams']['away']['probablePitcher']['fullName'])
        except:
            print("away probablePitcher Key not found")
            awayids.append(-1)

    # homePitcherStats = findpitcher(homeids) # get a list of dictionaries
    # awayPitcherStats = findpitcher(awayids)

    for i in range(len(gamethatday)): # update data in gamethatday
        try:
            home_pitcher_dic = findpitcher(gamethatday[i]['teams']['home']['probablePitcher']['id'])
            home_pitcher_dic['id'] = gamethatday[i]['teams']['home']['probablePitcher']['id']
            home_pitcher_dic['fullName'] = gamethatday[i]['teams']['home']['probablePitcher']['fullName']
            print('home pitcher', home_pitcher_dic)
            gamethatday[i]['teams']['home']['probablePitcher'].update(home_pitcher_dic)
        except:
            # if can't find a pitcher, give it TBD
            gamethatday[i]['teams']['home']['probablePitcher'] = {'fullName' : 'TBD'} # STILL NEED TO CHECK
            home_pitcher_dic['id'] = -1
            home_pitcher_dic['fullName'] = 'TBD'
        try:
            
            away_pitcher_dic = findpitcher(gamethatday[i]['teams']['away']['probablePitcher']['id'])
            away_pitcher_dic['id'] = gamethatday[i]['teams']['away']['probablePitcher']['id']
            away_pitcher_dic['fullName'] = gamethatday[i]['teams']['away']['probablePitcher']['fullName']
            gamethatday[i]['teams']['away']['probablePitcher'].update(away_pitcher_dic) # update global dict
        except:
            gamethatday[i]['teams']['away']['probablePitcher'] = {'fullName' : 'TBD'} 
            away_pitcher_dic['id'] = -1
            away_pitcher_dic['fullName'] = 'TBD'
        home_team_dic = {'team_abbrev': teamAbbrev[gamethatday[i]['teams']['home']['team']['name']], 'team_id': gamethatday[i]['teams']['home']['team']['id'], 
                         'team_name': gamethatday[i]['teams']['home']['team']['name'], 'win': gamethatday[i]['teams']['home']['leagueRecord']['wins'], 
                         'loss': gamethatday[i]['teams']['home']['leagueRecord']['losses'], 'win_pct': gamethatday[i]['teams']['home']['leagueRecord']['pct']}
        away_team_dic = {'team_abbrev': teamAbbrev[gamethatday[i]['teams']['away']['team']['name']], 'team_id': gamethatday[i]['teams']['away']['team']['id'], 
                         'team_name': gamethatday[i]['teams']['away']['team']['name'], 'win': gamethatday[i]['teams']['away']['leagueRecord']['wins'],
                         'loss': gamethatday[i]['teams']['away']['leagueRecord']['losses'], 'win_pct': gamethatday[i]['teams']['away']['leagueRecord']['pct']}
        try:
            home_team_dic['score'] = gamethatday[i]['teams']['home']['score']
        except:
            home_team_dic['score'] = 0
        try:
            away_team_dic['score'] = gamethatday[i]['teams']['away']['score']
        except:
            away_team_dic['score'] = 0
        home_team_dic.update(findTeamStats(home_team_dic['team_name'])) # update the team's batting stats
        away_team_dic.update(findTeamStats(away_team_dic['team_name']))
        print('home team dic', home_team_dic)
        print('away team dic', away_team_dic)
        print('home pitcher dic', home_pitcher_dic)
        print('away pitcher dic', away_pitcher_dic)

        gamethatday[i]['teams']['home']['team_abbrev'] = teamAbbrev[gamethatday[i]['teams']['home']['team']['name']] # give a abbreviation name
        gamethatday[i]['teams']['away']['team_abbrev'] = teamAbbrev[gamethatday[i]['teams']['away']['team']['name']]

        gamethatday[i]['teams']['home'].update(findTeamStats(gamethatday[i]['teams']['home']['team']['name'])) # update the team's batting stats
        gamethatday[i]['teams']['away'].update(findTeamStats(gamethatday[i]['teams']['away']['team']['name']))

        # if(gamethatday[i]['teams']['away']['probablePitcher']['fullName'] == 'TBD'):
        #     gamethatday[i]['teams']['home']['probablePitcher']['id'] = -1
        # h_pitcher_id = gamethatday[i]['teams']['home']['probablePitcher']['id'] if gamethatday[i]['teams']['home']['probablePitcher']['fullName'] != 'TBD' else -1
        # a_pitcher_id = gamethatday[i]['teams']['away']['probablePitcher']['id'] if gamethatday[i]['teams']['away']['probablePitcher']['fullName'] != 'TBD' else -1
        # if(gamethatday[i]['teams']['home']['probablePitcher']['fullName'] == 'TBD'):
        #     gamethatday[i]['teams']['away']['probablePitcher']['id'] = -1
        try:
            obj_home_pitcher, created = Pitcher.objects.update_or_create(
                id=home_pitcher_dic['id'],
                defaults={
                    'fullName': home_pitcher_dic['fullName'],'IP': home_pitcher_dic['IP'],
                    'Win': home_pitcher_dic['Win'], 'Loss': home_pitcher_dic['Loss'], #'ERA': home_pitcher_dic['ERA'],
                    # 'xERA': home_pitcher_dic['xERA'], 'xFIPm': home_pitcher_dic['xFIPm']
                }
            )
        except:
            print('home not created',obj_home_pitcher)
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
            print('away not created', away_pitcher_dic)
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
    return gamethatday