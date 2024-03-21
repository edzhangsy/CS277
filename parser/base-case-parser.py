import datetime
import logging
import os
import sys

def main(file):

    important = []
    important_phrases = ["Round", "Received", "Transmitted"]
    with open(file) as f:
        f = f.readlines()

    for line in f:
        for phrase in important_phrases:
            if phrase in line:
                important.append(line)
                break

    #Begin to parse the valuable data
    curr_round = 0
    for line in important:
        if "Round" in line:
            







    for line in important:
        print(line)
    return

if __name__ == "__main__":
    file = sys.argv[1]
    main(file)