########################################
# GET BIBLE PASSAGES
########################################

#---------------------------------------
# Import dependencies
#---------------------------------------

import sys
import argparse
import json
import time

from .tools.utils import *
from .tools.bgw import *
from .tools.rfi import *
from .tools.com import *

# Define local paths
#---------------------------------------

from pathlib import Path

PACKAGE_DIR = Path(__file__).parent
PROJ_ROOT = PACKAGE_DIR.parent
BIBLE_ROOT = PROJ_ROOT / ".bibles"
TOOLS_DIR = PACKAGE_DIR / "tools"
BOOK_FILE = TOOLS_DIR / 'bible_books.json'

#---------------------------------------
# Bible Argument Parser
#---------------------------------------


def bible_args():
  parser = argparse.ArgumentParser(
    description="Fetch Bible references from the internet."
  )
  parser.add_argument(
    "reference", nargs="*", help="bible reference"
  )
  parser.add_argument(
    "--lang",
    nargs="?",
    default="eng",
    help="the language of the book name",
  )
  parser.add_argument(
    "--version",
    nargs="?",
    help="translation (e.g. NIV, NLT)",
    default="NRSVUE",
  )
  parser.add_argument(
    "--verse-numbers",
    action="store_true",
    default=False,
    help="print verse numbers (hidden by default)",
  )
  parser.add_argument(
    "--ascii",
    action="store_true",
    default=False,
    help="translate Unicode to ASCII (useful on Windows)",
  )
  parser.add_argument(
    "--json",
    action="store_true",
    default=False,
    help="output the results in JSON format",
  )
  parser.add_argument(
    "--all",
    action="store_true",
    default=False,
    help="save the whole bible in JSON format",
  )
  parser.add_argument(
    "--force",
    action="store_true",
    default=False,
    help=
    "overwrite existing local files instead of resuming",
  )
  if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)
  args = parser.parse_args()
  return (
    " ".join(args.reference),
    args.lang,
    args.version,
    args.verse_numbers,
    args.ascii,
    args.json,
    args.all,
    args.force
  )


#---------------------------------------
# Check Source: local vs. which website
#---------------------------------------


def check_bible_source(
  version: str,
  book_key: str,
  chapter: int,
  skip_local: bool = False
) -> str:
  # Only check local if we aren't explicitly trying to download/overwrite
  if not skip_local:
    bible_dir = BIBLE_ROOT / version.lower()
    book_path = bible_dir / f"{book_key.lower()}.json"
    if book_path.exists():
      try:
        with book_path.open('r', encoding='utf-8') as f:
          local_data = json.load(f)
          if str(chapter) in local_data.get("chapters", {}):
            return 'local'
      except:
        pass

  if version == 'NRSVUE':
    return 'bgw'

  if version in rfi_versions:
    return 'rfi'

  if version in get_bgw_versions():
    return 'bgw'

  if version in com_versions:
    return 'com'

  print(f"No bible found for version '{version}'.")
  return None


#---------------------------------------
# Get local chapter
#---------------------------------------


def get_local_chapter(
  version: str,
  book_key: str,
  chapter: str,
):
  bible_dir = BIBLE_ROOT / version.lower()
  book_path = bible_dir / f"{book_key.lower()}.json"

  with book_path.open('r', encoding='utf-8') as f:
    full_data = json.load(f)
    chapter_data = full_data["chapters"][str(chapter)]

  return chapter_data


#---------------------------------------
# Fetch the Relevant Chapters
#---------------------------------------


def fetch_bible_chapters(
  version: str,
  book: str,
  book_key: str,
  ch1: int,
  ch2: int,
  lang: str,
  source: str = 'local',
):

  passage_chapters = []

  for ch in range(ch1, ch2 + 1):
    if source != 'local':
      time.sleep(1)
    if source == 'local':
      chapter_data = get_local_chapter(
        version,
        book_key,
        ch,
      )
    if source == 'bgw':
      chapter_data = get_bgw_chapter(
        version,
        book,
        ch,
        book_key,
      )
    if source == 'rfi':
      chapter_data = get_rfi_chapter(
        version,
        book_key,
        ch,
      )
    if source == 'com':
      chapter_data = get_com_chapter(
        version, book_key, ch, lang
      )

    passage_chapters.append(chapter_data)

  return passage_chapters


#---------------------------------------
# Get Specific Passage
#---------------------------------------


def fetch_bible_passage(
  reference: str,
  lang: str = "eng",
  version: str = "NRSVUE",
  show_verse_numbers: bool = False,
  use_ascii: bool = True,
):

  ref_data = parse_bible_reference(reference)

  book = ref_data['book']
  ch1 = ref_data['start_ch']
  v1 = ref_data['start_v']
  ch2 = ref_data['end_ch']
  v2 = ref_data['end_v']

  book_key, book_info = bible_book_code_lookup(book, lang)
  source1 = check_bible_source(version, book_key, ch1)
  source2 = check_bible_source(version, book_key, ch2)
  if source1 == 'local' and source2 == 'local':
    source = 'local'
  elif source1 != 'local':
    source = source1
  else:
    source = source2

  chapters = fetch_bible_chapters(
    version, book, book_key, ch1, ch2, lang, source
  )
  passage_output = []

  for i, chapter_data in enumerate(chapters):
    current_ch_num = ch1 + i
    verses = chapter_data.get("verses", [])

    start_idx = (v1 - 1) if current_ch_num == ch1 else 0
    end_idx = v2 if current_ch_num == ch2 else len(verses)

    requested_verses = verses[start_idx:end_idx]
    passage_output.extend(requested_verses)

  for verse in passage_output:
    text = verse['text']
    if use_ascii:
      from unidecode import unidecode
      text = unidecode(text)

    prefix = f"[{verse['v']}] " if show_verse_numbers else ""
    print(f"{prefix}{text}")


#---------------------------------------
# Save a Full Book to JSON
#---------------------------------------


def save_book(
  book: str, lang: str, version: str, source: str = None
):
  book_key, book_info = bible_book_code_lookup(book, lang)

  ch1 = 1
  ch2 = book_info.get("chapters", 1)
  print(f"Archiving {book} ({version}) to local storage...")

  if source is None:
    source = check_bible_source(version, skip_local=True)

  fetch_bible_chapters(
    version, book, book_key, ch1, ch2, lang, source
  )
  print(f"Successfully archived {ch2} chapters of {book}.")


#-----------------------------------------
# Check if a Complete Book exists in JSON
#-----------------------------------------


def is_book_complete(
  version: str,
  book_key: str,
  expected_chapters: int,
) -> bool:

  bible_dir = BIBLE_ROOT / version.lower()
  book_path = bible_dir / f"{book_key.lower()}.json"

  if book_path.exists():
    try:
      with book_path.open('r', encoding='utf-8') as f:
        data = json.load(f)
        # Check if the count of keys in 'chapters' matches expected count
        actual_chapters = len(data.get("chapters", {}))
        return actual_chapters >= expected_chapters
    except Exception:
      return False
  return False


#---------------------------------------
# Save the Full Bible Version
#---------------------------------------


def save_bible(
  lang: str,
  version: str,
  resume: bool = True,
):
  source = check_bible_source(
    version,
    "GEN",
    1,
    skip_local=True,
  )
  if not source:
    print(
      f"Error: Version '{version}' not found on any remote server."
    )
    return

  # Map your source names
  sources = {
    'bgw': 'BibleGateway',
    'rfi': 'Raamattu.fi',
    'com': 'Bible.com'
  }
  source_name = sources.get(source)

  print(
    f"--- Starting Full Archive of {version} via {source_name} ---"
  )

  with open(BOOK_FILE, 'r', encoding='utf-8') as f:
    books_data = json.load(f)

  for book_key, book_info in books_data.items():
    # Get the full name and expected chapter count
    book_name = book_info["languages"][lang]["name"]
    expected_ch = book_info.get("chapters", 0)

    # RESUME LOGIC: Skip if already fully downloaded
    if resume and is_book_complete(
        version, book_key, expected_ch):
      print(f"Skipping {book_name} (already archived).")
      continue

    try:
      save_book(book_name, lang, version, source=source)
      # Mandatory cooling period to avoid 504/Rate Limiting
      print("Taking a 5s breather...")
      time.sleep(5)
    except Exception as e:
      print(f"Error archiving {book_name}: {e}")
      print("Moving to next book...")
      continue


################ MAIN #################


def main():
  # Capture the arguments from the parser
  reference, lang, version, show_verse_numbers, use_ascii, out_json, all_flag, force = bible_args()

  if all_flag:
    # Save the entire Bible (or all available books)
    save_bible(lang, version, resume=(not force))
  elif out_json:
    # Save a specific book provided in the reference
    if not reference:
      print(
        "Error: Provide a book name (e.g., 'Genesis') to save."
      )
      sys.exit(1)
    save_book(reference, lang, version)
  else:
    if not reference:
      print("Error: No reference provided.")
      sys.exit(1)
    fetch_bible_passage(
      reference,
      lang,
      version,
      show_verse_numbers,
      use_ascii,
    )


if __name__ == "__main__":
  main()
