import requests
from bs4 import BeautifulSoup
from itertools import cycle
import argparse
import io
import math

import pandas as pd
from pandas import DataFrame
from sklearn import linear_model
import statsmodels.api as sm
from sklearn.svm import SVR
import matplotlib.pyplot as plt
import numpy as np
import math
import sys


teamStats = []


def clean(stng):
    
    output = ''

    for letter in stng:
        if letter != '[' and letter != ']' and letter != "'": #and letter != ' ':
            output += letter
        
    return output


def convertNum(stng):

    try:
        return float(stng)
    except:
        return 0


def progress(count, total, status=''):
    
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()


def cleanString(stng):

    output = ''

    for letter in stng:
        if letter.isdigit() or letter == '.' or letter == '%' or letter == '-':
            output += letter
        
    if '%' not in output and len(output) > 0:
        return float(output)
    else:
        if '%' in output:
            return output
        else:
            return 0


def extractNums(stng):

    output = []

    while '>' in stng:
        
        stng = stng[stng.find('>') + 1 : ]

        num = stng[0 : stng.find('</')]

        if len(num) < 10:
            try:
                output.append(float(num))
            except:
                if num.isdigit():
                    output.append(float(num))
                elif ('%' in num or ',' in num):
                    output.append(cleanString(num))
            
    return output


def getProxies(inURL):
    
    page = requests.get(inURL)
    soup = BeautifulSoup(page.text, 'html.parser')
    terms = soup.find_all('tr')
    IPs = []

    for x in range(len(terms)):  
        
        term = str(terms[x])        
        
        if '<tr><td>' in str(terms[x]):
            pos1 = term.find('d>') + 2
            pos2 = term.find('</td>')

            pos3 = term.find('</td><td>') + 9
            pos4 = term.find('</td><td>US<')
            
            IP = term[pos1:pos2]
            port = term[pos3:pos4]
            
            if '.' in IP and len(port) < 6:
                IPs.append(IP + ":" + port)
                #print(IP + ":" + port)

    return IPs 


proxyURL = "https://www.us-proxy.org/"
pxs = getProxies(proxyURL)
proxyPool = cycle(pxs)


def getFinalsMatchups(year):

    finalsMatchup = []

    page = requests.get('https://www.basketball-reference.com/playoffs/NBA_' + str(year) + '.html', proxies = {"http": next(proxyPool)})
    soup = str(BeautifulSoup(page.text, 'html.parser'))

    rawMatchup = soup[soup.find('"tooltip opener" data-id="s') : soup.find('"tooltip opener" data-id="s') + 220]
    team1 = rawMatchup[rawMatchup.find('html">') + 6 : rawMatchup.find('</a>')]

    rawMatchup = rawMatchup[rawMatchup.find('over') + 10 : ]
    team2 = rawMatchup[rawMatchup.find('>') + 1 : rawMatchup.find('</')]

    score = rawMatchup[rawMatchup.find('(') + 1 : rawMatchup.find(')')]
    team1Win = score[0 : score.find('-')]
    team2Win = score[score.find('-') + 1 : ]

    team1Result = 0
    team2Result = 1

    if float(team1Win) == 4:
        team1Result = 1
        team2Result = 0

    finalsMatchup.append([team1, team1Result])
    finalsMatchup.append([team2, team2Result])
   
    return finalsMatchup


def getTeamStats(year, seasons):

    global teamStats
        
    teams = []

    progressCounter = 0
    yr = year


    print('Getting data from the ' + str(year) + '-' + str(year - seasons + 1) + ' NBA seasons...')

    for x in range(1, 31):
        
        page = requests.get('https://www.basketball-reference.com/leagues/NBA_' + str(yr) + '_standings.html', proxies = {"http": next(proxyPool)})
        soup = str(BeautifulSoup(page.text, 'html.parser'))

        indexTo = soup.find('data-stat="ranker" csk="' + str(x) + '"')
        
        rawTeamStats = soup[indexTo + 80 : indexTo + 1200]

        rawTeamSymbol = rawTeamStats[rawTeamStats.find('/teams') + 7 : rawTeamStats.find('/teams') + 15]
        teamSymbol = rawTeamSymbol[0 : rawTeamSymbol.find('/')]
        teamName = rawTeamStats[rawTeamStats.find('>') + 1 : rawTeamStats.find('</')]

        teams.append([teamName, teamSymbol])
        
        rawTeamRecord = rawTeamStats[rawTeamStats.find('csk="') + 10 : rawTeamStats.find('csk=') + 25]

        wins = convertNum(rawTeamRecord[rawTeamRecord.find('>') + 1 : rawTeamRecord.find('-')])
        losses = convertNum(rawTeamRecord[rawTeamRecord.find('-') + 1 : rawTeamRecord.find('</')])

        rawHomeWins = rawTeamStats[rawTeamStats.find('data-stat="Home"') + 25 : rawTeamStats.find('data-stat="Home"') + 50]
        homeWins = convertNum(rawHomeWins[rawHomeWins.find('>') + 1 : rawHomeWins.find('-')])
        homeLosses = convertNum(rawHomeWins[rawHomeWins.find('-') + 1 : rawHomeWins.find('</')])

        rawRoadWins = rawTeamStats[rawTeamStats.find('data-stat="Road"') + 25 : rawTeamStats.find('data-stat="Road"') + 50]
        roadWins = convertNum(rawRoadWins[rawRoadWins.find('>') + 1 : rawRoadWins.find('-')])
        roadLosses = convertNum(rawRoadWins[rawRoadWins.find('-') + 1 : rawRoadWins.find('</')])

        rawMarginVictory = rawTeamStats[rawTeamStats.find('data-stat="3"') + 20 : rawTeamStats.find('data-stat="3"') + 100] 
        margin3Victories = convertNum(rawMarginVictory[rawMarginVictory.find('>') + 1 : rawMarginVictory.find('-')])
        margin3Losses = convertNum(rawMarginVictory[rawMarginVictory.find('-') + 1 : rawMarginVictory.find('</')])

        rawMarginVictory = rawMarginVictory[rawMarginVictory.find('data-stat="10"') + 25 : ]
        margin10Victories = convertNum(rawMarginVictory[rawMarginVictory.find('>') + 1 : rawMarginVictory.find('-')])
        margin10Losses = convertNum(rawMarginVictory[rawMarginVictory.find('-') + 1 : rawMarginVictory.find('</')])


        page = requests.get('https://www.basketball-reference.com/teams/' + teamSymbol + '/' + str(yr) + '.html', proxies = {"http": next(proxyPool)})
        soup = str(BeautifulSoup(page.text, 'html.parser'))
        soup2 = BeautifulSoup(page.text, 'html.parser')
        
        results = list(soup2.find(id='all_team_and_opponent'))
        rawTeamStats = str(results[5][results[5].find('>Team/G<') : ])

        rawTeamStatsPerGame = rawTeamStats[70 : rawTeamStats.find('>Lg Rank<')]
        rawLeagueRanks = rawTeamStats[rawTeamStats.find('>Lg Rank<') + 50 : rawTeamStats.find('>Year/Year<')]
        
        rawOppPerGame = rawTeamStats[rawTeamStats.find('>Opponent/G<') + 50 : rawTeamStats.find('opp_pts_per_g"') + 50]
        rawOppLeagueRanks = rawTeamStats[rawTeamStats.find('>Opponent/G<') : rawTeamStats.find('>Opponent/G<') + 2500][1320 : ]

        rawTeamYoY = rawTeamStats[rawTeamStats.find('>Year/Year<') + 20 : rawTeamStats.find('>Year/Year<') + 1550]
        rawOppTeamYoY = rawTeamStats[rawTeamStats.find('>Opponent/G<') + 50 : rawTeamStats.find('>Opponent/G<') + 4550][2420 : ]

        teamStatsPerGame = extractNums(rawTeamStatsPerGame)
        leagueRanks = extractNums(rawLeagueRanks)

        oppStatsPerGame = extractNums(rawOppPerGame)
        oppLeagueRanks = extractNums(rawOppLeagueRanks)
    
        teamStatsYoY = extractNums(rawTeamYoY)
        oppTeamStatsYoY = extractNums(rawOppTeamYoY)

        teamMisc = list(soup2.find(id='all_team_misc'))
        rawTeamAdv = str(teamMisc[5][teamMisc[5].find('data-stat="mov" >') : teamMisc[5].find('>Lg Rank<')])
        rawTeamMiscLgRank = teamMisc[5][teamMisc[5].find('>Lg Rank<') : teamMisc[5].find('>Lg Rank<') + 2000]
        
        teamMiscStats = extractNums(rawTeamAdv)
        teamMiscLgRank = extractNums(rawTeamMiscLgRank)

        start = 1
        starterPts = 0
        benchPts = 0

        for y in range(20):
            
            try:
                benchPlayer = soup[soup.find('data-stat="ranker" csk="' + str(start) + '"') : soup.find('data-stat="ranker" csk="' + str(start + 1) + '"')]
                name = benchPlayer[benchPlayer.find('data-stat="player" csk="') + 24 : benchPlayer.find('" ><a href="/players')]
                ppg = cleanString(benchPlayer[benchPlayer.find('pts_per_g') + 10 : benchPlayer.find('pts_per_g') + 20])
                
                if start < 6:
                    starterPts += ppg
                else:
                    benchPts += ppg

                start += 1
            except:
                print('Error')
                break


        finalsMatchup = getFinalsMatchups(yr)
        reachedFinals = 0
        finalsWin = 0

        if teamName == finalsMatchup[0][0] or teamName == finalsMatchup[1][0]:
            reachedFinals = 1

            if teamName == finalsMatchup[0][0] and finalsMatchup[0][1] == 1:
                finalsWin = 1

            
        if len(teamName) < 30:
            teamStats.append([teamName, yr, wins, losses, homeWins, homeLosses, roadWins, roadLosses, margin3Victories,
            margin3Losses, margin10Victories, margin10Losses, starterPts, benchPts, teamStatsPerGame, leagueRanks, oppStatsPerGame, oppLeagueRanks, 
            teamStatsYoY, oppTeamStatsYoY, teamMiscStats, teamMiscLgRank, reachedFinals, finalsWin])

        
        print(teamName)
        print('\nTeam Stats / G', teamStatsPerGame)
        print('\nLeague Ranks', leagueRanks)
        print('\nOppo Stats / G', oppStatsPerGame)
        print('\nOppo League Ranks', oppLeagueRanks)
        print('\nTeam Stats YoY', teamStatsYoY)
        print('\nOppo Team Stats YoY', oppTeamStatsYoY)
        print('\nTeam Misc Stats', teamMiscStats)
        print('\nTeam Misc League Rank', teamMiscLgRank)
        print('\nReached Finals', reachedFinals)
        print('\nFinals Win', finalsWin)
        print('\n')
    

        progress(progressCounter, 30 * seasons, status='Loading...')
        progressCounter += 1    


    print('\nDone!')

    datasetName = 'NBADataset' + str(year) + '-' + str(year - seasons + 1) + 'Seasons'
    
    MyFile = open(saveTo + datasetName + '.csv','w')

    header = 'Team Name, Year, Wins, Losses, Home Wins, Home Losses, Road Wins, Road Losses, Margin <= 3 Victories, Margin <= 3 Losses,\
        Margin >= 10 Victories, Margin >= 10 Losses, Starter PPG, Bench PPG, MP/G, FG/G, FGA/G, FG%, 3P/G, 3PA/G, 3P%, 2P/G, 2PA/G, 2P%, FT/G, FTA/G, FT%, ORB/G, DRB/G,\
            TRB/G, AST/G, STL/G, BLK/G, TOV/G, PF/G, PTS/G, MP/G Rank, FG/G Rank, FGA/G Rank, FG% Rank, 3P/G Rank, 3PA/G Rank, 3P% Rank,\
                2P/G Rank, 2PA/G Rank, 2P% Rank, FT/G Rank, FTA/G Rank, FT% Rank, ORB/G Rank, DRB/G Rank, TRB/G Rank, AST/G Rank, STL/G Rank,\
                    BLK/G Rank, TOV/G Rank, PF/G Rank, PTS/G Rank, Oppo MP/G, Oppo FG/G, Oppo FGA/G, Oppo FG%, Oppo 3P/G, Oppo 3PA/G,\
                        Oppo 3P%, Oppo 2P/G, Oppo 2PA/G, Oppo FT/G, Oppo FTA/G, Oppo FT%, Oppo ORB/G, Oppo DRB/G, Oppo TRB/G, Oppo AST/G,\
                            Oppo STL/G, Oppo BLK/G, Oppo TOV/G, Oppo PF/G, Oppo PTS/G, Oppo MP/G Rank, Oppo FG/G Rank, Oppo FGA/G Rank,\
                                Oppo FG% Rank, Oppo 3P/G Rank, Oppo 3PA/G Rank, Oppo 3P% Rank, Oppo 2P/G Rank, Oppo 2PA/G Rank,\
                                    Oppo FT/G Rank, Oppo FTA/G Rank, Oppo FT% Rank, Oppo ORB/G Rank, Oppo DRB/G Rank, Oppo TRB/G Rank,\
                                        Oppo AST/G Rank, Oppo STL/G Rank, Oppo BLK/G Rank, Oppo TOV/G Rank, Oppo PF/G Rank, Oppo PTS/G Rank,\
                                            MP/G YoY, FG/G YoY, FGA/G YoY, FG% YoY, 3P/G YoY, 3PA/G YoY, 3P% YoY, 2P/G YoY, 2PA/G YoY,\
                                                FT/G YoY, FTA/G YoY, FT% YoY, ORB/G YoY, DRB/G YoY, TRB/G YoY, AST/G YoY, STL/G YoY,\
                                                    BLK/G YoY, TOV/G YoY, PF/G YoY, PTS/G YoY, Oppo MP/G YoY, Oppo FG/G YoY, Oppo FGA/G YoY,\
                                                        Oppo FG% YoY, Oppo 3P/G YoY, Oppo 3PA/G YoY, Oppo 3P% YoY, Oppo 2P/G YoY,\
                                                            Oppo 2PA/G YoY, Oppo FT/G YoY, Oppo FTA/G YoY, Oppo FT% YoY, Oppo ORB/G YoY,\
                                                                Oppo DRB/G YoY, Oppo TRB/G YoY, Oppo AST/G YoY, Oppo STL/G YoY,\
                                                                    Oppo BLK/G YoY, Oppo TOV/G YoY, Oppo PF/G YoY, Oppo PTS/G YoY,\
                                                                        Margin of Victory, Strength of Schedule, Simple Rating System,\
                                                                            Offensive Rating, Defensive Rating, Pace, FT AR, 3P AR, EFG%,\
                                                                                TOV%, ORB%, FT/FGA, Oppo EFG%, Oppo TOV%, Oppo DRB%,\
                                                                                    Oppo FT/FGA, Arena Attendance, Margin of Victory Rank, \
                                                                                        Strength of Schedule Rank, Simple Rating System Rank,\
                                                                                            Offensive Rating Rank, Defensive Rating Rank, Pace Rank,\
                                                                                                FT AR Rank, 3P AR Rank, EFG% Rank,\
                                                                                                    TOV% Rank, ORB% Rank, FT/FGA Rank, Oppo EFG% Rank, \
                                                                                                        Oppo TOV% Rank, Oppo DRB% Rank, Oppo FT/FGA Rank,\
                                                                                                            Arena Attendance Rank, Reached Finals,Finals Win' + '\n'

    MyFile.write(header.replace(' ', ''))

    for row in teamStats:
        MyFile.write(clean(str(row)))
        MyFile.write('\n')

    MyFile.close()

    print('\nSaved as ' + saveTo + datasetName + '.csv')



saveTo = 'C:\\Users\\faiza\\OneDrive\\Desktop\\NBAData\\'    

getTeamStats(2019, 1)