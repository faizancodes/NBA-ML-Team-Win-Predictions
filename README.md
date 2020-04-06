# NBA-ML-Team-Win-Predictions
This program uses a machine learning model to predict the amount of NBA team wins per season

To run the program, enter the season you want to start with for your training data and the amount of seasons 
before that in which you want to include in the data. This will be used to train the machine learning model.

After that, you enter the starting season in which you want to predict the amount of wins and then the number of 
seasons before that which you want to predict as well. 

Data is scraped from https://www.basketball-reference.com/


**Example Terminal Output:** 

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



![NBAMLTeamWinsPredictions](https://user-images.githubusercontent.com/43652410/78615623-1263ec80-7840-11ea-8595-9e213e6a5b16.png)
