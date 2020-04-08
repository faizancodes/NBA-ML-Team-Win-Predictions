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


def progress(count, total, status=''):
    
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()


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

    for y in range(seasons):

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

            wins = rawTeamRecord[rawTeamRecord.find('>') + 1 : rawTeamRecord.find('-')]
            losses = rawTeamRecord[rawTeamRecord.find('-') + 1 : rawTeamRecord.find('</')]

            rawHomeWins = rawTeamStats[rawTeamStats.find('data-stat="Home"') + 25 : rawTeamStats.find('data-stat="Home"') + 50]
            homeWins = rawHomeWins[rawHomeWins.find('>') + 1 : rawHomeWins.find('-')]
            homeLosses = rawHomeWins[rawHomeWins.find('-') + 1 : rawHomeWins.find('</')]

            rawRoadWins = rawTeamStats[rawTeamStats.find('data-stat="Road"') + 25 : rawTeamStats.find('data-stat="Road"') + 50]
            roadWins = rawRoadWins[rawRoadWins.find('>') + 1 : rawRoadWins.find('-')]
            roadLosses = rawRoadWins[rawRoadWins.find('-') + 1 : rawRoadWins.find('</')]

            rawMarginVictory = rawTeamStats[rawTeamStats.find('data-stat="3"') + 20 : rawTeamStats.find('data-stat="3"') + 100] 
            margin3Victories = rawMarginVictory[rawMarginVictory.find('>') + 1 : rawMarginVictory.find('-')]
            margin3Losses = rawMarginVictory[rawMarginVictory.find('-') + 1 : rawMarginVictory.find('</')]

            rawMarginVictory = rawMarginVictory[rawMarginVictory.find('data-stat="10"') + 25 : ]
            margin10Victories = rawMarginVictory[rawMarginVictory.find('>') + 1 : rawMarginVictory.find('-')]
            margin10Losses = rawMarginVictory[rawMarginVictory.find('-') + 1 : rawMarginVictory.find('</')]


            #print(teamName)
            page = requests.get('https://www.basketball-reference.com/teams/' + teamSymbol + '/' + str(yr) + '.html', proxies = {"http": next(proxyPool)})
            soup = str(BeautifulSoup(page.text, 'html.parser'))

            #Points / Game
            rawPts = soup[soup.find('data-stat="pts_per_g" >') + 15 : soup.find('data-stat="pts_per_g" >') + 30]
            ptsPerGame = rawPts[rawPts.find('>') + 1 : rawPts.find('<')]
            #print('Points / Game', ptsPerGame)

            #Offensive Rating
            rawOffRating = soup[soup.find('data-stat="off_rtg" >') + 16 : soup.find('data-stat="off_rtg" >') + 27]
            offRating = rawOffRating[rawOffRating.find('>') + 1 : rawOffRating.find('<')]  
            #print('Off Rating', offRating)

            #Defensive Rating
            rawDefRating = soup[soup.find('data-stat="def_rtg" >') + 16 : soup.find('data-stat="def_rtg" >') + 27]
            defRating = rawDefRating[rawDefRating.find('>') + 1 : rawDefRating.find('<')]
            #print('Def Rating', defRating)

            #Pace
            rawPace = soup[soup.find('data-stat="pace" >') + 16 : soup.find('data-stat="pace" >') + 27]
            pace = rawPace[rawPace.find('>') + 1 : rawPace.find('<')]
            #print('Pace', pace)

            #FG%
            rawFgPCT = soup[soup.find('data-stat="fg_pct" >') + 18 : soup.find('data-stat="fg_pct" >') + 25]
            fgPCT = rawFgPCT[rawFgPCT.find('>') + 1 : rawFgPCT.find('<')]
            #print('FG%', fgPCT)

            #3P%
            raw3PCT = soup[soup.find('data-stat="fg3_pct" >') + 16 : soup.find('data-stat="fg3_pct" >') + 27]
            fg3PCT = raw3PCT[raw3PCT.find('>') + 1 : raw3PCT.find('<')]
            #print('3P%', fg3PCT)

            #FT%
            rawFTPCT = soup[soup.find('data-stat="ft_pct" >') + 16 : soup.find('data-stat="ft_pct" >') + 27]
            ftPCT = rawFTPCT[rawFTPCT.find('>') + 1 : rawFTPCT.find('<')]
            #print('FT%', ftPCT)

            #Offensive Rebounds / Game
            rawORB = soup[soup.find('data-stat="orb_per_g" >') + 10 : soup.find('data-stat="orb_per_g" >') + 30]
            orbPerGame = rawORB[rawORB.find('>') + 1 : rawORB.find('<')]
            #print('Offensive Rebounds / Game', orbPerGame)

            #Defensive Rebounds / Game
            rawDRB = soup[soup.find('data-stat="drb_per_g" >') + 10 : soup.find('data-stat="drb_per_g" >') + 30]
            drbPerGame = rawDRB[rawDRB.find('>') + 1 : rawDRB.find('<')]
            #print('Defensive Rebounds / Game', drbPerGame)

            #Assists / Game
            rawAstPG = soup[soup.find('data-stat="ast_per_g" >') + 15 : soup.find('data-stat="ast_per_g" >') + 30]
            astPerGame = rawAstPG[rawAstPG.find('>') + 1 : rawAstPG.find('<')]
            #print('Assists / Game', astPerGame)

            #Steals / Game
            rawStl = soup[soup.find('data-stat="stl_per_g" >') + 15 : soup.find('data-stat="stl_per_g" >') + 30]
            stlPerGame = rawStl[rawStl.find('>') + 1 : rawStl.find('<')]
            #print('Steals / Game', stlPerGame)

            #Blocks / Game
            rawBlk = soup[soup.find('data-stat="blk_per_g" >') + 15 : soup.find('data-stat="blk_per_g" >') + 30]
            blkPerGame = rawBlk[rawBlk.find('>') + 1 : rawBlk.find('<')]
            #print('Blocks / Game', blkPerGame)

            #Turnovers / Game
            rawTO = soup[soup.find('data-stat="tov_per_g" >') + 15 : soup.find('data-stat="tov_per_g" >') + 30]
            toPerGame = rawTO[rawTO.find('>') + 1 : rawTO.find('<')]
            #print('Turnovers / Game', toPerGame)

            #Fouls / Game
            rawF = soup[soup.find('data-stat="pf_per_g" >') + 15 : soup.find('data-stat="pf_per_g" >') + 30]
            foulsPerGame = rawF[rawF.find('>') + 1 : rawF.find('<')]
            #print('Fouls / Game', foulsPerGame)

            finalsMatchup = getFinalsMatchups(yr)
            reachedFinals = 0
            finalsWin = 0

            if teamName == finalsMatchup[0][0] or teamName == finalsMatchup[1][0]:
                reachedFinals = 1

                if teamName == finalsMatchup[0][0] and finalsMatchup[0][1] == 1:
                    finalsWin = 1
                
            if len(teamName) < 20:
                teamStats.append([teamName, yr, wins, losses, homeWins, homeLosses, roadWins, roadLosses, margin3Victories, margin3Losses, margin10Victories, margin10Losses, ptsPerGame, offRating, defRating, pace, fgPCT, fg3PCT, ftPCT, orbPerGame, drbPerGame, astPerGame, stlPerGame, blkPerGame, toPerGame, foulsPerGame, reachedFinals, finalsWin])

            progress(progressCounter, 30 * seasons, status='Loading...')
            progressCounter += 1    

        yr -= 1


    print('\nDone!')

    datasetName = 'NBADataset' + str(year) + '-' + str(year - seasons + 1) + 'Seasons'
    
    MyFile = open(saveTo + datasetName + '.csv','w')

    header = 'Team Name,Year,Wins,Losses,Home Wins,Home Losses,Road Wins,Road Losses,Margin <= 3 Victories,Margin <= Losses,Margin >= 10 Victories,Margin >= Losses,PPG,Off Rating,Def Rating,Pace,FG%,FG3%,FT%,Off RBG,Def RBG,Assists / Game,Steals / Game,Blocks / Game,Turnovers / Game,Fouls / Game,Reached Finals,Finals Win' + '\n'

    MyFile.write(header)

    for row in teamStats:
        MyFile.write(clean(str(row)))
        MyFile.write('\n')

    MyFile.close()

    print('\nSaved as ' + saveTo + datasetName + '.csv')



saveTo = 'C:\\Users\\faiza\\OneDrive\\Desktop\\NBAData\\'


getTeamStats(2019, 40)


for x in range(len(teamStats)):
    print(teamStats[x])
    print()

