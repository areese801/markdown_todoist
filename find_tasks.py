"""
This module contains functions for parsing (potential) todo items out of markdown
"""
import os.path
import re
import sys
import urllib.parse
import socket
import uuid

from config import _read_base_dir_from_config
from parsers import parse_tasks_from_strings
from parsers import get_todoist_front_matter_setting


def _find_tasks_in_file(file_name: str):
    """

    Args:
        file_name:  The file name we wish to look for / parse to-do items from
    Returns: a dictionary object with any to-do items found
    """

    # Read the file as a string
    with open(file_name, 'r') as f:
        data_string = f.read()

    # Parse each of the lines from the string for to-do items
    tasks = parse_tasks_from_strings(input_data=data_string)

    # Exit if we didn't find anything in the file
    if tasks is None:
        return tasks

    # If we get to this point, we found 1 or more tasks in the file

    # Get some metadata about this host and the file the to-dos were found in to augment the payload
    file_inode = os.stat(file_name).st_ino
    mac_address = hex(uuid.getnode())
    host_name = socket.gethostname()

    # Get note name from fully qualified path.  It's the short file name with the '.md' extension removed
    note_name = re.sub(pattern=r'.md$', repl='', string=os.path.basename(file_name))

    # Create Obsidian URI.  See:  https://help.obsidian.md/Advanced+topics/Using+obsidian+URI
    obsidian_uri = f"obsidian://open?path={urllib.parse.quote(file_name,safe='')}"
    file_name_escaped = file_name.replace(' ', '\ ')

    # Print some nice messages about what we found
    print(f"\nFound {len(tasks)} To-Do items in note: '{note_name}'")
    print(f"Obsidian URI: {obsidian_uri}")
    print(f"Path to File:  {file_name_escaped}")
    for task in tasks:
        task_description = task['task']

        # Inject file metadata
        task['from_file_inode'] = file_inode
        task['from_mac_address'] = mac_address
        task['from_hostname'] = host_name
        task['file_name'] = file_name
        task['file_name_escaped'] = file_name_escaped  # This shows double escaped in json output
        task['obsidian_uri'] = obsidian_uri

        print(f"To-Do:  '{task['task']}'") # That's a 'white square' just for visual reasons.  See:  https://www.alt-codes.net/square-symbols

    return tasks

def find_tasks(parent_directory:str = '~/Obsidian', file_ext= ".md") -> dict:
    """
    Recurses over a directory and any subdirectories found within looking for files with the
    extension(s) defined in the file_ext argument.  These are parsed for to-do items
    Args:
        parent_directory:  The parent director to seek files within
        file_ext: a string or list of file extensions to parse for to-do items within
    Returns: A dict describing all found matches
    """

    """
    Handle parent directory
    """

    # Make sure the parent directory exists
    parent_directory = os.path.realpath(os.path.expanduser(parent_directory))

    if not os.path.isdir(parent_directory):
        raise FileNotFoundError(f"The parent_directory argument '{parent_directory}' does not exist!")
    else:
        print(f"Files will be sought under the path '{parent_directory}'")

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

    all_todo_items = [] # Running list of to-do items, augmented with file, host, metadata

    for root, dirs, files in os.walk(parent_directory):

        # Short circuit if there are no files in the dir
        if len(files) == 0:
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
                # print(f"Inspecting file: {long_file_name}")

                # Does the frontmatter in the file indicate we should not parse for to-do items?
                todoist_frontmatter_setting = get_todoist_front_matter_setting(input_string=long_file_name)
                if todoist_frontmatter_setting is False:
                    # print(f"\nSkipping over file '{long_file_name}' due to todoist frontmatter setting value: "
                    #       f"[{todoist_frontmatter_setting}].")
                    continue

                tasks_from_file = _find_tasks_in_file(file_name=long_file_name)

                if tasks_from_file is not None:
                    all_todo_items.extend(tasks_from_file)

    # Return the payload of all the sweet, sweet to-do items we found
    if len(all_todo_items) > 0:
        ret_val = all_todo_items
    else:
        ret_val = None

    return ret_val


if __name__ == '__main__':
    # Resolve the path to the vault.  If it's not passed in, get it from the config file
    args = sys.argv
    if len(args) >= 2:
        base_dir = args[1]
    else:
        base_dir = _read_base_dir_from_config()

    todo_items = find_tasks(parent_directory=base_dir)

