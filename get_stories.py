from fanfiction.scraper import Scraper
import pickle
import urllib.request
import argparse
import os
import pdb
import csv
from tqdm import tqdm
import timeit


def load_story_ids(fpath):
    """
    Returns list of story ids loaded from text file.
    """

    with open(fpath) as f:
        story_ids = [int(i) for i in f.read().splitlines()]

    return story_ids

def save_stories(scraper, ids, out_dirpath, restart=None):

    metadata_out_fpath = os.path.join(out_dirpath, 'stories.csv')
    chmetadata_out_fpath = os.path.join(out_dirpath, 'chapters.csv')
    storycolumns = "fic_id,title,author,author_key,description,rating,canon_type,fandom,relationship,character,language,published,status,updated,num_words,num_reviews,num_favs,num_follows,chapter_count".split(",")
    chaptercolumns = "fic_id,title,chapter_num,chapter_title,paragraph_count".split(",")
    #columns = ["id", "canon_type", 'canon', 'author_id', 'title', 'updated', 'published', 'lang', 'genres', 'num_reviews', 'num_favs', 'num_follows', 'num_words', 'rated', 'num_chapters', 'chapter_names', 'characters']
    if not os.path.exists(metadata_out_fpath):
        with open(metadata_out_fpath, 'w') as f:
            w = csv.writer(f)
            w.writerow(storycolumns)
    if not os.path.exists(chmetadata_out_fpath):
        with open(chmetadata_out_fpath, 'w') as f:
            chw = csv.writer(f)
            chw.writerow(chaptercolumns)

    story_out_dirpath = os.path.join(out_dirpath, 'stories')
    if not os.path.exists(story_out_dirpath):
        os.mkdir(story_out_dirpath)

    # Change list for restarts
    if restart:
        ids = ids[ids.index(restart):]

    for i in tqdm(ids):
        tqdm.write("Scraping story {}...".format(i))

        #try:
        #    story_metadata = scraper.scrape_story(i)

        #except:
        #    tqdm.write(f"No story found for ID {i}")
        #    continue

        story_metadata = scraper.scrape_story(i)
        if story_metadata is None:
            continue

        # Save metadata
        with open(metadata_out_fpath, 'a') as f:
            w = csv.writer(f)
            w.writerow([story_metadata.get(col, '') for col in storycolumns])

        # Save story
        with open(chmetadata_out_fpath, 'a') as f:
            chw = csv.writer(f)
            for (chn, (c, story)) in enumerate(story_metadata['chapters'].items()):
                story_out_fpath = os.path.join(story_out_dirpath, "{}_{}.csv".format(story_metadata['fic_id'], str(c).zfill(4)))
                chw.writerow([story_metadata["fic_id"], story_metadata["title"], chn+1, story_metadata['chapter_names'][chn], len(story)])
                f2 = csv.writer(open(story_out_fpath, 'w')) 
                f2.writerow(["fic_id","chapter_id","para_id","text"])
                for (pn, para) in enumerate(story):
                    f2.writerow([story_metadata["fic_id"],chn+1,pn,para])


def main():
    parser = argparse.ArgumentParser(description="Scrape stories from a list of IDs.")
    parser.add_argument('ids_fpath', nargs='?', help="Filepath of file with list of IDs.")
    parser.add_argument('--out-directory', nargs='?', dest='out_dirpath', help="Path to directory where will save metadata CSV and story text files. Will be created if doesn't exist.")
    parser.add_argument('--restart', nargs='?', dest='restart', default=None, help="Story ID to restart from.")
    args = parser.parse_args()

    ids = load_story_ids(args.ids_fpath)

    if not os.path.exists(args.out_dirpath):
        os.makedirs(args.out_dirpath)

    scraper = Scraper(rate_limit=0.1)

    if args.restart is not None:
        restart = int(args.restart)
    else:
        restart = None
    save_stories(scraper, ids, args.out_dirpath, restart=restart)

if __name__ == '__main__':
    main()
