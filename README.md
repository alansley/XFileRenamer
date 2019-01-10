# XFileRenamer (Python 3)

Shortens filenames to make them suitable for FTP-ing to an original Xbox (XFAT, 42 char limit). Or just shortens filenames.

Can also optionally shorten or remove TOSEC / country codes from ROMs.

Usage: python xfile-renamer.py [DIRECTORY] [MAX_FILENAME_CHARS] (Options)
  
    Optional flags:
      -s  Shorten country codes, e.g. (Europe) -> (E) [NOT COMPATIBLE WITH -r]
      -r  Remove country codes and TOSEC codes [NOT COMPATIBLE WITH -s]
      -d  Dry-run - report what would happen but do not rename files (works with -s or -r just fine).
  
NOTE: 'Next-Available' file numbering does not operate correctly in dry-run mode. When not dry-running if shortened filenames collide then files will be numbered as well as possible (~2, ~3 etc).
