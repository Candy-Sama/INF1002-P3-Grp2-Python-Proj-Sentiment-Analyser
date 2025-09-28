import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(BASE_DIR, "..", "data", "sentiment_dictionary.csv")

def wordScores():
    # Always initialize sentimentDict, so it exists even if file fails
    sentimentDict = {}
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