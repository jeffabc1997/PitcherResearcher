import statsapi
import pybaseball
from datetime import datetime, timezone, timedelta

# Should put this function else where
# Add abbreviation name for teams
teamAbbrev = {'Arizona Diamondbacks': 'ARI', 'Chicago Cubs': 'CHC', 'St. Louis Cardinals': 'STL', 'Cincinnati Reds': 'CIN', 'Seattle Mariners': 'SEA', 'Tampa Bay Rays': 'TB', 'Chicago White Sox': 'CWS', 'Detroit Tigers': 'DET', 'Los Angeles Dodgers': 'LAD', 'Washington Nationals': 'WSH',\
           'Miami Marlins': 'MIA', 'Philadelphia Phillies': 'PHI', 'Milwaukee Brewers': 'MIL', 'New York Yankees': 'NYY', 'Kansas City Royals': 'KC', 'Toronto Blue Jays': 'TOR', 'Baltimore Orioles': 'BAL', 'Boston Red Sox': 'BOS', \
           'Pittsburgh Pirates': 'PIT', 'Atlanta Braves': 'ATL', 'Oakland Athletics': 'OAK', 'Texas Rangers': 'TEX', 'San Diego Padres': 'SD', 'Houston Astros': 'HOU', 'New York Mets': 'NYM', 'Minnesota Twins': 'MIN', 'Cleveland Guardians': 'CLE', 'Los Angeles Angels': 'LAA',\
           'Colorado Rockies': 'COL', 'San Francisco Giants': 'SF'}

def findpitcher(mlbids):
    statlist = []
    df = pybaseball.pitching_stats(2023, qual = 1) # all pitching stats
    # put only 1 player in this function for the right order
    for mid in mlbids:
        key = pybaseball.playerid_reverse_lookup([mid], key_type='mlbam')
        try:
            fgid = key['key_fangraphs'].values[0] # fangraphs ID
        except:
            print(f"MLB player ID {mid} not found.")
            statlist.append({})
            continue
        aPlayer = df.loc[df['IDfg'] == fgid]
        if aPlayer.empty:
            print(f"fgID: {fgid}, not a qualified pitcher.")
            statlist.append({})
            continue
        else: # customize the information we want to display on webpage
            statlist.append({'Win': aPlayer['W'].values[0], 'Loss': aPlayer['L'].values[0], 'IP': aPlayer['IP'].values[0], 'ERA': aPlayer['ERA'].values[0],'xFIP-': aPlayer['xFIP-'].values[0], 'xERA': aPlayer['xERA'].values[0]})

    return statlist
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

homestats = findpitcher(homeids) # get a list of dictionaries
awaystats = findpitcher(awayids)

for i in range(len(homestats)): # update data in gamethatday
    gamethatday[i]['teams']['home']['probablePitcher'].update(homestats[i])
    gamethatday[i]['teams']['away']['probablePitcher'].update(awaystats[i]) # update global dict
    
    gamethatday[i]['teams']['home']['team_abbrev'] = teamAbbrev[gamethatday[i]['teams']['home']['team']['name']] # give a abbreviation name
    gamethatday[i]['teams']['away']['team_abbrev'] = teamAbbrev[gamethatday[i]['teams']['away']['team']['name']]

# print(gamethatday)