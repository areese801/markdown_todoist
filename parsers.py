"""
String parsing functions to drive the main program
"""

import re
import sys
import hashlib

def make_task_hash(task_description: str):
    """
    A helper function that returns a hash of a task after applying some basic transformations
    to the input string to try to handle for leading / trailing spaces, dropping punctuation and the like.

    The idea here is if I make a task "feed dog:", then change that same tasks wording to "Feed Dog" that
    we could use this function to understand that those two things are the same task.

    Definitely not perfect and it kind of is what it is. Good enough for who it's for, but don't make any important life
    decisions based on it's output.

    Of course, these sort of tests could become more complex if needed we could involve a database or a Levenshtein
    distance test or NLP or whatever (If you're reading this and care to contribute via a pull request, please do!).
    But for now, the worst case is some 'duplicated' tasks might make their way into todoist if they were sufficiently
    re-worded in Obsidian in a short enough period of time.   Meh.

    Args:
        task_description:  The task to return a hash for.  Just the task part, not the markdown part
        Otherwise you'll get different digests out of this function

    Returns:

    """

    task_description_for_hash = re.sub(r'[^a-z0-9]', '', task_description.strip().lower()) # Keep numbers and letters, lowercased
    task_md5_hash = hashlib.md5(bytes(str(f"{task_description_for_hash}"),encoding='utf-8')).hexdigest() #then, hash those

    return task_md5_hash


def parse_strings(input_data: str | list) -> list | None:
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
    if type(input_data) not in [str, list]:
        raise TypeError (f"Error.  Expected a string or list of strings.  Got {type(input_data)}")

    # Split string to list as needed
    if type(input_data) is str:
        input_data = input_data.split('\n')

    all_todos = [] #Running list of To-do items
    for line in input_data:

        # Short circuit of the line is an empty string
        if line.strip() == "":
            continue

        todo_match = _parse_string(input_string=line)

        if todo_match is None:
            continue
        else:
            all_todos.append(todo_match)

    # If we found anything return the list, otherwise return None
    if len(all_todos) > 0:
        return all_todos
    else:
        return None

def _parse_string(input_string:str) -> dict | str:
    """
    Uses regex against a line of text to seek an incomplete to-do item
    The line of text should be a single line.  An exception will be thrown if it is not
    Args:
    input_string:  An input string to test the regex_pattern against
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

    todo_regex_pattern = "(^\s*- \[ \]\s+)(.*$)"

    # Input String Should be of type str
    if type(input_string) is not str:
        raise ValueError(f"The input string is expected to be a truthy string of type {type(str)}.  Got {type(input_string)}")

    # Strip whitespace from string, for good measure
    input_string = input_string.strip()

    # Input string should be truthy
    if input_string == "":
        raise ValueError(f"The input string is expected to be truthy. Got the value:  '{input_string}'")

    # Input_string mustn't contain any newline characters
    if '\n' in str(input_string):
        raise ValueError(f"The input string must not contain any newline characters.")

    # Test the string against the regex for matches
    regex_match = re.match(string=input_string, pattern=todo_regex_pattern)
    if regex_match is not None:

        original_string = input_string
        markdown_part = regex_match.group(1)  # We avoid strip here to maintain indentation in the migration module
        task_part = regex_match.group(2).strip()

        # Remove #hashtags from the string.  Keep in mind that # signifies a project in todoist.  @ signifies tags
        drop_chars = ('#', '@')
        for c in drop_chars:
            task_part = task_part.replace(c, '')

        # TODO:  Driop these lines.  moved into standalone function
        # task_description_for_hash = re.sub(r'[^a-z0-9]', '', task_part.lower()) # Keep numbers and letters, lowercased
        # task_md5_hash = hashlib.md5(bytes(str(f"{task_description_for_hash}"),encoding='utf-8')).hexdigest()

        task_md5_hash = make_task_hash(task_description=task_part)

        ret_val =  dict(markdown_part=markdown_part,
                        task=task_part,
                        task_md5_hash=task_md5_hash,
                        original_string=original_string)
    else:
        ret_val = None

    return ret_val  # If same task description (task_name_id_part) in file >1x, it will be duplicated here.  Handle for dups downstream



