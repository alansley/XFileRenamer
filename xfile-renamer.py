'''
Script : xfile-renamer.py (Python 3)
Purpose: To truncate filenames in a directory and all subdirs to a maximum char count and remove any illegal characters for transfer to a modded Xbox (XFAT filesystem - 42 char limit).
Author : r3dux
Date   : 2019-01-10
'''

import os
import sys

# Flag to control whether we dry-run the file renaming or actually do it, flip to True (perform dry-run) by passing "-d" as an argument to the script.
DRY_RUN = False

# Enums for how we should handle country codes in filenames
from enum import Enum
class CountryCodeOptions(Enum):
    DEFAULT = 1 # Treat as part of file
    SHORTEN = 2 # (Europe) -> (E) etc.
    REMOVE  = 3 # (Europe) / (E) removed.

# Count how many files we've renamed and how many errors occurred
num_files_renamed = 0
num_errors        = 0

# Function to replace the last occurence of a char or string sequence in a source string
# Source: https://stackoverflow.com/a/3675423/1868200
# Modified to not ADD the thing we're looking to replace should it not exist in the source...
def replace_last(source_string, replace_what, replace_with):
    head, _sep, tail = source_string.rpartition(replace_what)
    if (len(head) == 0):
        return head + tail
    else:
        return head + replace_with + tail


# Function to rename a file
def rename_file(directory, src_filename, dst_filename):
    global DRY_RUN
    global num_files_renamed
    global num_errors
    global char_limit

    # If the last character of a file before the extension is a space (e.g. 'foo .bar') remove it
    if (dst_filename.find(' .') != -1):
        dst_filename = replace_last(dst_filename, ' .', '.')

    # Expand filenames to their full absolute values
    full_src = os.path.join(directory, src_filename)
    full_dst = os.path.join(directory, dst_filename)

    # If the source and destination filenames are different perform the rename
    if (src_filename != dst_filename):    
        try:
            if (DRY_RUN == False):
                os.rename(full_src, full_dst)
                print( '[OK] Renamed file {} to {}'.format(src_filename, dst_filename) )
            else:
                print( '[DRY-RUN] Renamed file {} to {}'.format(src_filename, dst_filename) )
                
            num_files_renamed += 1    
        except Exception as e:
            print( '[FAIL] Could not rename file {} to {}. Error: {}'.format(src_filename, dst_filename, e) )
            num_errors += 1


# Function to rename a file to the next available file numbering (e.g. foo~2.bar, foo~13.bar etc.)
def rename_to_next_available_file_numbering(directory, src_filename, dst_filename):

    # Does this filename have an extension? Value will be -1 if not
    extension_start_loc = src_filename.rfind('.')

    # We'll look for numberings in the range 2 through 99...
    for loop in range(2,100):
        
        # Get how many chars the loop value is as a string and add 1 for the tilde prefix
        loop_chars_len = len( str(loop) ) + 1

        # Generate a numbered filename, appending the extension if there is one
        if (extension_start_loc == -1):        
            truncated_filename = dst_filename[:-loop_chars_len] + "~" + str(loop)
        else:
            truncated_filename = dst_filename[:-loop_chars_len] + "~" + str(loop) + src_filename[extension_start_loc:]

        # Does a file with that name already exist? If not then we can rename the file and return
        if ( os.path.isfile(os.path.join(directory, truncated_filename)) == False ):
            rename_file(directory, src_filename, truncated_filename)
            return

    # Could not find a free numbering value? Inform user
    print( '[FAIL] Could not rename file {} - too many numbered versions already?'.format(src_filename) )


# Recursive function to get a list of all directories under a root directory
def get_dirlist(root_dir):
    dir_list = []
    with os.scandir(root_dir) as entries:
        for entry in entries:
            if not entry.name.startswith('.') and entry.is_dir():
                dir_list.append(entry.path)
                dir_list += get_dirlist(entry.path)
    dir_list.sort()                
    return dir_list


# Function to shorten the filenames of all files within a directory to a maximum length
def shorten_files(root_dir, char_limit, cc_handling_policy):
    
    # Generate a list of all subdirectories from the root directory downwards (not forgetting to add the root directory itself)
    dirs  = get_dirlist(root_dir)
    dirs.insert(0, root_dir)

    # Loop over all directories and subdirectories
    for d in dirs:
       
        # Get a list of all files in the directory and sort them by name
        files = [ f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f)) ]
        files.sort()

        # Skip to the next directory if this one is empty
        if (len(files) == 0):
            continue

        # Remove this script from the list of files to process if it's in the same directory as the files
        if (sys.argv[0] in files):
            files.remove( sys.argv[0] )
        
        print( '\nProcessing directory: {} ({} files)...\n'.format(d, len(files)) )

        # Loop over all files in the directory
        for f in files:

            # Get a copy of the filename we can modify
            temp_f = f

            # Shorten country codes to letters if required. Note: If removing we first shorten!
            country_codes = [ ['(Europe)', '(E)'], ['(USA)', '(U)'], ['(Japan)', '(J)'], ['(Europe, USA)', '(EU)'],
                              ['(USA, Europe)', '(UE)'], ['(China)', '(C)'], ['(Brazil)', '(B)'], ['(Japan, USA)', '(JU)'],
                              ['(World)', '(W)'], ['(Germany)', '(G)'], ['(Korea)', '(K)'], ['(Spain)','(S)'],
                              ['(Taiwan)','(T)'], ['(Japan, Korea)', '(JK)'] ]
            
            if (cc_handling_policy != CountryCodeOptions.DEFAULT):                
                for country_code in country_codes:                    
                    temp_f = temp_f.replace(country_code[0], country_code[1])

            # Remove ROM codes from filename if required.
            if (cc_handling_policy == CountryCodeOptions.REMOVE):
                rom_codes = ['[!]', '[M2]', '[M3]', '[M4]', '[M5]', '[M6]', '[M7]']

                # Add all shortened country codes to the list of codes to remove
                for shortened_code in country_codes:
                    rom_codes.insert(0, shortened_code[1])

                # Remove those codes...
                for rom_code in rom_codes:
                    temp_f = temp_f.replace(rom_code, '')

            # Remove / substitute illegal chars
            illegal_chars = [ [',', ''], ['+', 'plus'] ]
            for illegal_char in illegal_chars:
                temp_f = temp_f.replace(illegal_char[0], illegal_char[1])

            # Does the filename need shortening? If so set the flag for us to do some further processing, or if we've
            # shortened or removed a country code and we're under our char limit then just perform the rename and move
            # on to the next file.
            needs_shortening = False
            if (len(temp_f) > char_limit):
                needs_shortening = True
            else:
                if (f != temp_f):
                    rename_file(d, f, temp_f)

            # If we need to further shorten the filename then let's get on with it...
            if (needs_shortening == True):
                
                # ----- Strategy 1 - Remove spaces -----

                # How many characters must we remove?
                num_chars_to_remove = len(temp_f) - char_limit                
                
                # Count spaces in filename only (spaces in the path don't count because we can't change the path)
                space_count = temp_f.count(' ')

                # Will removing spaces bring the filename in under our limit?
                length_without_spaces = len(temp_f) - space_count            
                if (length_without_spaces <= char_limit):

                    # Remove enough space to fit the filename into our limit working right to left
                    for loop in range(num_chars_to_remove):
                        temp_f = replace_last(temp_f, ' ', '')

                    # Rename the file and set flag to skip to next file
                    rename_file(d, f, temp_f)
                    needs_shortening = False

                else: # ----- Strategy 2 - Truncate filename -----

                    # Flag to keep track of whether we've renamed the file yet or not
                    file_renamed = False
                    
                    # Does filename contain a file extension (e.g. .gb, .bin etc.)
                    last_dot = temp_f.rfind('.')

                    # No file extension? Okay - raw truncation
                    if (last_dot == -1):
                        
                        # Truncate filename to our char limit
                        temp_f = temp_f[:(len(temp_f) - num_chars_to_remove)]

                        # Does this truncated filename already exist? If not we can use it...
                        if ( os.path.isfile( os.path.join(d, temp_f) ) == False):
                            rename_file(directory, f, temp_f)
                            file_renamed = True
                        else:
                            # We'll have to find the next available file numbering and rename to that
                            rename_to_next_available_file_numbering(d, f, temp_f)

                    else: # If the file has an extension we must keep it...

                        # Grab the file extension from the end of the filename
                        file_extension = temp_f[last_dot:]

                        # Grab just the filename without the extension
                        temp_f = temp_f[:last_dot]
                        
                        # Truncate and re-assemble filename
                        end_loc = len(temp_f) - num_chars_to_remove
                        temp_f = temp_f[:end_loc]
                        truncated_filename = temp_f + file_extension

                        # Check if filename already exists (we shouldn't rename to it if it does or we'll overwrite it!)
                        if ( os.path.isfile(os.path.join(d, truncated_filename)) == False ):

                            # File does not exist - safe to rename
                            rename_file(d, f, truncated_filename)
                            file_renamed = True

                        else:
                            # We'll have to find the next available file numbering and rename to that                            
                            rename_to_next_available_file_numbering(d, f, temp_f)
                            
                    # End of if file has an extension block

                # End of if we've not shortened by space removal block

            # End of if the file needed shortening block
                
        # End of loop over files in directory

    # End of loop over subdirectories


# Function to print usage instructions
def print_usage():
    print("\nUsage: python xfile-renamer.py <DIRECTORY> <MAX_FILENAME_CHARS> [OPTIONS]")
    print("Optional flags:")
    print("\t-s\tShorten country codes, e.g. '(Europe)' to '(E)' [NOT COMPATIBLE WITH -r],")
    print("\t-r\tRemove  country codes [NOT COMPATIBLE WITH -s],")
    print("\t\tNOTE: Default behaviour is to treat country codes as a normal part of the filename that can be truncated if neccessary.")
    print("\t-d\t(Dry-run) Report what would happen but do not rename files. NOTE: 'next-available' file numbering does not operate in this mode because we cannot test for the existence of renamed files.")
    

# Main function
if __name__ == '__main__':
    # Uncomment to debug - substitute path and char count as you see fit
    #sys.argv = [sys.argv[0], '/home/r3dux/xbox/Gameboy', 42]
    
    char_limit            = 0
    target_directory      = ""

    # How to handle country codes (DEFAULT = treat as normal part of file, SHORTEN = (Europe) -> (E), REMOVE = remove!)
    cc_handling_policy = CountryCodeOptions.DEFAULT

    # Ensure we got at least two arguments. Note: sys.argv will be something like ['sanitise-xbox-filenames.py', '~/ROMs/Gameboy', 42].
    num_args = len(sys.argv)
    if (num_args < 3):
        print("[Error] Missing required arguments.")
        print_usage()
        exit(-1)
    else:
        # Expand tilde if necessary
        if (sys.argv[1][0:1] == "~"):
            target_directory = os.path.expanduser(sys.argv[1])
        else:
            target_directory = sys.argv[1]
        
        # Ensure the target directory exists
        if ( os.path.isdir(target_directory) == False ):
            print("[Error] {} is not a directory or we don't have permissions to access it.".format(target_directory) )
            exit(-2)

        # Ensure the char limit argument is an int
        try:
            char_limit = int( sys.argv[2] )
        except ValueError:
            print("[Error] {} is not a valid integer.".format( sys.argv[2] ) )
            exit(-3)

    # Process additional arguments if they exist
    if (num_args > 3):

        # Specify a list of valid optional arguments
        valid_args = ["-s", "-r", "-d"]        

        # Get any arguments after the mandatory path and char limit
        optional_args = sys.argv[3:]

        # Abort on unrecognised argument(s)
        for arg in optional_args:
            if (arg not in valid_args):
                print("[Error] Unrecognised argument {}".format(arg) )
                print_usage()
                exit(-4)

        # Abort on conflicting arguments
        if ("-s" in optional_args) and ("-r" in optional_args):
            print("[Error] Chose EITHER -s (shorten) OR -r (remove), not both.")
            print_usage()
            exit(-5)

        # Set country code option if flag available
        if ("-s" in optional_args):
            cc_handling_policy = CountryCodeOptions.SHORTEN
        if ("-r" in optional_args):
            cc_handling_policy = CountryCodeOptions.REMOVE
        if ("-d" in optional_args):
            DRY_RUN = True
            
    # All good? Then lets shorten any filenames that need it
    shorten_files(target_directory, char_limit, cc_handling_policy)

    # Report on our progress when we're done returning 0 for success and -6 for this particular fail (we may have returned other minus numbers previously if not dry-running)
    if (num_files_renamed == 0):
        if (DRY_RUN == False):
            print("\n[DONE] No files required renaming.")
        else:
            print("\n[DRY-RUN] No files required renaming.")
        exit(0) # Success, of sorts!
    else:
        if (num_errors == 0):
            if (DRY_RUN == False):
                print("\n[DONE] {} file(s) renamed.".format(num_files_renamed) )
            else:
                print("\n[DRY-RUN] {} file(s) would be renamed.".format(num_files_renamed) )
                print("NOTE: File numbering that would otherwise occur does not show up in dry-runs because we can't check for file existence e.g. foo.bar, f~2.bar, f~3.bar, etc.")
            exit(0) # Success!
        else:
            if (DRY_RUN == FALSE):
                print("\n[DONE] {} file(s) renamed, {} errors.".format(num_files_renamed, num_errors) )
            else:
                print("\n[DRY-RUN] {} file(s) would be renamed, {} errors.".format(num_files_renamed, num_errors) )
                print("NOTE: File numbering that would otherwise occur does not show up in dry-runs because we can't check for file existence e.g. foo.bar, f~2.bar, f~3.bar, etc.")
            exit(-6) # Errors occurred =/ 
