"""
This module contains functions for parsing (potential) todo items out of markdown
"""

import re
INCOMPLETE_MARKDOWN_TODO_PATTERN = "(^\s*- \[ \]\s+)(.*$)"

def seek_todo(input_string:str, regex_pattern:str=None) -> str:
    """
    Uses regex against a line of text to seek an incomplete todo item
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

    """
    Validation of the input string has passed at this point.
    Apply the regex to see if it matches the pattern for an incomplete todo item in markdown syntax
    """

    



if __name__ == '__main__':
    s = "She said:\nHello there, the angel from my nightmare"
    print(s)
    seek_todo(input_string=s)
