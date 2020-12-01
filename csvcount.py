import csv
import sys
for file in sys.argv:
    print file, len([row for row in csv.DictReader(open(file))])
