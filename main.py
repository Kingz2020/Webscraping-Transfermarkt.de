import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time


def create_prime_soup(year, page, headers, path):
    '''Creates and stores the primal soup for a particular year.'''
    url = page + str(year)
    tree = requests.get(url, headers=headers)
    soup = BeautifulSoup(tree.content, 'html.parser')
    with open(path + 'prime_page_' + str(year) + '.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))
    return print(f'prime_page ' + str(year) + " created")


def store_prime_soup(begin_year, end_year, page, headers, path):
    """ Store the primal soup for a range of years ( begin year to end year inclusive)."""
    x = [i for i in range(begin_year, end_year+1)]
    for i in range(len(x)):
        create_prime_soup(x[i], page, headers, path)
    return print(f'prime pages all years from ' + str(begin_year) + ' to ' + str(end_year) + ' stored')


def get_soup(year, path):
    inh = open(path + 'prime_page_' + str(year) + '.html').read()
    soup = BeautifulSoup(inh)
    return soup


def create_teamlinks(teams_soup):
    '''
    creates the teamlinks
    location that the link is pointing to is needed 
    only need the links in locations 1,3,5, etc.
    '''
    teamLinks = []
    # Extracts all links with the correct CSS selector
    links = teams_soup.select("a.vereinprofil_tooltip")
    for i in range(1, 36, 2):
        teamLinks.append(links[i].get("href"))
    for i in range(len(teamLinks)):
        teamLinks[i] = "https://www.transfermarkt.de"+teamLinks[i]
    return teamLinks


def create_playerlinks(squadlinks):
    '''
    creates the playerlinks of all teams in the league needed to retrieve the players attributes.
    '''
    players = []
    #number_of_teams = len(squadlinks)
    for i in range(len(squadlinks)):
        page = squadlinks[i]
        # print(i,page)
        squadplayers = requests.get(page, headers=headers)
        time.sleep(0.2)
        soup = BeautifulSoup(squadplayers.content, 'html.parser')
        links = soup.select("a.spielprofil_tooltip")
        playerLinks = []
        #links = soup.select("a.spielprofil_tooltip")
        # For each link, extract the location that it is pointing to
        for j in range(len(links)):
            playerLinks.append(links[j].get("href"))
        # Add the location to the end of the transfermarkt domain to make it ready to scrape
        for j in range(len(playerLinks)):
            playerLinks[j] = "https://www.transfermarkt.de"+playerLinks[j]
        playerLinks = list(set(playerLinks))
        players.extend(playerLinks)
    return players


def write_file(lst, year, path):
    """"""
    with open(path + str(year) + '_' + 'players.txt', 'w') as filehandle:
        filehandle.writelines("%s\n" % players for players in lst)
    return print(str(year) + " done")


def write_players_of_year(begin_year, end_year, source_path, dest_path):
    """creates and stores the players of the years(begin year to end_year) """
    for i in range(begin_year, end_year+1):
        print(i)
        teamlinks = create_teamlinks(get_soup(i, source_path))
        squadlinks = create_squadlinks(teamlinks)
        players = create_playerlinks(squadlinks)
        write_file(players, i, dest_path)
    return print("writing all players of the years - done")


def create_squadlinks(teamlinks):
    '''Create the squadlinks with the teamlinks.'''
    squadlinks = []
    # Run the scraper through each of our 20 team links
    for i in range(len(teamlinks)):
        pos = teamlinks[i].find('spielplan')
        squadlinks.append(teamlinks[i][0:pos] + 'kader'+teamlinks[i][pos+9:])
    return squadlinks


def get_player_from_file(year, path):
    """Retrieves the player file from the XXXX_players where XXXX is the year"""
    player_lst = []
    with open(path + str(year) + '_' + 'players.txt', 'r') as filehandle:
        for line in filehandle.readlines():
            player_lst.append(line.strip('\n'))
            print(line)
    return player_lst


def store_players(players, year, player_path, headers):
    '''Store player data into path'''
    counter = 0
    for player in players:
        page = player
        pos = player.rfind('/')
        id = players[counter][pos+1:]
        pos_name = player.find('t.de/')+5
        pos_name_end = player.find('/profil')
        name = player[pos_name:pos_name_end]
        play = requests.get(page, headers=headers)
        time.sleep(0.2)
        soup_player = BeautifulSoup(play.content, 'html.parser')
        pos = player.rfind('/')
        id = players[counter][pos+1:]
        print(id)
        counter += 1
        with open(f'new_data/html/players/' + str(year) + '/player_' + name + '_' + id.strip('\n') + '.html', 'w', encoding='utf-8') as f:
            f.write(str(soup_player))
    print(f'players of {year} stored successfully')


def store_all_years(begin, end, path):
    """Stores all the players in their years"""
    for i in range(begin, end + 1):
        players = get_player_from_file(i, path)
        store_players(players, i, path, headers)
    return print("all years done")


def store_profile(year, source_path, dest_path):
    """Goes through all the player files in source_path,
    stores the id,name, and position of each one into the dataset, and
    saves dataset in dest_path"""
    source_path = source_path+str(year)+'/'
    df_id = pd.DataFrame(columns=['id', 'name', 'position'])
    for fn in os.listdir(source_path):
        #pos = fn.find('player_')
        pos_end = fn.rfind('_')
        name = fn[7:pos_end]
        id = fn[pos_end+1:-5]
        print(source_path+fn)
        with open(source_path+fn, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        Players = soup.find_all("div", {"class": "dataDaten"})
        try:
            soup_dataDaten = Players[1]
            soup_position = soup_dataDaten.find_all('p')
            soup_pos = soup_position[1]
            soup_ps = soup_pos.find_all('span', {"class": "dataValue"})
            position = str(soup_ps[0].get_text().strip())
            df_id = df_id.append({'id': id, 'name': name, 'position': position
                                  }, ignore_index=True)
        except Exception as e:
            print(e, id, name)
    df_id.to_csv(dest_path + 'profile__' + str(year) + '.csv')
    return print(f'profile_'+str(year) + ' stored in destination path')


def store_profile_all_years(beg_year, end_year, source_path, dest_path):
    """Stores profiles of all years"""
    for i in range(beg_year, end_year+1):
        store_profile(i, source_path, dest_path)
    return print('all profiles stored')


def store_stats(year, source_path, stats_path):
    ''' Get all in the stats.'''
    df_stats = pd.DataFrame(
        columns=['date', 'name', 'goals', 'pps_score', 'assists'])
    source_path = source_path+str(year)+'/'
    for fn in os.listdir(source_path):
        pos = fn.rfind('_')
        name = fn[7:pos]
        print(source_path, fn)
        inh = open(source_path + fn).read()
        player_goals = BeautifulSoup(inh)
        Players_gols = player_goals.find_all("div", {"class": "grid-view"})
        try:
            gols = Players_gols[0]
            g = gols.find_all('tr')
            h = g[1]
            h = h.find_all('td', {'class': 'zentriert'})
            #h0 = h[0]
            #nr_games_played = h0.get_text()
            h1 = h[1]
            pps_score = h1.get_text()
            h2 = h[2]
            nr_goals = h2.get_text()
            h3 = h[3]
            nr_assists = h3.get_text()
            print(nr_assists)
        except Exception as e:
            print(e)
            #nr_games_played = 0
            pps_score = 0
            nr_goals = 0
            nr_assists = 0
            # continue
        df_stats = df_stats.append({'date': year,
                                    'name': name,
                                    'goals': nr_goals,
                                    'pps_score': pps_score,
                                    'assists': nr_assists}, ignore_index=True)
    df_stats.to_csv(stats_path+'stats_'+str(year)+'.csv')
    print(f'stats for {year} stored successfully')


def store_all_stats(begin_year, end_year, dest_path, stats_path):
    """Stores all stats from begin_year to end year in the stats_path"""
    for year in range(begin_year, end_year+1):
        store_stats(year, dest_path, stats_path)
    return print(" all stats stored in their years")


main_path = 'new_data/html/'
store_prime_path = main_path + 'prime pages/'
players_years_path = main_path + 'players-years/'
source_path = 'new_data/html/prime pages/'
dest_path = 'new_data/html/players/'
profile_path = 'new_data/html/profiles/'
stats_path = 'new_data/html/stats/'
chart_path = 'new_data/html/charts/'


def store_chart_info(year, player_source_path, dest_path):
    ''' create a chart-info table for the players in year X.'''
    player_source_path = player_source_path + str(year)+'/'
    dest_path = dest_path + str(year)+'/'
    for fn in os.listdir(player_source_path):
        name = fn[7:fn.rfind('_')]
        id = fn[fn.rfind('_')+1:-5]
        compl_name = 'chart_mv_' + name + '_' + id + '.html'
        if compl_name in os.listdir(dest_path):
            print(f'{id} exists already')
            # continue
        else:
            name = fn[7:fn.rfind('_')]
            id = fn[fn.rfind('_')+1:-5]
            page = 'https://www.transfermarkt.co.uk/' + \
                name + '/marktwertverlauf/spieler/' + id
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:63.0) Gecko/20100101 Firefox/63.0'}
            market_value = requests.get(page, headers=headers)
            time.sleep(0.2)
            soup_mv = BeautifulSoup(market_value.content, 'html.parser')
            print(name)
            with open(dest_path + '/chart_mv_' + name + '_' + id + '.html', 'w', encoding='utf-8') as f:
                f.write(str(soup_mv))
    print(f'############ {year} charts stored succesfully! #############')


def store_all_charts(begin_year, end_year, dest_path, chart_path):
    """Stores all stats from begin_year to end year in the stats_path"""
    for year in range(begin_year, end_year+1):
        store_chart_info(year, dest_path, chart_path)
    return print(" all charts stored in their years")


page = 'https://www.transfermarkt.de/1-bundesliga/tabelle/wettbewerb/L1?saison_id='
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:63.0) Gecko/20100101 Firefox/63.0'}

# creates the primal soup
store_prime_soup(2010, 2010, page, headers, store_prime_path)

# creates the XXXX_player file from the primal soup
write_players_of_year(2010, 2010, source_path, players_years_path)

# stores all the data for each player in their file.
store_all_years(20105, 2020, players_years_path)

# stores the profile csv of all players in the year in the profile path
store_profile_all_years(2010, 2020, dest_path, profile_path)

# stores all the stats from begin year to end year of players in a csv file in the given path
store_all_stats(2010, 2020, dest_path, stats_path)

# stores all the chart info from begin year to end year of players from dest_path to the chart_path
store_all_charts(2010, 2020, dest_path, chart_path)
