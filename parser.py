"""
This module contains functions for parsing (potential) todo items out of markdown
"""
import os.path
import re
import sys


INCOMPLETE_MARKDOWN_TODO_REGEX_PATTERN = "(^\s*- \[ \]\s+)(.*$)"

def parse_string(input_string:str, regex_pattern:str=None) -> dict | str:
    """
    Uses regex against a line of text to seek an incomplete to-do item
    The line of text should be a single line.  An exception will be thrown if it is not
    Args:
    input_string:  An input string to test the regex_pattern against
    regex_pattern: A string, which can be a custom regex to use.  If omitted (normal behavior)
    then it will be defaulted tp the value in INCOMPLETE_MARKDOWN_TODO_PATTERN

    Returns:
    None or a String
    If a match is found, the corresponding description of the task is returned.  Otherwise, None

    Raises:
    TypeError:  If the input string is not a string
    ValueError: A value error if the input is invalid.  It is expected to be a truthy string without
    any newline characters
    """

    """
    Validate input string
    """

    # Input String Should be of type str
    if type(input_string) is not str:
        raise ValueError(f"The input string is expected to be a truthy string of type {type(str)}.  Got {type(input_string)}")

    input_string = input_string.strip()  # Just to be nice.  We will accommodate for leading / trailing newlines

    # Input string should be truthy
    if input_string == "":
        raise ValueError(f"The input string is expected to be truthy. Got the value:  '{input_string}'")

    # input_string mustn't contain any newline characters (Other than those we may have stripped off of the front or back
    if '\n' in str(input_string):
        raise ValueError(f"The input string must not contain any newline characters.")

    # Validate Regex
    if regex_pattern is None:
        regex_pattern = INCOMPLETE_MARKDOWN_TODO_REGEX_PATTERN
    elif type(regex_pattern) is str:
        try:
            regex_test = re.compile(pattern=regex_pattern)  # Just to test validity
        except Exception as ex:
            regex_pattern = INCOMPLETE_MARKDOWN_TODO_REGEX_PATTERN
            print(f"The regular expression [{regex_pattern}] is not valid. Will default to [{regex_pattern}]."
                  f"Caught exception\n{ex}", file=sys.stderr)
    else:
        raise TypeError(f"The regex_pattern argument needs to be None or a valid regex string.  "
                        f"Got type {type(regex_pattern)}")

    # Test the string for matches
    regex_match = re.match(pattern=regex_pattern, string=input_string)
    if regex_match is not None:

        task_part = regex_match.group(2).strip()

        # Remove #hashtags from the string.  Keep in mind that # signifies a project in todoist.  @ signifies tags
        drop_chars = ('#', '@')
        for c in drop_chars:
            task_part = task_part.replace(c, '')

        task_name_id_part = re.sub(r'\W', '', re.sub(r' +', '_', task_part.lower()))

        ret_val =  dict(task_name_id_part=task_name_id_part, task=task_part)
    else:
        ret_val = None

    return ret_val  # If same task description (task_name_id_part) in file >1x, it will be duplicated here.  Handle for dups downstream

def parse_lines(input_data: str|list, regex_pattern:str=None) -> list|None:
    """
    Passes each line in a string to parse_line (singular) and returns each of the matches
    Args:
        input_data: A string or list of strings (e.g. Markdown Syntax).  May or may not be multiple lines of text
        regex_pattern: A regex pattern to pass into parse_lines. If not passed, the default will be used (recommended)
    Returns:  #A list of dictionaries describing the matches or None, if none are found
    """

    """
    Validate the type of the input
    """
    if not type(input_data) in [str, list]:
        raise TypeError (f"Error.  Expected a string or list of strings.  Got {type(input_data)}")


    # Split string to list as needed
    if type(input_data) is str:
        input_data = input_data.split('\n')

    all_todo_matches = []
    for line in input_data:

        if not line:
            continue

        todo_match = parse_string(input_string=line, regex_pattern=regex_pattern)

        if todo_match is not None:
            all_todo_matches.append(todo_match)

    if len(all_todo_matches) == 0:
        return None
    else:
        return all_todo_matches

def process_file(file_name: str, regex_pattern:str=None) -> list | None:
    """

    Args:
        file_name:  The file name we wish to look for / parse to-do items from
        regex_pattern: A regex pattern to pass into parse_lines. If not passed, the default will be used (recommended)
    Returns: a dictionary object with any to-do items found
    """

    # Read the file
    with open(file_name, 'r') as f:
        data_string = f.read()

    # Process the file
    tasks = parse_lines(input_data=data_string)

    # print what we found, if anything
    if tasks is not None:
        print(f"\nParsed Open To-Do Items from the file '{file_name}':")
        for t in tasks:
            print(f"\t{t['task']}")

        # Get the inode of the file.  The reason is that we want to be resilient against a file being moved or renamed
        file_inode = os.stat(file_name).st_ino

        # Get the mac address of the machine running this code.  This along with file_inode can be used as a key

        print("!")



    return tasks

def scan_files(parent_directory:str = '~/Obsidian', file_ext: list | str = '.md') -> dict:
    """
    Recurses over a directory and any subdirectories found within looking for files with the
    extension(s) defined in the file_ext argument.  These are parsed for to-do items
    Args:
        parent_directory:  The parent director to seek files within
        file_ext: a string or list of file extensions to parse for to-do items within
    Returns: A dict describing all found matches
    """

    # Make sure the parent directory exists
    parent_directory = os.path.realpath(os.path.expanduser(parent_directory))

    if not os.path.isdir(parent_directory):
        raise FileNotFoundError(f"The parent_directory argument '${parent_directory}' does not exist!")

    """
    Handle file_extension(s)
    """

    # Check the type of the argument
    if not type(file_ext) in (str, list):
        raise TypeError(f"The file_ext argument must be a string or list of strings with the file extensions to seek.")

    # Coerce to list as necessary
    if type(file_ext) is str:
        file_ext = [file_ext]

    # Make sure every entry is unique
    file_ext = list(set(file_ext))

    # See that every entry is a string and that it is prefixed with a '.'
    for item in file_ext:
        if type(item) is not str:
            raise TypeError(f"File Extension arguments should be strings.  Got value [{item}] which is of type "
                            f"{type(item)}")
        if not item.startswith('.'):
            file_ext.remove(item)
            file_ext.append(f".{item}")

    """
    Recurse over the directory, and parse files with desired extensions for to-do items
    """
    for root, dirs, files in os.walk(parent_directory):
        # print(f"root = {root}\ndirs = {dirs}\nfiles = {files}\n")

        # Short Circuit if no files in the dir
        if len(files) == 0:
            # No files in the dir (just other dirs)
            continue

        # Test each file for desired extension(s)
        for short_file_name in files:

            file_ext_match = False
            for extension in file_ext:
                if short_file_name.endswith(extension):
                    file_ext_match = True
                    break

            # Found a file extension match.  Parse for to-do items
            if file_ext_match is True:
                long_file_name = os.path.join(root, short_file_name)

                process_file(file_name=long_file_name)

if __name__ == '__main__':
    # base_dir = os.path.realpath(os.path.expanduser("~/Obsidian"))
    # scan_files(parent_directory=base_dir)
    scan_files()