import datetime
import logging
import os
import sys

def main(file):

    important = []
    important_phrases = ["Training", "Round", "Received", "Transmitted", "Total", "aggregator"]
    with open(file) as f:
        f = f.readlines()

    for line in f:
        for phrase in important_phrases:
            if phrase in line:
                important.append(line)
                break

    #Begin to parse the valuable data
    timestamp_str = '2024-03-21 02:57:56,432'
    timestamp_format = '%Y-%m-%d %H:%M:%S,%f'

    parsed_timestamp = datetime.strptime(timestamp_str, timestamp_format)
    print(parsed_timestamp)







    for line in important:
        print(line)
    return

if __name__ == "__main__":
    file = sys.argv[1]
    main(file)