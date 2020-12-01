#id,canon_type,canon,author_id,title,updated,published,lang,genres,num_reviews,num_favs,num_follows,num_words,rated,num_chapters,chapter_names
#13056208,"('Games',)",Detroit: Become Human,5712094,'Off The Rails\,,1536080838,English,"['Drama', 'Sci']",3,4,4,1536,Fiction  M

import csv
import json
import datetime
import argparse

parser = argparse.ArgumentParser("Convert fanfiction.net files to csv for DiscourseDB import")
parser.add_argument("ff_download_dir", help="Directory containing metadata.csv and stories/")
parser.add_argument("--csvfile", help="output csv file", default="X")
args,unknown = parser.parse_known_args()
if args.csvfile == "X":
    args.csvfile = args.ff_download_dir.replace("/","") + ".csv"

outf = csv.writer(open(args.csvfile,"w"))
columns = "id,replyto,username,forum,forum_types,discourse,title,when,annotation_lang,annotation_rated,annotation_num_reviews,annotation_num_faves,annotation_num_follows,annotation_genres,post".split(",")
outf.writerow(columns)

for row in csv.DictReader(open(args.ff_download_dir + "/metadata.csv")):
    chapter_names = eval(row["chapter_names"])
    genres = eval(row["genres"])
    for page in range(1,int(row.get("num_chapters",1))+1):
        pagefile = args.ff_download_dir + "/stories/" + row["id"] + "_" + str(page).zfill(4) + ".txt"
        outf.writerow([
	    row["id"]+"_"+str(page),
	    row["id"]+"_"+str(page-1) if page > 1 else "",
            row["author_id"],
            row["title"],
            "STORY",
            "Detroit: Become Human fan fiction",
            chapter_names[page-1],
            datetime.datetime.utcfromtimestamp(int(row["published"])).isoformat(),
            row["lang"],
            row["rated"],
            row["num_reviews"],
            row["num_favs"],
            row["num_follows"],
            ";".join(genres),
            open(pagefile).read()])
