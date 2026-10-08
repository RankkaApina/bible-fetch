##############################################################################
# FUNCTIONS FOR
##############################################################################

#---------------------------------------
# Import dependencies
#---------------------------------------

import os
import re
import json
import requests
from bs4 import BeautifulSoup

# Define local paths
#---------------------------------------

from pathlib import Path

TOOLS_DIR = Path(__file__).parent
BOOK_FILE = TOOLS_DIR / 'bible_books.json'

PACKAGE_DIR = TOOLS_DIR.parent
PROJ_ROOT = PACKAGE_DIR.parent
BIBLE_ROOT = PROJ_ROOT / ".bibles"


#---------------------------------------
# Book codes
#---------------------------------------


# Finds the book key (e.g., 'GEN') from a name or short name.
def bible_book_code_lookup(book: str, lang: str = 'eng'):


  with open(BOOK_FILE, 'r', encoding='utf-8') as f:
    books_data = json.load(f)

  search_term = book.lower().rstrip('.')

  for key, data in books_data.items():
    if search_term == key.lower():
      return key, data

    if lang in data["languages"]:
      lang_info = data["languages"][lang]

      if search_term in [lang_info["name"].lower(),
        lang_info["short"].lower().rstrip('.')]:
        return key, data
  return None, None


#---------------------------------------
# Parse Reference
#---------------------------------------


def parse_bible_reference(ref: str):

  pattern = r"([0-9A-Za-z\.\s]+?)\s*(\d+):(\d+)(?:\s*-\s*(?:(\d+):)?(\d+))?$"
  m = re.match(pattern, ref.strip())

  if not m:
    return None

  book, c1, v1, c2, v2 = m.groups()

  start_ch = int(c1)
  end_ch = int(c2) if c2 else start_ch

  return {
    "book": book.strip(),
    "start_ch": start_ch,
    "start_v": int(v1),
    "end_ch": end_ch,
    "end_v": int(v2) if v2 else int(v1)
  }


#---------------------------------------
# Fetch Data from URL
#---------------------------------------


def fetch_bible_data(url):
  headers = {
    "User-Agent": "Mozilla/5.0"
  }
  r = requests.get(url, headers=headers)
  r.raise_for_status()
  return BeautifulSoup(r.text, "html.parser")

#---------------------------------------
# Save Bible Chapter Locally to JSON
#---------------------------------------

def save_bible_chapter(
  version: str,
  book_key: str,
  chapter: int,
  chapter_data: dict
):
  bible_dir = BIBLE_ROOT / version.lower()
  book_path = bible_dir / f"{book_key.lower()}.json"

  bible_dir.mkdir(parents=True, exist_ok=True)

  if book_path.exists():
    with book_path.open('r', encoding='utf-8') as f:
      book_data = json.load(f)
  else:
    book_data = {
      "chapters": {}
    }

  book_data["chapters"][str(chapter)] = chapter_data

  with book_path.open('w', encoding='utf-8') as f:
    json.dump(book_data, f, indent=2, ensure_ascii=False)