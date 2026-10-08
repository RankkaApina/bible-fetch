##############################################################################
# BIBLE PASSAGES FROM Bible.com
##############################################################################

#---------------------------------------
# Import dependencies
#---------------------------------------

from .utils import *

#---------------------------------------
# Get version number
#---------------------------------------

com_versions = {
  "FB92": "330",    # Virallinen käännös 1992
  "FB38": "365",    # Virallinen käännös 1938
  "FINRK": "1745",    # Raamattu Kansalle (kunniottaa alkuperäistekstejä)
  "FI1776": "60",    # Virallinen? käännös 1776
  "SFB15": "1223"    # Svenska Folkbibeln 2015
}

#---------------------------------------
# Get Bible.com Chapter
#---------------------------------------


def get_com_chapter(
  version: str,
  book_key: str,
  chapter: int,
  lang: str,
):

  version_no = com_versions[version]

  url = f"https://www.bible.com/bible/{version_no}/{book_key}.{chapter}.{version}"

  soup = fetch_bible_data(url)
  data = {
    "verses": [],
    "footnotes": {}
  }

  # Using your exact extraction logic
  verse_spans = soup.find_all(
    "span",
    attrs={
    "data-usfm": True,
    "class": lambda x: x and "ChapterContent_verse__" in x
    },
  )

  for tag in verse_spans:
    v_num_tag = tag.find(
      "span", class_="ChapterContent_label__R2PLt"
    )
    v_num = v_num_tag.get_text(
      strip=True
    ) if v_num_tag else None

    content_spans = tag.find_all(
      "span", class_="ChapterContent_content__RrUqA"
    )
    v_text = " ".join(
      span.get_text(strip=True) for span in content_spans
    )

    if v_num and v_text:
      data["verses"].append({
        "v": v_num,
        "text": v_text,
        "footnotes": []
      })

  save_bible_chapter(version, book_key, chapter, data)
  return data
