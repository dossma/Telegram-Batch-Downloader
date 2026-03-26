# Telegram-Batch-Downloader
Powerful downloader for a vector of channels or groups with options, filters and archiving functionality (i.e. duplication filter)

## Features
* Fetch an array of channels, designate a saving path and filter options in a table
* Archiving table with all relevant information of downloaded files
* Writing data into file metadata for effective use in programs (i.e. music players) 
* Optional shutdown after end of run

## Motivation 
When you know channels or groups which contain content of interest, you may want to store them on your computer. 
It is also useful as the channel, or the app itself, may shut down at any time and its content would be lost.

If you use Telegram a lot, you may know many channels which are cool. 
So you can list all channels you want to download and set filtering options for each.  

## Scope
The program is targeted for channels or groups which provide media such as documents, audio files, videos or images.

## Instructions
1. You need an API ID and an API hash from Telegram which you can get from [here](https://core.telegram.org/api/obtaining_api_id#obtaining-api-id).
2. Save the files from this repository in a folder
3. Open the file `task_file.ods` and `Downloader.py`
   
### Task file setup
Firstly, it is essential that the table has `Telegram` as its sheet name.

In the column `channel`, add here the channels to be downloaded

In the column `Target Path`, add here the full paths where the content should be saved. Each path must end with a final backslash `\`.

In the column `Media-Modus`, you can add a filter for the typer of media.
Available filtering options:
| Command  | Effect |
|-------|-----|
| `Audio` |  Only audio files |
| `Speech`    | Only speech files |
| `Video`  | Only video files |
| `Photo`  | Only photos |
| `PhotoVideo`  | Only photos and videos |

If you want to get all media, leave the cell blank or type in anything else as the above commands (for example a slash `/`).

In the column `Positive-Filter`, you can add keywords, seperated by comma, which fetch only content where those keyword occur in text/caption.
Matchings are case-insensitive.  

__Example 1:__
If you want to download media in a channel containing conspiracy theories, and you want only things on 9/11 conspiracies, you could list here:
`9/11,911,9-11,plane,flight,WTC,tower` 

__Example 2:__
If you target a channel that provides military news, and you only want content of certain ships, a possible list is:
`aircraft carrier,destroyer,speed boat` 

__Example 3:__
If you target an art channel that shares all kind of things art related but you want only images from Monet, Rimbaud and Baudelaire and all kind of images from the renaissance, you could set Media-Modus:`Photo` and as Positive-Filter: `monet,rimbaud,baudelaire,renaissance`.

<img src="https://github.com/dossma/Telegram-Batch-Downloader/blob/master/target_table.jpg" width=100% height=100%>

### Downloader file setup
1. Paste your API ID and API hash in the designated fields.
2. Set the value for `limit` which indicates how many files you want to download. It downloads in order from the most recent one. Set `None` if you want to get all. Be aware that content can be big in size, think of large videos. In such case, you can do one run with a resonable amount for `limit`, let it finish, and the next day you incraese `limit`, do a consecutive run and so forth. Through the archiving functionality, files already downloaded will be skipped.
3. Set `shutdown` and `beeptone` each to `True` or `False `, the former shutting down the computer when finished while the ladder makes a beep when finished. 
4. Set the paths: `task_file_path` points to the task file, `archive_file_path` where the archive file is located or will be created, and `backup_folder` if you want that a backup of the archive file will be created after each run. These paths pointing to a file do **not** have a final backslash `\`. 

When you're done, run the downloader file and the program starts.

### Examining the archive file
On the first run, when there is no archive file, it will be created.
The archive file contains practically all information of the files which have been downloaded. 
After each run, the file is set to write protected.
To check which files have already be downloaded, the program looks into the column `id`, which is a unique ID for each item in a channel or group.
In case you want to edit the file (deleting a row for example would mean that this file would be downloaded again), then de-select write protection in the file properties before opening. After saving, you must not re-activate write protection again.  

<img src="https://github.com/dossma/Telegram-Batch-Downloader/blob/master/archive_table.jpg" width=100% height=100%>
    
## Development setup

Required external libraries are
- Telethon: [https://github.com/LonamiWebs/Telethon](https://github.com/LonamiWebs/Telethon)
- Pandas: [https://github.com/LonamiWebs/Telethon](https://github.com/pandas-dev/pandas)

```sh
pip install telethon
pip install pandas
```

Downloading can be rather slow. 

I recommend to install cryptg so that decrypting the received data is done in C instead of Python, which is much faster.

```sh
pip install cryptg
```

## Encouragement

Notify me when there's any error or bug.

## Future Work

It is planned to add a negative filter (downloading all but excluding a keyword matching pattern) and a size filter.

## Meta

Author: Jonas Dossmann

Distributed under the AGPL-3.0 license.

[https://github.com/dossma/](https://github.com/dossma/)

<!-- Markdown link & img dfn's -->
[npm-image]: https://img.shields.io/npm/v/datadog-metrics.svg?style=flat-square
[npm-url]: https://npmjs.org/package/datadog-metrics
[npm-downloads]: https://img.shields.io/npm/dm/datadog-metrics.svg?style=flat-square
[travis-image]: https://img.shields.io/travis/dossma/node-datadog-metrics/master.svg?style=flat-square
[travis-url]: https://travis-ci.org/dossma/node-datadog-metrics
[wiki]: https://github.com/dossma/ebook-file-renaming/wiki
