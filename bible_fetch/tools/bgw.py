##############################################################################
# BIBLE PASSAGES FROM BIBLE GATEWAY
##############################################################################
# Source (for bible gateway): https://github.com/covode/bible-fetch

#---------------------------------------
# Import dependencies
#---------------------------------------

import sys
from bs4 import BeautifulSoup
import argparse
import requests
from unidecode import unidecode
import urllib.parse

from .utils import *
#---------------------------------------
# Get Versions availabe at Bible Gateway
#---------------------------------------


def get_bgw_versions():

  url = "https://www.biblegateway.com/versions/"
  try:
    soup = fetch_bible_data(url)

    versions = [
      opt['value']
      for opt in soup.find_all('option')
      if 'lang' not in opt.get('class', [])
      and 'spacer' not in opt.get('class', [])
    ]
    return set(versions)
  except Exception as e:
    print(
      f"Warning: Could not update BibleGateway list: {e}"
    )
    return set()


#---------------------------------------
# Get Bible Gateway Chapter
#---------------------------------------


def get_bgw_chapter(
  version: str,
  book: str,
  chapter: int,
  book_key: str,
) -> dict:
  query = urllib.parse.quote_plus(f"{book} {chapter}")
  url = f"https://www.biblegateway.com/passage/?search={query}&version={version}&interface=print"

  soup = fetch_bible_data(url)
  container = soup.find(class_="passage-content")

  data = {
    "verses": []
  }

  if not container:
    return data

  # 1. KILL THE FOOTERS: Remove the actual lists at the bottom of the page
  # This prevents the text from being appended to the last verse.
  for bottom_junk in container.find_all(class_=["footnotes",
    "crossrefs",
    "publisher-info-bottom"]):
    bottom_junk.decompose()

  # 2. PRE-CLEAN: Remove inline markers ([a], [b], etc.) from within the verses
  for inline_junk in container.find_all(["sup", "a"],
    class_=["footnote", "crossreference"]):
    inline_junk.decompose()

  current_v = None

  # 3. PARSE: Using descendants to maintain verse separation
  for child in container.descendants:
    if child.name in ['sup', 'span']:
      classes = child.get('class',
        []) if child.get('class') else []

      if 'versenum' in classes or 'chapternum' in classes:
        v_num_raw = child.get_text().strip()
        v_num = str(
          chapter
        ) if 'chapternum' in classes else v_num_raw

        current_v = {
          "v": v_num,
          "text": ""
        }
        data["verses"].append(current_v)
        continue

    if isinstance(child, str) and current_v:
      # Check if parent is a verse number we already handled
      parent_classes = child.parent.get('class',
        []) if child.parent.name else []
      if any(cls in parent_classes
        for cls in ['versenum', 'chapternum']):
        continue

      text = child.strip()
      if text:
        current_v["text"] = (
          current_v["text"] + " " + text
        ).strip()

  # Final cleanup of double spaces
  for v in data["verses"]:
    v["text"] = " ".join(v["text"].split())

  save_bible_chapter(version, book_key, chapter, data)

  return data
