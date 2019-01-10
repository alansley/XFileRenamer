# XFileRenamer

Shortens filenames to make them suitable for FTP-ing to an original Xbox (XFAT, 42 char limit). Or just shortens filenames.

Also shortens or removes TOSEC / country codes for ROMs.

Usage: python xfile-renamer.py <DIRECTORY> <MAX_FILENAME_CHARS> [OPTIONS]
  
    Optional flags:
      -s  Shorten country codes, e.g. (Europe) -> (E) [NOT COMPATIBLE WITH -r]
      -r  Remove  country codes [NOT COMPATIBLE WITH -s]
      -d  Dry-run - report what would happen but do not rename files.
  
NOTE: 'Next-Available' file numbering does not operate in dry-run mode because we only test for the existence of existing files and number from there. That is, without dry-run mode shortening the filename can result in a matching filename, and if that exists the current file will get numbered (foo.bar -> f~2.bar -> f~3.bar etc) but in dry-run mode this doesn't function because the script checks for actual file existence not against a list of potential filenames to compare with (i.e. what WOULD happen).
    
