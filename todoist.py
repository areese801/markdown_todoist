"""
Code to manage the creation of new items in Todoist
See:  https://pypi.org/project/todoist-api-python/
"""
import os.path
import sys

from todoist_api_python.api import TodoistAPI
import json

def _read_api_token_from_file(file_name:str):
    """
    Args:
        file_name:  A Filename that we expect to hold the API token

    Returns:

    """

    """
    For good measure, be stubborn if the file's permissions are not sufficiently restrictive
    """
    perms = oct(os.stat(file_name)[0])[-3:]
    owner_perm = int(perms[0])
    group_perm = int(perms[1])
    world_perm = int(perms[2])

    ok_owner_perms = (4,6)
    ok_group_perms = (4,0)
    ok_world_perms = (0,)

    # Roll over and die if the file permissions are too broad
    if owner_perm not in ok_owner_perms or group_perm not in ok_group_perms or world_perm not in ok_world_perms:
        raise ValueError(f"The file permissions on the file '{file_name}' are too broad.  They are {perms}")

    # If an exception hasn't been raised by now, read the api token from the file
    with open(file_name, 'r') as f:
        s = f.read().strip() #In case there is a trailing new line

    ret_val = s

    return ret_val

# Fetch tasks asynchronously
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


if __name__ == '__main__':

    get_api_token()


