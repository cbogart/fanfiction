from fanfiction.scraper import Scraper
import urllib.request
import argparse
import pdb

def main():

    parser = argparse.ArgumentParser(description="Scrape story IDs for a fandom for fanfiction.net")
    parser.add_argument('--fandom-type', nargs='?', dest='fandom_type', help="Type of fandom from FF.net's categories: anime/manga, book, cartoon, etc.")
    parser.add_argument('--fandom', nargs='?', dest='fandom_name', help="Name of fandom.")
    parser.add_argument('--out', nargs='?', dest='out_fpath', help="Filepath of textfile, with extension, to save IDs to.")
    args = parser.parse_args()

    scraper = Scraper()

    print("Scraping story IDs", end=' ')
    scraper.story_ids_by_fandom(args.fandom_type, args.fandom_name, args.out_fpath)
    print('done.')

if __name__ == '__main__':
    main()
