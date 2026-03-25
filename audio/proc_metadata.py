"""
This program is a module which processes metadata of given audio files.
When metadata for artist or title is not present, the program skips the file.

mutagen.id3.TIT2(encoding=<Encoding.UTF16: 1>, text=[])
Possible tag keys:
Title -> TIT2
artist ->
    TPE1 (Lead Artist/Performer/Soloist/Group
    TOPE (Original Artist/Performer)
genre -> TCON
release year -> TORY -> Original Release Year
Album -> TALB
Eingebettetes Bild (mutagen komprimiert) -> APIC
"""

import mutagen
from mutagen.id3 import ID3, TIT2, COMM, TPE1, TALB, TCON, TDRC, ID3NoHeaderError
from mutagen.mp3 import MP3
# from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4, MP4Tags
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.wave import WAVE
from mutagen import MutagenError

mutagen.id3
def write_meta(file_fullpath, meta_dict):
    # tag_dict ist Dictionary, das als keys präzise die Tags (artist, title, published,...) haben muss
    # Bsp: tag_dict{'artist': 'Joel Kelly', 'title': 'Ich lieber alter Wandersmann', 'year': '2002'}
    # Telegram Downloader: tag_dict = {"artist": channel, "title": newtitle, "year": creatime}

    # --- Datei laden - Mutagen erkennt kompatiblen Dateityp, wird sonst None ---
    try:  # Z.B. AVI-Dateien erzeugen Fehler und Abbruch
        mutag = mutagen.File(file_fullpath)  # Guesses file type
    except MutagenError as e:
        print(f"Metadaten können nicht geschrieben werden für {file_fullpath!s}: {e}")
        return 
    if mutag is None:
        print("Format für die Umwandlung der Metadaten nicht unterstützt. \nMetadaten werden nicht geschrieben")
        return

    # --- Mapping-Dictionaries der Metadaten-Standards erzeugen ---
    ID3_MAP = {
    "title": TIT2,
    "artist": TPE1,
    "album": TALB,
    "genre": TCON,
    "year": TDRC,
    "comm": COMM,
    }

    MP4_MAP = {
    "title": "\xa9nam",
    "artist": "\xa9ART",
    "album": "\xa9alb",
    "genre": "\xa9gen",
    "year": "\xa9day",
    "comm": "\xa9com",
    }

    # Für EasyID3 und Vorbis‑Comments können die gleichen Schlüssel verwendet werden
    # EASY_MAP = {"title", "artist", "album", "genre", "date", "tracknumber"}

    # --- Dateiformate durchgenen um welche Datei es sich handelt und für diese die Metadaten schreiben ---
    if isinstance(mutag, MP3):  # v.A. MP3
        try:
            tags = ID3(file_fullpath)
        except ID3NoHeaderError:
            tags = ID3()
        for key, value in meta_dict.items():
            if key in ID3_MAP:
                tags.add(ID3_MAP[key](encoding=3, text=str(value)))
                tags.save(file_fullpath)
    # Alternativ: EasyMP3 – praktischere Schreibweise
    # elif isinstance(audio, EasyID3):
    #     for key, value in meta_dict.items():
    #         if key in EASY_MAP:
    #             audio[key] = str(value)
    #             audio.save()

    elif isinstance(mutag, FLAC):
        for key, value in meta_dict.items(): # FLAC verwendet Vorbis‑Comments → Schlüssel exakt wie im dict
            mutag[key] = str(value)
            mutag.save()

    elif isinstance(mutag, MP4):  # MP4, M4A, MOV
        tags: MP4Tags = mutag.tags or MP4Tags()
        for key, value in meta_dict.items():
            if key in MP4_MAP:
                mp4_key = MP4_MAP[key]
                # MP4 erwartet Listenwerte (z. B. ["My title"])
                tags[mp4_key] = [str(value)]
                mutag.tags = tags
                mutag.save()
    
    elif isinstance(mutag, OggVorbis):  # OggVorbis
        for key, value in meta_dict.items():
            mutag[key] = [str(value)]
            mutag.save()

    elif isinstance(mutag, OggOpus):
        for key, value in meta_dict.items():
            mutag[key] = [str(value)]
            mutag.save()

    else:
        raise TypeError(f"Metadaten schreiben für {type(mutag)} nicht implementiert")
        # print(f"Metadaten‑Schreiben für {type(mutag)} nicht implementiert")
    
    # FÜR DEBUGGING:
    print(f"- Metadaten geschrieben -") # in\n'{file_fullpath}'")

# To Do
# -Video
# -PDF
# -Bilder

if __name__ == '__main__':

    # target_file = r"C:\Users\Katzi\Desktop\Test\Sade - Still In Love With You.mp3"
    # target_file = r"C:\Users\Katzi\Desktop\Test\15 - Try Again.flac"
    # target_file = r"C:\Users\Katzi\Desktop\Test\Particle swarm optimization-SD.avi"
    # target_file = r"C:\Users\Katzi\Desktop\Test\joseph goebbels on media and propaganda.webm"
    # target_file = r"C:\Users\Katzi\Desktop\Test\2025-02-26 Ergänzung id15093 15600views.ogg"
    # target_file = r"C:\Users\Katzi\Desktop\Test\Albert Einstein - Plagarist and Fraud.MOV"
    target_file = r"C:\Users\Katzi\Desktop\Test\illuminati-intro-reallygraceful.mkv"
    test_tag_dict = {"artist": "TestArtist", "title": "TestTitle", "year": "TestYear"}

    write_meta(file_fullpath=target_file, meta_dict=test_tag_dict)
