##############################################################################
# BIBLE PASSAGES FROM RAAMATTU.FI
##############################################################################

#---------------------------------------
# Import dependencies
#---------------------------------------

from .utils import *

#---------------------------------------
# Bible Versions in raamattu.fi
#---------------------------------------

rfi_versions = {
  "UT2020": "1. Moos, Job, Psalmit, UT",
  "KR92": "Raamattu 1992",
  "KR38": "Raamattu 1933/-38",
  "SelkoL": "Luukkaan evankeliumi selkokielellä",
  "UTNS72": "UT ja psalmit nykysuomeksi",
  "AGUT": "Agricolan UT 1548",
  "B2000": "Bibel 2000",
  "EVVAN": "Johanneksen evankeliumi koltansaameksi",
  "Biibbal": "pohjois-saame",
  "Anaras": "Neljä evankeliumia anaras-kielellä?",
  "KAR11": "UT vienan karjalaksi",
  "RuS1876": "Russian translation 1876",
  "FCR19": "La Bible Nouvelle Francais courant",
  "GNBGE": "GNB Abfolge",
  "HEBR": "Biblia Hebraica Stuttgartensia",
  "NA28": "Novum Testamentum Graece"
}

#---------------------------------------
# Get Raamattu.fi Chapter
#---------------------------------------


def get_rfi_chapter(
  version: str, book_key: str, chapter: int
) -> dict:
  # Fix: use book_key correctly in the URL
  url = f"https://www.raamattu.fi/raamattu/{version}/{book_key}.{chapter}"
  soup = fetch_bible_data(url)

  data = {
    "verses": []
  }

  for tag in soup.select("span.verse[id]"):
    try:
      verse_id = tag["id"]
      verse_num = verse_id.split(".")[-1]

      text_tag = tag.select_one("span")
      text = text_tag.get_text(
        strip=True
      ) if text_tag else ""

      if text:
        data["verses"].append({
          "v": verse_num,
          "text": text
        })
    except (IndexError, KeyError):
      continue

  save_bible_chapter(version, book_key, chapter, data)
  return data
