import json
import os

def _read_base_dir_from_config(config_file_name: str = "config/config.json") -> str:
    """
    Reads the directory from which markdown files should be sought from the configuration file
    Args:
        config_file_name:

    Returns:
    """

    # Read the config file
    with open(config_file_name, 'r') as f:
        config = json.loads(f.read())

    # Get the base directory out of the config file
    ret_val = config['config']['markdown_base_directory']
    return ret_val



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
