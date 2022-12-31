import hashlib
import re


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
    task_md5_hash = hashlib.md5(bytes(str(f"{task_description_for_hash}"),encoding='utf-8')).hexdigest() # Then, hash those

    return task_md5_hash
