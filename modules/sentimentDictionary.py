import csv
import os

# os.chdir(r'.\data')
file_path = r'INT1002-P3-Grp2-Python-Proj-Sentiment-Analyser\data\sentiment_dictionary.csv'

def wordScores():
    try:
        with open(file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            csv_reader = csv.reader(csvfile)

            sentimentDict = {

            }

            for row in csv_reader:
                sentimentDict[row[0]] = float(row[1])

    except Exception as e:
        print(e)

    return sentimentDict