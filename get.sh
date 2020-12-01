#python3 get_story_ids.py --fandom-type game --fandom Detroit-Become-Human  --out ff_detroit_ids.txt
#python3 get_story_ids.py --fandom-type anime --fandom My-Hero-Academia-僕のヒーローアカデミア  --out ff_academia_ids.txt
#python3 get_story_ids.py --fandom-type tv --fandom Friends --out ff_friends_ids.txt
#python3 get_story_ids.py --fandom-type comic --fandom Homestuck --out homestuck_ids.txt
python3 get_stories.py ff_detroit_ids.txt --out-directory ff_detroit_text
python3 get_stories.py ff_academia_ids.txt --out-directory ff_academia_text
#python3 get_stories.py ff_homestuck_ids.txt --out-directory ff_homestuck_text
python3 get_stories.py ff_friends_ids.txt --out-directory ff_friends_text
