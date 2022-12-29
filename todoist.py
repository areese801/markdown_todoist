"""
Code to manage the creation of new items in Todoist
See:  https://pypi.org/project/todoist-api-python/
"""
import os.path
import sys

from todoist_api_python.api import TodoistAPI
import json

from config import _read_api_token_from_file


def get_todoist_tasks(todoist_api_token:str):
    """
    Gets a list of all open tasks in todoist
    Args:
        todoist_api_token:
    Returns:
    """

    api = TodoistAPI(todoist_api_token)
    try:
        tasks = api.get_tasks()
        return tasks
    except Exception as ex:
        print(f"Got Exception while trying to collect tasks from the Todoist API:\n{ex}.", file=sys.stderr)
        raise ex


def get_api_token(todoist_api_config_file: str = 'config/todoist_api_config.json'):
    """
    Consults the api config file, which should adhere to the structure specified in
    config/todoist_api_config_TEMPLATE.json to resolve the API token
    Args:
        todoist_api_config_file:  A path to the config file we can use to read the API token from
    Returns:

    """

    # Read the config file
    with open (todoist_api_config_file, 'r') as f:
        todoist_config = json.loads(f.read())['todoist_api_config']

    # Get the API token out of the config json object.  If that string is a file, read the token from that file
    todoist_api_token = todoist_config['todoist_api_token']
    if os.path.isfile(todoist_api_token):
        todoist_api_token = _read_api_token_from_file(file_name=todoist_api_token)

    return todoist_api_token

def create_task(todoist_api_token:str, task_content:str, task_description:str = None, due_string:str = "Today") -> str:
    """
    Creates a task in todoist and returns the URL for that task
    Note that the create method for the API takes a lot of optional parameters
    This function could be refactored to handle for those should the need arise.

    If you're reading this and feel like contributing, feel free to submit a pull request!

    See:  https://developer.todoist.com/rest/v2/?python#create-a-new-task

    Args:
        task_content (String):  Not the best name, but corresponds with the API documentation.
            This is the DESCRIPTION of the task itself.  Example:  "Feed the dog"
        task_description (string):  Not the best name, but corresponds with the API documentation.
            This is the ADDITIONAL, optional 'flavor text' so to speak.  Example "...and him a treat cause you love him"
        due_string: "A natural language string that tells the todoist API when a task is due"
            More Details here:  https://todoist.com/help/articles/due-dates-and-times
        todoist_api_token:  The token, required to interact with todoist API


    Returns: A string, which is the URL to the created task
    """

    # Create the payload to pass to the API
    data = dict(content=task_content)

    # Bake in the task description of a truth string was passed in
    if task_description:
        data['description'] = str(task_description)

    # Bake in the task due string, if some value was passed in.  We'll hope it's valid
    # We'll rely on the API itself to return an error if its rubbish
    if due_string:
        data['due_string'] = str(due_string)

    # init API
    api = TodoistAPI(todoist_api_token)
    try:
        task = api.add_task(**data)
    except Exception as ex:
        print(f"Encountered exception of type {type(ex)} while trying to create a task with todoist with the payload:"
              f" {data}\n{ex}", file=sys.stderr)
        return ex

    return task



if __name__ == '__main__':

    get_api_token()


