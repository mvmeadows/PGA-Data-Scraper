## Overview
This python script is used to scrape PGA Tour player data from www.pgatour.com.
The for loop within the script is used to provide the year range of data to access. 
The script will access all tournaments within the year and return a dataframe 
consisting of the player, the total score for each round and the name of the tournament. 

This script also utilizes a postgresql database to store the dataframe to then be used for more detailed analysis.
