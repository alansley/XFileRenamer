# XFileRenamer (Python 3)

Shortens filenames and strips XFAT illegal chars to make files suitable for FTP-ing to an original Xbox (XFAT, 42 char limit).

Can also optionally shorten or remove TOSEC / country codes from ROMs.

Usage: python xfile-renamer.py [DIRECTORY] [MAX_FILENAME_CHARS] (Options)
  
    Optional flags:
      -s  Shorten country codes, e.g. (Europe) -> (E) [NOT COMPATIBLE WITH -r]
      -r  Remove country codes and TOSEC codes [NOT COMPATIBLE WITH -s]
      -d  Dry-run - report what would happen but do not rename files (works with -s or -r just fine).
  
NOTE: 'Next-Available' file numbering (~2, ~3 etc) does not operate in dry-run mode.

Example to DRY-RUN (i.e. test but do not perform) the shortening and then cut (if req'd) of all filenames in a given directory down to 42 chars:

python xfile-renamer.py /home/roms/xbox/snes 42 -s -d

