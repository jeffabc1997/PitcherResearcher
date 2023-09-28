import statsapi
import pybaseball
from datetime import datetime, timezone, timedelta

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
def findpitcher(mlbids):
    statlist = []
    global allPitcherStats
    # df = pybaseball.pitching_stats(2023, qual = 1) # all pitching stats
    # put only 1 player in this function for the right order
    for mid in mlbids:
        key = pybaseball.playerid_reverse_lookup([mid], key_type='mlbam')
        statDict = {}
        brefPlayer = baseballRefPitcher.loc[baseballRefPitcher['mlbID'] == mid].to_dict('record')[0]
        statDict['Win'] = int(brefPlayer['W'])
        statDict['Loss'] = int(brefPlayer['L'])
        statDict['IP'] = brefPlayer['IP']
        statDict['ERA'] = brefPlayer['ERA']
        statDict['WHIP'] = brefPlayer['WHIP']
        statDict['SO9'] = brefPlayer['SO9']
        try:
            fgid = key['key_fangraphs'].values[0] # fangraphs ID
        except:
            print(f"MLB player ID {mid} not found.")
            statlist.append({})
            continue
        aPlayer = allPitcherStats.loc[allPitcherStats['IDfg'] == fgid]
        
        if aPlayer.empty:
            print(f"fgID: {fgid}, not a qualified pitcher.")
            statlist.append({})
            continue
        else: # customize the information we want to display on webpage
            statlist.append({'Win': aPlayer['W'].values[0], 'Loss': aPlayer['L'].values[0], \
                             'IP': aPlayer['IP'].values[0], 'ERA': aPlayer['ERA'].values[0], \
                             'xFIPm': aPlayer['xFIP-'].values[0], 'xERA': aPlayer['xERA'].values[0]}) # beware that xFIP- is renamed to xFIPm

    return statlist
def findTeamStats(name):
    global allTeamBatStats, teamtoFgId
    battingOfTeam = allTeamBatStats.loc[allTeamBatStats['teamIDfg'] == teamtoFgId[name], ["OPS", "wOBA", "wRC+"]]
    battingOfTeam = battingOfTeam.rename(columns={'wRC+': 'wRCp'}) # html can't parse '+'
    return battingOfTeam.to_dict('records')[0]
# getting the year from the current date and time
current_datetime = datetime.now(timezone.utc) - timedelta(hours=8) # Time zone: western time in US
date = current_datetime.strftime("%m/%d/%Y")
params = {
    "sportId": 1,
    "date": date,
    "hydrate": "probablePitcher(note)",
}
schedule = statsapi.get("schedule", params)
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

homePitcherStats = findpitcher(homeids) # get a list of dictionaries
awayPitcherStats = findpitcher(awayids)

for i in range(len(homePitcherStats)): # update data in gamethatday
    try:
        gamethatday[i]['teams']['home']['probablePitcher'].update(homePitcherStats[i])
    except:
        # if can't find a pitcher, give it TBD
        gamethatday[i]['teams']['home']['probablePitcher'] = {'fullName' : 'TBD'} # STILL NEED TO CHECK

    try:
        gamethatday[i]['teams']['away']['probablePitcher'].update(awayPitcherStats[i]) # update global dict
    except:
        gamethatday[i]['teams']['away']['probablePitcher'] = {'fullName' : 'TBD'} 

    gamethatday[i]['teams']['home']['team_abbrev'] = teamAbbrev[gamethatday[i]['teams']['home']['team']['name']] # give a abbreviation name
    gamethatday[i]['teams']['away']['team_abbrev'] = teamAbbrev[gamethatday[i]['teams']['away']['team']['name']]

    gamethatday[i]['teams']['home'].update(findTeamStats(gamethatday[i]['teams']['home']['team']['name'])) # update the team's batting stats
    gamethatday[i]['teams']['away'].update(findTeamStats(gamethatday[i]['teams']['away']['team']['name']))
# print(gamethatday)