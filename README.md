# NBA-ML-Team-Win-Predictions
This program uses a machine learning model to predict the amount of NBA team wins per season

To run the program, enter the season you want to start with for your training data and the amount of seasons 
before that in which you want to include in the data. This will be used to train the machine learning model.

After that, you enter the starting season in which you want to predict the amount of wins and then the number of 
seasons before that which you want to predict as well. 

Data is scraped from https://www.basketball-reference.com/


## **Example Terminal Output:** 

Enter starting season: 2017 

Enter the number of seasons to gather data from: 2

Gathering training data from the 2017 - 2016 NBA seasons

[===========================================================-] 98.3% ...Loading...

Done!

Saved as C:\Users\faiza\OneDrive\Desktop\NBAData\NBAMLTrainingSet20172Y.csv

Enter starting season for your testing set: 2019

Enter how many seasons you want to test: 2

Gathering testing data from the 2019 - 2018 NBA seasons

[===========================================================-] 98.3% ...Loading...

Done!

Saved as C:\Users\faiza\OneDrive\Desktop\NBAData\NBAMLTestingSet20192Y.csv


## **Predictions** 

**Team Name, Year, Actual Wins, Predicted Wins**

Atlanta Hawks 2019 29.0 27 Error: (2.0)

Atlanta Hawks 2018 24.0 28 Error: (4.0)

Boston Celtics 2019 49.0 52 Error: (3.0)

Boston Celtics 2018 55.0 52 Error: (3.0)

Brooklyn Nets 2019 42.0 41 Error: (1.0)

Brooklyn Nets 2018 28.0 33 Error: (5.0)

Chicago Bulls 2019 22.0 20 Error: (2.0)

Chicago Bulls 2018 27.0 24 Error: (3.0)

Charlotte Hornets 2019 39.0 39 Error: (0.0)

Charlotte Hornets 2018 36.0 42 Error: (6.0)

Cleveland Cavaliers 2019 19.0 17 Error: (2.0)

Cleveland Cavaliers 2018 50.0 44 Error: (6.0)

Dallas Mavericks 2019 33.0 38 Error: (5.0)

Dallas Mavericks 2018 24.0 34 Error: (10.0)

Denver Nuggets 2019 54.0 51 Error: (3.0)

Denver Nuggets 2018 46.0 45 Error: (1.0)

Detroit Pistons 2019 41.0 41 Error: (0.0)

Detroit Pistons 2018 39.0 42 Error: (3.0)

Golden State Warriors 2019 57.0 57 Error: (0.0)

Golden State Warriors 2018 58.0 56 Error: (2.0)

Houston Rockets 2019 53.0 54 Error: (1.0)

Houston Rockets 2018 65.0 63 Error: (2.0)

Indiana Pacers 2019 48.0 50 Error: (2.0)

Indiana Pacers 2018 48.0 45 Error: (3.0)

Los Angeles Clippers 2019 48.0 44 Error: (4.0)

Los Angeles Clippers 2018 42.0 41 Error: (1.0)

Los Angeles Lakers 2019 37.0 35 Error: (2.0)

Los Angeles Lakers 2018 35.0 37 Error: (2.0)

Memphis Grizzlies 2019 33.0 35 Error: (2.0)

Memphis Grizzlies 2018 22.0 26 Error: (4.0)

Miami Heat 2019 39.0 40 Error: (1.0)

Miami Heat 2018 44.0 43 Error: (1.0)

Milwaukee Bucks 2019 60.0 61 Error: (1.0)

Milwaukee Bucks 2018 44.0 40 Error: (4.0)

Minnesota Timberwolves 2019 36.0 37 Error: (1.0)

Minnesota Timberwolves 2018 47.0 47 Error: (0.0)

New Orleans Pelicans 2019 33.0 37 Error: (4.0)

New Orleans Pelicans 2018 48.0 43 Error: (5.0)

New York Knicks 2019 17.0 18 Error: (1.0)

New York Knicks 2018 29.0 32 Error: (3.0)

Oklahoma City Thunder 2019 49.0 49 Error: (0.0)

Oklahoma City Thunder 2018 48.0 50 Error: (2.0)

Orlando Magic 2019 42.0 43 Error: (1.0)

Orlando Magic 2018 25.0 29 Error: (4.0)

Philadelphia 76ers 2019 51.0 47 Error: (4.0)

Philadelphia 76ers 2018 52.0 52 Error: (0.0)

Phoenix Suns 2019 19.0 18 Error: (1.0)

Phoenix Suns 2018 21.0 17 Error: (4.0)

Portland Trail Blazers 2019 53.0 51 Error: (2.0)

Portland Trail Blazers 2018 49.0 48 Error: (1.0)

Sacramento Kings 2019 39.0 39 Error: (0.0)

Sacramento Kings 2018 27.0 24 Error: (3.0)

San Antonio Spurs 2019 48.0 46 Error: (2.0)

San Antonio Spurs 2018 47.0 49 Error: (2.0)

Toronto Raptors 2019 58.0 56 Error: (2.0)

Toronto Raptors 2018 59.0 61 Error: (2.0)

Utah Jazz 2019 50.0 54 Error: (4.0)

Utah Jazz 2018 48.0 53 Error: (5.0)

Washington Wizards 2019 32.0 34 Error: (2.0)

Washington Wizards 2018 43.0 43 Error: (0.0)

**Avg Error 2.433333333333333**

![NBAMLTeamWinsPredictions](https://user-images.githubusercontent.com/43652410/78718954-2287d480-78f1-11ea-994e-1dcaeb6b659d.png)
