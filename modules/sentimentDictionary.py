import csv
import os

os.chdir('..\data')
file_path = r'sentiment_dictionary.csv'

try:
    with open(file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
        csv_reader = csv.reader(csvfile)

        sentimentDict = {

        }

        for row in csv_reader:
            sentimentDict[row[0]] = float(row[1])

        print(sentimentDict)

except Exception as e:
    print(e)