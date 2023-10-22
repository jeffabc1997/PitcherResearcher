import statsapi
import pybaseball
from datetime import datetime, timezone, timedelta
import math
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

thisYear = 2023
baseballRefPitcher = pybaseball.pitching_stats_bref(2023)
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
        statDict['IP'] = brefPlayer['IP'] if not math.isnan(brefPlayer['IP']) else 0
        statDict['ERA'] = "{:.2f}".format(brefPlayer['ERA'])
        statDict['WHIP'] = "{:.2f}".format(brefPlayer['WHIP'])
        statDict['SO9'] = "{:.2f}".format(brefPlayer['SO9'])
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
            statDict['IP'] = aPlayer['IP']
            statDict['ERA'] = "{:.2f}".format(aPlayer['ERA'])
        statDict['xFIPm'] = aPlayer['xFIP-'] # beware that xFIP- is renamed to xFIPm
        statDict['xERA'] = aPlayer['xERA']
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
    battingdict['wOBA'] = "{:.3f}".format(battingdict['wOBA'])
    battingdict['OPS'] = "{:.3f}".format(battingdict['OPS'])
    return battingdict
# getting the year from the current date and time
def mlbgame():
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
            gamethatday[i]['teams']['home']['probablePitcher'].update(findpitcher(gamethatday[i]['teams']['home']['probablePitcher']['id']))
        except:
            # if can't find a pitcher, give it TBD
            gamethatday[i]['teams']['home']['probablePitcher'] = {'fullName' : 'TBD'} # STILL NEED TO CHECK

        try:
            gamethatday[i]['teams']['away']['probablePitcher'].update(findpitcher(gamethatday[i]['teams']['away']['probablePitcher']['id'])) # update global dict
        except:
            gamethatday[i]['teams']['away']['probablePitcher'] = {'fullName' : 'TBD'} 

        gamethatday[i]['teams']['home']['team_abbrev'] = teamAbbrev[gamethatday[i]['teams']['home']['team']['name']] # give a abbreviation name
        gamethatday[i]['teams']['away']['team_abbrev'] = teamAbbrev[gamethatday[i]['teams']['away']['team']['name']]

        gamethatday[i]['teams']['home'].update(findTeamStats(gamethatday[i]['teams']['home']['team']['name'])) # update the team's batting stats
        gamethatday[i]['teams']['away'].update(findTeamStats(gamethatday[i]['teams']['away']['team']['name']))
    print("in getdata: ",gamethatday)
    # print("test view")
    return gamethatday