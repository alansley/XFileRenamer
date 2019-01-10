# XFileRenamer (Python 3)

Shortens filenames to make them suitable for FTP-ing to an original Xbox (XFAT file system, 42 char limit).

Usage: python xfile-renamer.py <DIRECTORY> <MAX_FILENAME_CHARS> [OPTIONS]

Optional flags:
    -s    Shorten country codes, e.g. '(Europe)' to '(E)' [NOT COMPATIBLE WITH -r]
    -r    Remove  country codes [NOT COMPATIBLE WITH -s],")
    -d    Dry-run, e.g. report what would happen but do not rename files.
    NOTE: 'next-available' file numbering (foo~2.bar, foo~3.bar etc.) does not operate in this mode.

The directory pointed recurses to process any and all files in subdirectories.
