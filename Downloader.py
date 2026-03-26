'''
Telegram Batch Downloader with options and filters
'''
from telethon import TelegramClient, events, sync, types  # Events must be included, otherwise it bounds to coroutine 'MessageMethods.get_messages' was never awaited" error
import telethon.tl.types
import logging
logging.basicConfig(filename="log-telegram-download.txt", format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.INFO, filemode="w+")  # ohne filemode="w+" wird das neue Log nur angefügt, nicht überschreiben
import os
import shutil
import datetime
import pandas as pd
import re
import cleanup_filename
from winsound import Beep
from proc_metadata import write_meta

# API account credentials. If unknowen, get them from https://core.telegram.org/api/obtaining_api_id#obtaining-api-id
api_id = 123456
api_hash = 'your_API_hash'

# Parameter
limit = 6  # Type here None or a number for the number of items to be downloaded 
shutdown = False # Set this to True or False. If set to True, you computer will shut down after finishing.
beeptone = True  # Set this to True or False. True means there will be short acoustic signal when the program is finished. 

# Set here the paths to the task file, archive file and a backup folder (backup saving can be deactivated by setting to None). No final (back)slash!
task_file_path = r"C:\path\to\task_file.ods"
archive_file_path = r"C:\path\to\archive_telegram.ods"
# backup_folder = "C:/Users/Katzi/InternxtDrive - c8f3b5a7-8b54-4218-8bac-4405a9714bfe/HiDrive/Archiv/Python/Backup-Archiv-Dateien/" 
backup_folder = None

# ---

media_dict = {
"Audio":telethon.tl.types.InputMessagesFilterMusic,
"Speech":telethon.tl.types.InputMessagesFilterVoice,
"Video":telethon.tl.types.InputMessagesFilterVideo,
"Photo":telethon.tl.types.InputMessagesFilterPhotos,
"PhotoVideo":telethon.tl.types.InputMessagesFilterPhotoVideo  # Filter for messages containing photos or videos.
# "Alles":telethon.tl.types.TypeMessageMedia
}

header = ["channel", "id", "creation date", "date saved", "title", "size", "size [Mb]", "duration", "extension", "filename", "views", "media modus", "success", "failure error"] 
todaydate = datetime.datetime.today().strftime('%Y-%m-%d')

async def get_channel_messages(target_path, channel, media_type, archive_df, pos_filter, replace_dict, limit):
    ''' Mit async ist's eine co-routine!, Variable zurück geben über await, sonst Fehlermeldung!'''
    
    # Pfad selektieren, ggf. erstellen
    if not os.path.isdir(target_path):
        os.mkdir(target_path)
    os.chdir(target_path)  # Arbeitsverzeichnis zum Zielordner ändern
    
    # Modus selektieren aus Tabelle
    # modus_input = modus # "Speech", "Audio", "Video",..."
    media_type_tel = media_dict.get(media_type)  # Modus-Filter für Telegram wird aus Dict selektiert, Achtung: get_messages-Funktion nimmt nur MessagesFilter, kein z.B. telethon.tl.types.TypeMessageMedia!
    print("Media modus selected:", str(media_type))
    # Messages sammeln
    msgs = await client.get_messages(entity=channel, limit=limit, filter=media_type_tel)
    print(len(msgs), "entries collected")
    if not media_type_tel: # Wenn kein Filter gesetzt ist, müssen alle tatsächlichen Nicht-Medien herausgefiltert werden 
        print("Filtering Media files")
        # msgs = [msg for msg in msgs if msg.media]  # "Media" sind auch URLs und andere Texttypen
        msgs = [msg for msg in msgs if msg.file]
        print(len(msgs), "entries collected after media filtering.")

    # Positiv-Filter        
    if isinstance(pos_filter, str):
        pos_filtered_msgs = []  # Regex-gefilterte Einträge
        pos_filter = pos_filter.split(",")
    if isinstance(pos_filter, list):
        pos_filter=["(?i)"+i for i in pos_filter]  # Groß/Kleinschreibung ignorieren
        for msg in msgs:
            # if any(ele in msg.file.name for ele in pos_filter):  # Wenn ein regex-Eintrag auf den message-text anschlägt
            # if any([re.search(i, str(msg.raw_text)+str(msg.file.name)) for i in pos_filter]):  # Alle Filterregexe in der Liste auf ein Match prüfen
            if any([re.search(i, str(msg.raw_text)) for i in pos_filter]):  # Alle Filterregexe in der Liste auf ein Match prüfen
                pos_filtered_msgs.append(msg)
        print(str(len(pos_filtered_msgs)) + " entries left after positive filter")
    else:
        pos_filtered_msgs = msgs

    # Duplikate filtern
    # Filtern ob file-ID schon vorhanden ist
    # filtered_ids = [msg for msg in msgs if msg.file.id not in archive_df["id"].to_list()]
    # Filtern ob identische Größe, Titel und Länge bereits vorhanden (alle 3 müssen übereinstimmen für Matching)
    msgs_id_filtered = [msg for msg in pos_filtered_msgs if
                    # (msg.file.size not in archive_df["size"].to_list()) and  # nicht alle haben msg.file.size!
                    # (msg.file.duration not in archive_df["duration"].to_list())
                    (msg.id not in archive_df["id"].to_list())
                    # (channel not in archive_df["channel"].to_list())
                    ]
    print(len(msgs_id_filtered), "entries left after ID filter")

    # Dateigrössen-Filter  # ZU ERLEDIGEN
    # if size_filter:
    #     size_filter = size_filter * 1024 ** 2
    #     resulted_msgs = [msg for msg in resulted_msgs if msg.file.size <= size_filter ]
    #     # logging.info(len(resulted_msgs), "Einträge übrig nach Dateigrössen-Filter")
    #     logging.info("Einträge übrig nach Dateigrössen-Filter")

    # Attribute sammeln
    counter_message = 0
    completed_list = []  # Liste mit heruntergeladenen Dateien die später an id_list angefügt wird
    # for msg in filtered_msgs:
    for msg in msgs_id_filtered:
        counter_message += 1  # Message-Zähler
        # Attribute
        # file_id = msg.file.id  # Wird nicht gepflegt -> vermeiden!
        # voiceid = #msg.voice.id
        print("\nDownloading of No.", str(counter_message), "of", len(msgs_id_filtered))
        file_id = msg.id

        # Prüfen ob das Attribut für Dateiname im msg.document.attribute vorhanden ist, verhindert Duplizierung der Dateiendung beim Setzen d. Dateinamens
        filename = False
        if hasattr(msg, "document") and hasattr(msg.document, "attributes"):
            doc_name = [item for item in msg.document.attributes if isinstance(item, telethon.tl.types.DocumentAttributeFilename)]
            if doc_name:  # Liste ist nicht leer (=hat den einen Eintrag)
                title = doc_name[0].file_name  # Liste mit einem Eintrag
                filename = title  # Hier wird bereits der Dateiname gesetzt
        if not filename:
            try:
                title = msg.file.name if msg.file.name else msg.raw_text
            except AttributeError:
                title = msg.raw_text  # ist Dateiname. msg.raw_text ist (detailierte) Beschreibung; auch möglich: msg.message
                print_exception(typestr="File title", set_to=title, counter_message=counter_message, file_id=file_id)
        try:
            size = msg.file.size
            sizeMB = round(size / (1024 ** 2), 2)  # Konvertierung Bytes in Mb
        except AttributeError:  # size gibt es nicht 'NoneType' has no attribute...
            size, sizeMB = 0, 0
            print_exception(typestr="File size", set_to=size, counter_message=counter_message, file_id=file_id)
        
        duration = None  # None ist default, wird ansonsten folgend überschrieben
        if not media_type_tel or not "Photo" in media_type:
            try:
                mime = msg.file.mime_type
                if not "image" in mime:
                    duration = msg.file.duration
                    duration = str(datetime.timedelta(seconds=duration))
            except (AttributeError, TypeError):  # Wenn es keine Länge gibt  (z.B. Photos) oder Länge None ist, dann auf 0 setzen
                print_exception(typestr="Duration", set_to=duration, counter_message=counter_message, file_id=file_id)
                
        try:
            extension = msg.file.ext
        except AttributeError:
            extension = ""
            print_exception(typestr="File extension ", set_to="empty string", counter_message=counter_message, file_id=file_id)
        creatime = msg.date.date().isoformat()  # Datumsformat: yyyy-mm-dd
        try:  # Z.B. Kanalbildänderungen haben den Type "MessageService" und nicht "Message", sodann andere Attribute
            views = msg.views  # views speichern
            views = round(views / 100) * 100  # Auf tausender runden
            views = str(views)  # in Text konvertieren
        except TypeError:  
            views = ""

        # Dateiname aufbereiten
        if not filename:
            if len(title) > 0:
                filename = title + " " + "id" + str(file_id) + extension
            else:  # Titel ist leer
                filename = creatime + " " + "id" + str(file_id) + extension
        filename = cleanup_filename.sanitize(path=target_path, filename=filename, replace_dict=None)
        newtitle = os.path.splitext(filename)[0]
        tag_dict = {"artist": channel, "title": newtitle, "year": creatime}

        # Herunterladen
        print(filename)
        try:  # Datei ist noch nicht im Verzeichnis. Versuchen, sie herunterzuladen
            await msg.download_media(file=filename)
            completed_list.append([channel, file_id, creatime, todaydate, title, size, sizeMB, duration, extension, filename, views, media_type, "success", "no error"])
            print("- File downloaded -")
            # Prüfen ob Datei Mime-Type verfügbar ist, nur dann sind's Audio oder Video-Dateien, die zum Schreiben d. Metadaten übergeben werden
            if hasattr(msg, "file") and hasattr(msg.file, "mime_type"):
                if "audio" in msg.file.mime_type or "video" in msg.file.mime_type:  # Im Moment nur Audio und manche Videos (MP4, MOV, M4A,..)
                    try:
                        write_meta(file_fullpath=target_path+filename, meta_dict=tag_dict)
                    except Exception as inst:
                        print("Error writing metadata", inst)
        
        except ConnectionError as e:
            print(e)
            print("Error: Connection interrupted. Closing procedure.")
            completed_list.append([channel, file_id, creatime, todaydate, title, size, sizeMB, duration, extension, filename, views, media_type, "failure", "Loss of Connection"])
            break # Schleife verlassen
        except Exception as inst:
            print("Error:", filename, "ID:", str(file_id), "could not be downloaded.")
            print("Error message:\n", inst)  # __str__ allows args to be printed directly,
            completed_list.append([channel, file_id, creatime, todaydate, title, size, sizeMB, duration, extension, filename, views, media_type, "failure", inst])
    # Kanalweise Inhalte
    neu_df = pd.DataFrame(completed_list, columns=header)
    archive_df = pd.concat([archive_df, neu_df], ignore_index=True)

    return archive_df

def print_exception(typestr, set_to, counter_message, file_id):
    print(f"Exception: {typestr} could not be retrieved for No. {counter_message} and id {file_id}. Set to {set_to}")

def terminate(arch_dict):
    # Archiv-Datei speichern
    
    timenow = datetime.datetime.today().strftime('%Y-%m-%d %H_%M-')
    archive_filename = archive_file_path.split("/")[-1]
    
    # Schreibschutz lösen: les- und schreibbar.
    os.chmod(archive_file_path, 0o755) 
    # Blätter nacheinander in Datei schreiben 
    with pd.ExcelWriter(archive_file_path) as writer:
        for sheet_name, df in arch_dict.items():
            if "t.me/" in sheet_name:  # Zum Speichern des Sheet Namens ggfs. ungültige Zeichen entfernen
                sheet_name = sheet_name.replace("t.me/", "")
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    # Schreibschutz setzen
    os.chmod(archive_file_path, 0o444)
    # Backup speichern
    if backup_folder:
        shutil.copy2(src=archive_file_path, dst=backup_folder+timenow+archive_filename)

async def main(df_tasks, replace_dict, limit, beeptone, shutdown):
    '''
    Archiv initialisieren, get_channel_messages aufrufen, 
    '''
    if os.path.isfile(archive_file_path):  # Prüfen ob Datei vorhanden
        arch_dict = pd.read_excel(io=archive_file_path, sheet_name=None)  # Archiv-Datei als Dict aller Blätter laden
    else:
        pd.ExcelWriter(archive_file_path)  # Leere Datei initialisieren
        arch_dict = {}

    df_tasks["Channel"]=df_tasks.Channel.str.replace("t.me/","")  # Ggfs. t.me/ entfernen
    for index, zeile in df_tasks.iterrows():
        print("\n --- Starting with channel", zeile["Channel"], "--- ")#, "Modus:", zeile["Modus"])
        if zeile["Channel"] in arch_dict.keys():
            archive = arch_dict[zeile["Channel"]]
        else:
            archive = pd.DataFrame(columns=header)  # leeres DF erzeugen

        #Positiv-Filter-Eintrag vorbereiten (nan oder Whitespace-String werden mit None ersetzt)
        pos_entry = None if str(zeile["Positive-Filter"]) == "nan" or zeile["Positive-Filter"].isspace() else zeile["Positive-Filter"]
        
        if client.is_connected(): # Vorsorgemaßnahme gegen Verbindungsabbruch
            archive_new = await get_channel_messages(channel=zeile["Channel"], target_path=zeile["Target Path"], media_type=zeile["Media-Modus"], pos_filter=pos_entry, archive_df=archive, replace_dict=replace_dict, limit=limit)
        else:
            print("Error: Connection lost. Closing procedure.")
            break # Schleife verlassen

        arch_dict[zeile["Channel"]] = archive_new  # Spezifisches DF im Dict updaten

    terminate(arch_dict=arch_dict)

    print("\n - FINISHED DOWNLOADING - ")

    if beeptone:
        Beep(1000, 1000)
    if shutdown:
        os.system("shutdown -s -t 20")  # Computer herunterfahren, letzte Zahl ist Timer


if __name__ == '__main__':

    client = TelegramClient(session="Downloader", api_id=api_id, api_hash=api_hash, auto_reconnect=True)
    # -> Ansatz für Problemlösung: auto_reconnect=False, session entfernen, zumindest Uhrzeit entfernen (jedes Mal wird Telefonnummer abgefragt) 
    # --- OPTIONEN ---
   
    # --- AUFGABEN-TABELLE LADEN ---
    df_tasks_tm = pd.read_excel(task_file_path, sheet_name="Telegram")
    df_tasks_tm = df_tasks_tm.replace({float('nan'): None})  # Leere Einträge ersetzen mit None 

    with client:
        # client.loop.run_until_complete(main(df=df_tm, replace_dict=replace_dict, limit=limit, beeptone=beeptone, shutdown=shutdown))
        client.loop.run_until_complete(main(df_tasks=df_tasks_tm, replace_dict=None, limit=limit, beeptone=beeptone, shutdown=shutdown))
        # client.run_until_disconnected(main(df_tasks=df_tasks_tm, replace_dict=None, limit=limit, beeptone=beeptone, shutdown=shutdown))
