import csv
import os

ffs = ["friends"]
for ff in ffs:
    ids = [idd.strip() for idd in open("ff_" + ff + "_ids.txt").readlines()]
    mids = [row["id"] for row in csv.DictReader(open("ff_" + ff + "_text/metadata.csv"))]
    pages = {row["id"]:row.get("num_pages",1) for row in csv.DictReader(open("ff_" + ff + "_text/metadata.csv"))}
    print ff, "id comparison"
    if len(ids) != len(set(ids)):  print "Duplicate ids exist: "
    if len(mids) != len(set(mids)):  print "Duplicate ids in metadata.csv exist:"
    if len(set(ids)) > len(set(mids)): 
        print "Not all ids were collected: missing ", 
        missing = set(ids).difference(set(mids))
        print len(missing), "ids out of ", len(ids),
        if len(missing) < 20: print  missing
        else: print "including ", list(missing)[0:5]
    if len(set(mids)) > len(set(ids)): print "Extra ids were collected: ", set(mids).difference(set(ids))
    for f in pages:
        for pi in range(1,int(pages[f])+1):
            pagefile = "ff_" + ff + "_text/stories/" + str(f) + "_" + str(pi).zfill(4) + ".txt"
            if not os.path.isfile(pagefile):
                print ff, "Page ", pi, " of ", pages[f], " pages of ", f, " missing"
            if os.path.getsize(pagefile) < 100:
                print ff, "Page ", pi, " of ", pages[f], " pages of ", f, " is super short (", (os.path.getsize(pagefile)),")"

