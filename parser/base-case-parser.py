import datetime
import logging
import os
import sys

def main(file):

    important = []
    important_phrases = ["Training", "Round", "Received", "Transmitted", "Total"]
    with open(file) as f:
        f = f.readlines()

    for line in f:
        for phrase in important_phrases:
            if phrase in line:
                important.append(line)
                break

    print(important)
    return

if __name__ == "__main__":
    file = sys.argv[1]
    main(file)