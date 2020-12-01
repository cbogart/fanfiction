
import csv
import os
from collections import defaultdict
import glob
from tqdm import tqdm

ids = "ff_pride_ids.txt"
stories = "ff_pride_text/stories.csv"
chapters = "ff_pride_text/chapters.csv"
filesd = "ff_pride_text/stories/"
errs = "../AO3Scraper/errs/"

ids = [i[0] for i in csv.reader(open(ids,"r"))]
print "Found",len(ids),"ids"
stories = {s["fic_id"]: s["chapter_count"] for s in csv.DictReader(open(stories,"r"))}
print "found", len(stories),"stories"
chapterinf = defaultdict(set)
chapcount = 0
for c in csv.DictReader(open(chapters,"r")):
    chapterinf[c["fic_id"]].add(c["chapter_num"])
    chapcount += 1
print "found", len(chapterinf),"stories"
print "found", chapcount, "chapters listed"
errs = [f.split("_")[1].split(".")[0] for f in os.listdir(errs)]
files = defaultdict(lambda: defaultdict(int))
filecount = 0
for f in os.listdir(filesd):
    ficid = f.split("_")[0]
    storyid = int(f.split("_")[1].split(".")[0])
    files[ficid]["count"] += 1
    if storyid > files[ficid]["max"]:
        files[ficid]["max"] = storyid 
    filecount += 1
print "found", filecount,"chapters scraped"
print "found", len(files),"stories scraped"

bad = defaultdict(set)
for id1 in tqdm(ids):
    if id1 in errs:
        bad[id1].add("Error file found")
    if id1 not in stories:
        bad[id1].add("No entry in stories.csv")
    if id1 not in chapterinf:
        bad[id1].add("No entry in chapters.csv")
    else:
        if int(stories.get(id1,0)) < len(chapterinf[id1]):
            bad[id1].add("Too few chapters mentioned in stories.csv")
        if int(stories.get(id1,0)) > len(chapterinf[id1]):
            bad[id1].add("Too few chapters mentioned in chapters.csv (" + str(stories.get(id1,0)) + "/" + str(len(chapterinf[id1])) + ")")
        if files[id1]["count"] != int(stories.get(id1,0)):
            bad[id1].add("wrong number of chapters scraped (actual=" + str(files[id1]["count"]) + ", counted=" + str(stories.get(id1,0)) + ")")
            pdb.set_trace()
        if files[id1]["max"] != int(stories.get(id1,0)):
            bad[id1].add("some chapters skipped (actual=" + str(files[id1]["max"]) + ", counted=" + str(stories.get(id1,0)) + ")")

print "Found", len([b for b in bad if len(bad[b]) > 0]), " errors"
for b in bad:
    if len(bad[b]) > 0: 
        print b
        for bb in bad[b]:
            print "      ", bb
