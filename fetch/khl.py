import requests
from bs4 import BeautifulSoup
import datetime
import urllib.parse as urlparse
import time
import utils.data as record
import pandas as pd


from globals import TEST_MODE
from fetch.common.sportzone import createSportZoneGame
from utils.data import RemoteStorageConnection
from utils.player import Suspension


def fetchKHLGames(team, seasons):
    page = None
    soup = None
    games = []

    if 'cache' in team:
        content_cache = team['cache']
        print('found cache')
        return team['cache']

    if not TEST_MODE:
        soups = []

        '''Handle one off tournament teams'''
        if 'season' in team:
            KHL_BASE_URL = "https://krakenhockeyleague.com/"
            URL = f'{KHL_BASE_URL}team/{team["id"]}/schedule/?season=' + \
                team['season']
            print(URL)
            page = requests.get(URL)
            if page.status_code != 200:
                print('ERROR: Could not retrieve website: ' +
                      str(page.reason) + ", " + str(page.status_code))
                return games
            soups.append(BeautifulSoup(page.content, "html.parser"))
        else:
            for season in seasons['khl']['current_seasons']:
                KHL_BASE_URL = "https://krakenhockeyleague.com/"
                URL = f'{KHL_BASE_URL}team/{team["id"]}/schedule/?season=' + str(
                    season)
                print(URL)
                page = requests.get(URL)
                if page.status_code != 200:
                    print('ERROR: Could not retrieve website: ' +
                          str(page.reason) + ", " + str(page.status_code))
                    return games
                soups.append(BeautifulSoup(page.content, "html.parser"))

        '''Update the logo_url

        - find the image in the KHL site
        - parse the url and encode any odd characters
        - replace the placeholder image in the teams object.'''
        image = soups[0].find('img', attrs={'class': 'float-left'})
        image_url = urlparse.quote(image['src'])
        team['logo_url'] = f"{KHL_BASE_URL}{image_url}"
        print(f"Updated logo_url to <{team['logo_url']}>")
    else:
        print("rate limited, opening sample file")
        with open("samples/sampleKHLHTML.txt", 'rb') as sample_file:
            content = sample_file.read()
            soup = BeautifulSoup(content, "html.parser")

    for soup in soups:
        tables = soup.find_all('table', attrs={
                               'class': 'display table table-striped border-bottom text-muted table-fixed'})
        for table in tables:
            table_body = table.find('tbody')
            rows = table_body.find_all('tr')

            for row in rows:
                cols = row.find_all('td')

                # khl uses sz backed website
                game = createSportZoneGame(cols, team, season)
                games.append(game)

        team['cache'] = games
#   While we are fetching all of the games, let's update player stats
    print(games)
    try:
        print("Entering Try")
        for game in games:
            if game.result:
                print(f"Processing score sheet for game ID: {game.game_id}")
                parse_score_sheet(game)
    except Exception as e:
        print(f"Failed to write game stats to DB: {e}")
    return games

def fetchKHLSuspensions(team_data):
    if TEST_MODE:
        return []

    suspensions = team_data['suspensions']['khl']

    all_suspensions = []
    base_URL = 'https://krakenhockeyleague.com/suspensions/?season='
    cache_found = False
    for season, value in suspensions.items():
        if 'cache' in value:
            all_suspensions += value['cache']
            cache_found = True
            continue

        season_suspensions = []
        URL = base_URL + str(season)
        print(URL)

        page = requests.get(URL)
        if page.status_code != 200:
            print('ERROR: Could not retrieve website: ' +
                  str(page.reason) + ", " + str(page.status_code))
            continue
        soup = BeautifulSoup(page.content, "html.parser")

        tables = soup.find_all('table', attrs={
                               'class': 'table border-bottom table-striped text-muted order-column table-responsive-md'})
        for table in tables:
            rows = table.find('tbody').find_all('tr')

            for row in rows:
                cols = row.find_all('td')

                sus_date = datetime.datetime.strptime(
                    cols[0].getText(), "%b %d, %Y")
                sus_name = cols[1].a.getText()
                sus_team = cols[2].a.getText()
                sus_div = cols[3].getText()
                sus_games = int(cols[4].getText())
                sus_id = cols[5].a.get('href').split('/')[2]
                sus_link = 'https://krakenhockeyleague.com/suspension-details/' + sus_id

                sus = Suspension(sus_date, sus_name, sus_team,
                                 sus_div, sus_games, sus_id)
                season_suspensions.append(sus)
        suspensions[season]['cache'] = season_suspensions
        all_suspensions += season_suspensions

        # In case we are loading a lot, don't want to overload
        time.sleep(1)

    if cache_found:
        print("cache found")

    return all_suspensions

def organize_data(tables):
    dfs = []
    for i, table in enumerate(tables):
        data = [[cell.get_text(strip=True) for cell in row.find_all(['th', 'td'])]
                for row in table.find_all('tr')]
        df = pd.DataFrame(data)
        df = df[1:]  # Skip the header row
        dfs.append(df)
    new_dfs = [dfs[2], dfs[3], dfs[6], dfs[21], dfs[22], dfs[25]]

    #Rosters
    rosters = [new_dfs[0][1:], new_dfs[3][1:]]
    for i in range(len(rosters)):
        roster = rosters[i]
        roster.columns = ["Jersey Number", "Name"]
        roster = roster[roster['Jersey Number'].notna() & (roster['Jersey Number'] != '')]
        rosters[i] = roster

    #Scoring
    scoring = [new_dfs[1], new_dfs[4]]
    for i in range(len(scoring)):
        scores = scoring[i].iloc[1:, 1:]
        scores = scores.drop(scores.columns[4], axis=1)
        scores.columns = ["Period", "Time of Goal", "Player Number", "Assist", "Second Assist", "Type"]
        scores = scores[scores['Period'].notna() & (scores['Period'] != '')]
        scores = scores[scores['Period'] != '.']
        scoring[i] = scores

    #Penalties
    penalties = [new_dfs[2], new_dfs[5]]
    for i in range(len(penalties)):
        penalty_scores = penalties[i].iloc[:, 1:]  # Remove the first row and first column
        penalty_scores.columns = ["Period", "Time", "Player", "Infraction", "Min"]  # Rename columns
        penalty_scores = penalty_scores[
            penalty_scores['Period'].notna() & (penalty_scores['Period'] != '')]  # Filter out empty periods
        penalty_scores = penalty_scores[penalty_scores['Period'] != '.']  # Remove rows with just a period
        penalties[i] = penalty_scores  # Update the penalties list with cleaned DataFrames

    return rosters, scoring, penalties

def write_game_stats(degens, scoresheet, home, game):
    for degen in degens:
        game_data = {}
        game_data['season_id'] = game.season_id
        game_data['id'] = game.game_id
        game_data['Team'] = game.team['name']
        game_data['Player'] = degen
        goals = 0
        goals += scoresheet[home]['Player Number'].eq(degens[degen]).sum()
        game_data['Goals'] = goals
        assists = 0
        assists += scoresheet[home]['Assist'].eq(degens[degen]).sum()
        game_data['Assists'] = assists
        secondassists = 0
        secondassists += scoresheet[home]['Second Assist'].eq(degens[degen]).sum()
        game_data['Secondary Assists'] = secondassists
        db_conn = RemoteStorageConnection()
        db_conn.write_player_game_stats(game_data)

def parse_score_sheet(game):
    games = []
    scoring = []
    if not TEST_MODE:
        soups = []
        rosters = []
        URL = game.score_sheet
        page = requests.get(URL)
        if page.status_code != 200:
            print('ERROR: Could not retrieve website: ' +
                  str(page.reason) + ", " + str(page.status_code))
            return games
        soups.append(BeautifulSoup(page.content, "html.parser"))
        #Get all of the tables from the KHL ScoreSheet
        for soup in soups:
            tables = soup.find_all('table', attrs={'cellspacing': 0})
            #placeholder for dataframes down the road
            rosters, scoring, penalties = organize_data(tables)
    degens = {}
    home = 0
    for degen in game.team['players']:
        for i, roster in enumerate(rosters):
            matches = roster[roster['Name'].str.contains(degen, case=False)]
            if not matches.empty:
                for _, row in matches.iterrows():
                    jersey_number = row['Jersey Number']
                    degens[degen] = jersey_number
                if i != 0:
                    home = 1
    print(f"Writing game {game.score_sheet} NOW")
    write_game_stats(degens, scoring, home, game)

    print(degens)




    return games

