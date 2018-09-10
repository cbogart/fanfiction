# Python 2/3 compatibility
try:
    from urllib.parse import unquote_plus
except ImportError:
    from urllib import unquote_plus
import time, re, requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pdb

class Scraper:

    def __init__(self, rate_limit=1):
        self.base_url = 'http://fanfiction.net'
        self.rate_limit = rate_limit
        self.parser = "lxml" #"html.parser"

    def get_genres(self, genre_text):
        genres = genre_text.split('/')
        # Hurt/Comfort is annoying because of the '/'
        corrected_genres = []
        for genre in genres:
            if genre == 'Hurt':
                corrected_genres.append('Hurt/Comfort')
            elif genre == 'Comfort':
                continue
            else:
                corrected_genres.append(genre)
        return corrected_genres

    def story_ids_by_fandom(self, fandom_type, fandom_name, out_fpath):
        """
        Saves a list of story IDs for a fandom to a text file.
        """ 
        url = '{0}/{1}/{2}/?&srt=1&lan=1&r=10'.format(self.base_url, fandom_type, fandom_name.replace(' ', '-'))
        result = requests.get(url)
        html = result.content
        soup = BeautifulSoup(html, self.parser)

        # Get list of pages
        last_page = int(soup.find('a', text="Last")['href'].split('=')[-1])

        for p in tqdm(range(1, last_page)):
            url = '{0}/{1}/{2}/?&srt=1&lan=1&r=10&p={3}'.format(self.base_url, fandom_type, fandom_name.replace(' ', '-'), p)
            result = requests.get(url)
            html = result.content
            soup = BeautifulSoup(html, self.parser)

            # Get story IDs
            story_ids = [s['href'].split('/')[2] for s in soup.find_all('a', {'class': 'stitle'})]

            # Save story IDs (append)
            with open(out_fpath, 'a') as f:
                for s in story_ids:
                    f.write(s + '\n')

    def scrape_story_metadata(self, story_id):
        """
        Returns a dictionary with the metadata for the story.

        Attributes:
            -id: the id of the story
            -canon_type: the type of canon
            -canon: the name of the canon
            -author_id: the user id of the author
            -title: the title of the story
            -updated: the timestamp of the last time the story was updated
            -published: the timestamp of when the story was originally published
            -lang: the language the story is written in
            -genres: a list of the genres that the author categorized the story as
            -num_reviews
            -num_favs
            -num_follows
            -num_words: total number of words in all chapters of the story
            -rated: the story's rating.
        """
        url = '{0}/s/{1}'.format(self.base_url, story_id)
        try:
            result = requests.get(url)
        except (requests.exceptions.ChunkedEncodingError,
                requests.exceptions.ConnectionError) as e:
            pdb.set_trace()
            return None
        html = result.content
        soup = BeautifulSoup(html, self.parser)
        pre_story_links = soup.find(id='pre_story_links')
        if pre_story_links is None:
            return None
        else:
            pre_story_links = soup.find(id='pre_story_links').find_all('a')
        #author_id = re.search(r"var userid = (.*);", str(soup))
        author_id = re.search(r"var userid = (.*?);", str(html))
        if author_id is None:
            pdb.set_trace()
        else:
            author_id = int(author_id.groups()[0]);
        #title = re.search(r"var title = (.*);", str(soup)).groups()[0];
        title = re.search(r"var title = (.*?);", str(html)).groups()[0];
        title = unquote_plus(title)[2:-2]
        metadata_div = soup.find(id='profile_top')
        times = metadata_div.find_all(attrs={'data-xutime':True})
        metadata_text = metadata_div.find(class_='xgray xcontrast_txt').text
        metadata_parts = metadata_text.split('-')
        genres = self.get_genres(metadata_parts[2].strip())
        try:
            chapters = soup.find(id='chap_select').find_all("option")
            chapter_names = []
            omit = 0
            while len(chapters) > 0:
                ch = chapters.pop()
                if omit > 0:
                    chapter_names.insert(0,ch.text[0:-omit])
                else:
                    chapter_names.insert(0,ch.text)
                omit = len(ch.text)
        except AttributeError:
            chapter_names=[title]
             

        metadata = {
            'id': story_id,
            'canon': pre_story_links[-1].text,
            'author_id': author_id,
            'title': title,
            'lang': metadata_parts[1].strip(),
            'published': int(times[-1]['data-xutime']),
            'chapter_names': chapter_names,
            'genres': genres
        }
        if len(pre_story_links) > 1:
            metadata['canon_type'] = pre_story_links[0].text,
        if len(times) > 1:
            metadata['updated'] = int(times[0]['data-xutime'])
        for parts in metadata_parts:
            parts = parts.strip()
            tag_and_val = parts.split(':')
            if len(tag_and_val) != 2:
                continue
            tag, val = tag_and_val
            tag = tag.strip().lower()
            if tag not in metadata:
                val = val.strip()
                try:
                    val = int(val.replace(',', ''))
                    metadata['num_'+tag] = val
                except:
                    metadata[tag] = val
        if 'status' not in metadata:
            metadata['status'] = 'Incomplete'
        return metadata

    def scrape_story(self, story_id, keep_html=False):
        metadata = self.scrape_story_metadata(story_id)
        if metadata is None:
            return None # Error--story not found

        if "chapters" in metadata:
            num_chapters = len(metadata['chapters'])
        if "num_chapters" in metadata:
            num_chapters = int(metadata['num_chapters'])
        else:
            num_chapters = 1

        metadata['chapters'] = {}
        metadata['reviews'] = {}
        # rate limit to follow fanfiction.net TOS
        time.sleep(self.rate_limit)

        if num_chapters == 0: # no chapter structure
            num_chapters = 1
        metadata["num_chapters"] = num_chapters

        for chapter_id in range(1, num_chapters + 1):
            time.sleep(self.rate_limit)
            chapter = self.scrape_chapter(story_id, chapter_id)
            time.sleep(self.rate_limit)
            chapter_reviews = self.scrape_reviews_for_chapter(
                story_id, chapter_id)

            metadata['chapters'][chapter_id] = chapter
            metadata['reviews'][chapter_id] = chapter_reviews

        return metadata

    def scrape_chapter(self, story_id, chapter_id, keep_html=False):
        url = '{0}/s/{1}/{2}'.format(self.base_url, story_id, chapter_id)
        try:
            result = requests.get(url)
        except requests.exceptions.SSLError:
            return b''
        html = result.content
        soup = BeautifulSoup(html, self.parser)
        chapter = soup.find(class_='storytext')
        if chapter is None:
            return b''
        if not keep_html:
            chapter_text = chapter.get_text('\n').encode('utf8')
        return chapter_text

    def scrape_reviews_for_chapter(self, story_id, chapter_id):
        """
        Scrape reviews for chapter in story.

        Returns:
            Array of review dicts.
            Each review dict contains the user id of the reviewer if it exists,
            the timestamp of the review, and the text of the review.
        """
        url = '{0}/r/{1}/{2}'.format(self.base_url, story_id, chapter_id)
        try:
            result = requests.get(url)
        except ssl.SSLError:
            return []
        html = result.content
        soup = BeautifulSoup(html, self.parser)
        reviews_table = soup.find(class_='table-striped')
        reviews = []

        if reviews_table is None:
            return reviews
        else:
            reviews_table = reviews_table.tbody
        reviews_tds = reviews_table.find_all('td')

        if len(reviews_tds) == 1 and reviews_tds[0].string == 'No Reviews found.':
            return reviews

        for review_td in reviews_tds:
            match = re.search(r'href="/u/(.*)/.*">.*</a>', str(review_td))
            if match is not None:
                user_id = int(match.groups()[0])
            else:
                user_id = None
            time = review_td.find('span', attrs={'data-xutime':True})
            if time is not None:
                time = int(time['data-xutime'])

            if review_td.div is None:
               continue 
            review = {
                'time': time,
                'user_id': user_id,
                'text': review_td.div.text.encode('utf8')
            }
            reviews.append(review)
        return reviews
