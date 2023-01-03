"""
String parsing functions to drive the main program
"""

import re
import sys

from hashing import make_task_hash
import os
import frontmatter
from yaml import parser as yaml_parser


def parse_tasks_from_strings(input_data):
    """
    Parses each line in a string to parse_line (singular) and returns each of the matches
    Args:
        input_data: A string or list of strings (e.g. Markdown Syntax).  May or may not be multiple lines of text
    Returns:  A list of dictionaries describing the matches or None, if none are found
    """

    """
    Validate the type of the input
    """
    if type(input_data) not in [str, list]:
        raise TypeError(f"Error.  Expected a string or list of strings.  Got {type(input_data)}")

    # Split string to list as needed
    if type(input_data) is str:
        input_data = input_data.split('\n')

    all_todos = []  # Running list of To-do items
    for line in input_data:

        # Short circuit of the line is an empty string
        if line.strip() == "":
            continue

        todo_match = _parse_task_from_string(input_string=line)

        if todo_match is None:
            continue
        else:
            all_todos.append(todo_match)

    # If we found anything return the list, otherwise return None
    if len(all_todos) > 0:
        return all_todos
    else:
        return None


def _parse_task_from_string(input_string: str):
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

        task_md5_hash = make_task_hash(task_description=task_part)

        ret_val = dict(markdown_part=markdown_part,
                       task=task_part,
                       task_md5_hash=task_md5_hash,
                       original_string=original_string)
    else:
        ret_val = None

    # TODO: If same task in file >1x, it might be duplicated here.  Handle for duplicates downstream
    return ret_val


def parse_frontmatter(input_string: str) -> frontmatter.Post:
    """
    Parses front matter from a file or string
    Args:
        input_string: A fully qualified file path or a string

    Returns:
    """

    # Is input_string a file?
    if os.path.isfile(input_string):
        with open(input_string, 'r') as f:
            input_string = f.read()
    try:
        """
        Note:  Frontmatter fails when trying to parse frontmatter that looks like the below (Obsidian Template Variables):
        It raises yaml.parser.ParserError
        
        ---
        tags:
          - {{date}}
          - {{date:YYYY}}-MM-DD
          - {{date:MMMM}}
          - {{date:dddd}}
          - WorkWeek{{date:ww}}
          - DailyNote
        publish: false
        ---
        """

        ret_val = frontmatter.loads(text=input_string, encoding='utf-8')
    except yaml_parser.ParserError as ex:
        # print(f"Got Exception of type {type(ex)} while trying to parse the input below.  "
        #       f"Continuing: \n{input_string}", file=sys.stderr)
        # print(ex, file=sys.stderr)
        ret_val = None



    return ret_val


def get_todoist_front_matter_setting(input_string:str):
    """
    Parses the todoist property from the frontmatter of a string or file that that string is the path for

    This is used to disallow specific notes (e.g. Packing list Template) from having parsed To-do's migrated to Todoist

    Args:
        input_string: A fully qualified file path or a string

    Returns: A Boolean flag, defaulting to True where no setting is found.
    Raises: Value error if the 'todoist' key is supplied in the frontmatter with any value other than 'true' or 'false'
    """

    fm = parse_frontmatter(input_string=input_string)

    ret_val = None
    if fm is None:
        # This might happen due to the try block in parse_frontmatter.  Move on with life
        return ret_val
    elif type(fm) is not frontmatter.Post:
        print(f"The resulting object was not of type {type(frontmatter.Post)}, which is unexpected.  Continuing.",
              file=sys.stderr)
        return ret_val
    elif not hasattr(fm, 'metadata'):
        print(f"The resulting object of type {type(frontmatter.Post)} does not have a 'metadata' attribute, which is "
              f"unexpected.  Continuing.", file=sys.stderr)
        return ret_val

    metadata = fm.metadata  # This is a dict
    todoist = metadata.get('todoist')

    if todoist is None:
        ret_val = True
    elif todoist is False:
        ret_val = False  # Expected when frontmatter explicitly contains 'todoist: false'
    elif todoist is True:
        ret_val = True   # Not necessary to supply, but this is when the frontmatter explicitly contains 'todoist: true'
    else:
        raise ValueError(f"Could not parse 'todoist' setting front matter.  There is no handling.  "
                         f"Got value '{todoist}', which is of type {type(todoist)} from the input: \n {input_string}")
    return ret_val
