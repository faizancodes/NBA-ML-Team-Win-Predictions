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


teamWinsByYear = []
teams = []
overallTeamStats = []
covTeamStats = []
header = ''


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


def getTeamNames(year):

    global teamWinsByYear
    global teams
        
    page = requests.get('https://www.espn.com/nba/standings/_/season/' + str(year) + '/group/league', proxies = {"http": next(proxyPool)})
    soup = str(BeautifulSoup(page.text, 'html.parser'))

    for x in range(30):
        
        rawTeamName = soup[soup.find('data-idx="' + str(x) + '">') + 190 : soup.find('data-idx="' + str(x) + '">') + 500]
        teamName = rawTeamName[rawTeamName.find('<img alt=') + 10 : rawTeamName.find('" class="aspect-ratio')]

        teamSymbol = rawTeamName[rawTeamName.find('/name/') + 6 : rawTeamName.find('/name/') + 9].upper()

        if teamSymbol == 'GS/':
            teamSymbol = 'GSW'

        if teamSymbol == 'NO/':
            teamSymbol = 'NOP'

        if teamSymbol == 'SA/':
            teamSymbol = 'SAS'

        if teamSymbol == 'NY/':
            teamSymbol = 'NYK'

        if teamSymbol == 'BKN':
            teamSymbol = 'BRK'

        if teamSymbol == 'WSH':
            teamSymbol = 'WAS'

        if teamSymbol == 'CHA':
            teamSymbol = 'CHO'

        if teamSymbol == 'PHX':
            teamSymbol = 'PHO'


        teams.append([teamName, teamSymbol])


def generateDataset(year, seasons, datasetName):

    global teams
    global overallTeamStats
    global covTeamStats
    global header

    overallTeamStats = []
    progressCounter = 0

    for x in range(len(teams)):

        yr = year

        for y in range(seasons):
        
            page = requests.get('https://www.basketball-reference.com/teams/' + teams[x][1] + '/' + str(yr) + '.html', proxies = {"http": next(proxyPool)})
            soup = str(BeautifulSoup(page.text, 'html.parser'))

            rawTeamName = teams[x][0]
            teamName = rawTeamName[0 : rawTeamName.find('"')]
            #print(teamName, yr) 

            try:

                #Wins
                rawWins = soup[soup.find('data-stat="wins" >') + 15 : soup.find('data-stat="wins" >') + 30]
                wins = float(rawWins[rawWins.find('>') + 1 : rawWins.find('<')])
                #print('Wins', wins)

                #Losses
                rawLosses = soup[soup.find('data-stat="losses" >') + 15 : soup.find('data-stat="losses" >') + 30]
                losses = float(rawLosses[rawLosses.find('>') + 1 : rawLosses.find('<')])
                #print('Losses', losses)

                #Points / Game
                rawPts = soup[soup.find('data-stat="pts_per_g" >') + 15 : soup.find('data-stat="pts_per_g" >') + 30]
                ptsPerGame = float(rawPts[rawPts.find('>') + 1 : rawPts.find('<')])
                #print('Points / Game', ptsPerGame)

                #Offensive Rating
                rawOffRating = soup[soup.find('data-stat="off_rtg" >') + 16 : soup.find('data-stat="off_rtg" >') + 27]
                offRating = float(rawOffRating[rawOffRating.find('>') + 1 : rawOffRating.find('<')])   
                #print('Off Rating', offRating)

                #Defensive Rating
                rawDefRating = soup[soup.find('data-stat="def_rtg" >') + 16 : soup.find('data-stat="def_rtg" >') + 27]
                defRating = float(rawDefRating[rawDefRating.find('>') + 1 : rawDefRating.find('<')])   
                #print('Def Rating', defRating)

                #Pace
                rawPace = soup[soup.find('data-stat="pace" >') + 16 : soup.find('data-stat="pace" >') + 27]
                pace = float(rawPace[rawPace.find('>') + 1 : rawPace.find('<')])   
                #print('Pace', pace)

                #FG%
                rawFgPCT = soup[soup.find('data-stat="fg_pct" >') + 18 : soup.find('data-stat="fg_pct" >') + 25]
                fgPCT = float(rawFgPCT[rawFgPCT.find('>') + 1 : rawFgPCT.find('<')])   
                #print('FG%', fgPCT)

                #3P%
                raw3PCT = soup[soup.find('data-stat="fg3_pct" >') + 16 : soup.find('data-stat="fg3_pct" >') + 27]
                fg3PCT = float(raw3PCT[raw3PCT.find('>') + 1 : raw3PCT.find('<')])   
                #print('3P%', fg3PCT)

                #FT%
                rawFTPCT = soup[soup.find('data-stat="ft_pct" >') + 16 : soup.find('data-stat="ft_pct" >') + 27]
                ftPCT = float(rawFTPCT[rawFTPCT.find('>') + 1 : rawFTPCT.find('<')])
                #print('FT%', ftPCT)

                #Offensive Rebounds / Game
                rawORB = soup[soup.find('data-stat="orb_per_g" >') + 10 : soup.find('data-stat="orb_per_g" >') + 30]
                orbPerGame = float(rawORB[rawORB.find('>') + 1 : rawORB.find('<')])
                #print('Offensive Rebounds / Game', orbPerGame)

                #Defensive Rebounds / Game
                rawDRB = soup[soup.find('data-stat="drb_per_g" >') + 10 : soup.find('data-stat="drb_per_g" >') + 30]
                drbPerGame = float(rawDRB[rawDRB.find('>') + 1 : rawDRB.find('<')])
                #print('Defensive Rebounds / Game', drbPerGame)

                #Assists / Game
                rawAstPG = soup[soup.find('data-stat="ast_per_g" >') + 15 : soup.find('data-stat="ast_per_g" >') + 30]
                astPerGame = float(rawAstPG[rawAstPG.find('>') + 1 : rawAstPG.find('<')])
                #print('Assists / Game', astPerGame)

                #Steals / Game
                rawStl = soup[soup.find('data-stat="stl_per_g" >') + 15 : soup.find('data-stat="stl_per_g" >') + 30]
                stlPerGame = float(rawStl[rawStl.find('>') + 1 : rawStl.find('<')])
                #print('Steals / Game', stlPerGame)

                #Blocks / Game
                rawBlk = soup[soup.find('data-stat="blk_per_g" >') + 15 : soup.find('data-stat="blk_per_g" >') + 30]
                blkPerGame = float(rawBlk[rawBlk.find('>') + 1 : rawBlk.find('<')])
                #print('Blocks / Game', blkPerGame)

                #Turnovers / Game
                rawTO = soup[soup.find('data-stat="tov_per_g" >') + 15 : soup.find('data-stat="tov_per_g" >') + 30]
                toPerGame = float(rawTO[rawTO.find('>') + 1 : rawTO.find('<')])
                #print('Turnovers / Game', toPerGame)

                #Fouls / Game
                rawF = soup[soup.find('data-stat="pf_per_g" >') + 15 : soup.find('data-stat="pf_per_g" >') + 30]
                foulsPerGame = float(rawF[rawF.find('>') + 1 : rawF.find('<')])
                #print('Fouls / Game', foulsPerGame)

                overallTeamStats.append([teamName, yr, wins, losses, ptsPerGame, offRating, defRating, pace, fgPCT, fg3PCT, ftPCT, orbPerGame, drbPerGame, astPerGame, stlPerGame, blkPerGame, toPerGame, foulsPerGame])
                covTeamStats.append([teamName, yr, wins, losses, ptsPerGame, offRating, defRating, pace, fgPCT, fg3PCT, ftPCT, orbPerGame, drbPerGame, astPerGame, stlPerGame, blkPerGame, toPerGame, foulsPerGame])

            except:
            
                print('Error', teamName, yr)
                print()

            progress(progressCounter, len(teams) * seasons, status='Loading...')
            progressCounter += 1    
            yr -= 1

    print('\nDone!')
    
    MyFile = open(saveTo + datasetName + '.csv','w')

    header = 'Team Name,Year,Wins,Losses,PPG,Off Rating,Def Rating,Pace,FG%,FG3%,FT%,Off RBG,Def RBG,Assists / Game,Steals / Game,Blocks / Game,Turnovers / Game,Fouls / Game' + '\n'

    MyFile.write(header)

    for row in overallTeamStats:
        MyFile.write(clean(str(row)))
        MyFile.write('\n')

    MyFile.close()

    print('\nSaved as ' + saveTo + datasetName + '.csv')


def applyModel(trainSet, testSet):

    #Load Training Set
    df = pd.read_csv(saveTo + trainSet + '.csv')

    X = df[['PPG', 'Off Rating', 'Def Rating', 'FG%', 'FG3%', 'Def RBG', 'Assists / Game']] 
    Y = df['Wins']    

    regr = linear_model.LinearRegression()
    regr.fit(X, Y)

    #print('Intercept: \n', regr.intercept_)
    #print('Coefficients: \n', regr.coef_)

    #Predict Team Wins
    testData = pd.read_csv(saveTo + testSet + '.csv')

    predictions = regr.predict(testData[['PPG', 'Off Rating', 'Def Rating', 'FG%', 'FG3%', 'Def RBG', 'Assists / Game']])

    plt.plot(testData['Wins'], label = 'Actual Wins')
    plt.plot(predictions, label = 'Predicted Wins')
    plt.title('NBA Team Win Predictions (' + str(testYear) + '-' + str(testYear - testSeasons + 1) + ' Seasons)')
    plt.legend() 
    plt.show()
    
    teamWins = testData.values.tolist()

    errSum = 0

    print("\n\nTeam Name, Year, Actual Wins, Predicted Wins")

    for x in range(len(testData)):
        print(teamWins[x][0], teamWins[x][1], teamWins[x][2], math.ceil(predictions[x]), 'Error: (' + str(abs(teamWins[x][2] - math.ceil(predictions[x]))) + ')\n') 
        errSum += abs(teamWins[x][2] - math.ceil(predictions[x]))

    print('Avg Error', errSum / len(testData))
  

def findCorrelations():

    global covTeamStats
    global header

    correlations = []
    stat = header[header.find('PPG') : ]
    print()

    for y in range(4, 17):
        
        wins = []
        stats = []

        for x in range(len(covTeamStats)):
            
            wins.append(covTeamStats[x][2])
            stats.append(covTeamStats[x][y])
            #print(covTeamStats[x][2], covTeamStats[x][5])
        
        wins = np.array(wins)
        stats = np.array(stats)
        corre = np.corrcoef(wins, stats)

        correlations.append([stat[0 : stat.find(',')], corre[0][1]])
        
        print(stat[0 : stat.find(',')])
        print(corre[0][1])
        print()

        stat = stat[stat.find(',') + 1 : ]


    correlations = sorted(correlations,key=lambda l:l[1], reverse=True)

    print(correlations)


saveTo = 'C:\\Users\\faiza\\OneDrive\\Desktop\\NBAData\\' ##Change this to the location in which you want to save your files

#Generate Training Set
year = int(input("Enter starting season: "))
seasons = int(input("Enter the number of seasons to gather data from: "))

print('Gathering training data from the ' + str(year) + " - " + str(year - seasons + 1) + " NBA seasons\n")

trainingSet = 'NBAMLTrainingSet' + str(year) + str(seasons) + "Y"


getTeamNames(year)
generateDataset(year, seasons, trainingSet)

#findCorrelations()

#Generate Testing Set
testYear = int(input("\nEnter starting season for your testing set: "))
testSeasons = int(input("Enter how many seasons you want to test: "))

print('Gathering testing data from the ' + str(testYear) + " - " + str(testYear - testSeasons + 1) + " NBA seasons\n")

testingSet = "NBAMLTestingSet" + str(testYear) + str(testSeasons) + "Y"

generateDataset(testYear, testSeasons, testingSet)


#Apply Regression Model
applyModel(trainingSet, testingSet)

