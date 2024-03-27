"""
This module contains helper functions
"""

import os
import json
import sys
import subprocess


def running_on_wsl():
    """
    Helper function to determine if we're running on Linux under WSL (Windows Subsystem for Linux).
    :return: Boolean.  True if WSL is detected, else false
    """

    #TODO: This function was developed on Ubuntu running under WSL.  It might be need to be modified to work with other
    # linux distros under WSL

    try:
        with open('/proc/version', 'r') as f:
            s = f.read().strip().lower()
            if 'microsoft' in s and 'wsl' in s:
                return True
    except Exception as ex:
        print(f"An exception occurred when trying to detect WSL.  It will be ignored.")
        print(ex, file=sys.stderr)
        pass

    return False

def _resolve_windows_style_home_under_wsl():
    """"
    Dynamically Resolves Windows-Style home (e.g. "C:\\Users\\FirstName LastName") to the WSL equivalent (e.g. "/mnt/c/Users/FirstName\ LastName")
    """

    windows_style_home_path = subprocess.check_output(["cmd.exe", "/c", "echo %USERPROFILE%"], stderr=subprocess.DEVNULL).decode("utf-8").strip() # Looks like: C:\\Users\Dave Grohl

    windows_style_split = windows_style_home_path.split("\\")
    windows_style_drive_letter = windows_style_split[0][0] # Drops the ":"
    parts = []

    for i in range(len(windows_style_split)):
        if i == 0:
            parts.append(windows_style_drive_letter.lower())
        else:
            _p = windows_style_split[i]
            parts.append(_p)

    linux_mount_point = '/mnt/' + '/'.join(parts)
    return linux_mount_point

def _transform_windows_style_path_to_wsl_equivalent(some_path:str) -> str:
    """
    Transformas a path like: 'C:\\Users\\Adam Reese\\Obsidian\\Work Vault'
    into something like this:  '/mnt/c/Users/Adam Reese/Obsidian/Work Vault'
    :param some_path: A windows-like file path
    :return:
    """

    path_split = some_path.split('\\')

    parts=[]
    for i in range(len(path_split)):
        if i == 0:
            parts.append(path_split[i][0].lower())
        else:
            parts.append(path_split[i])

    linux_mount_point = '/mnt/' + '/'.join(parts)

    ret_val = linux_mount_point
    return ret_val



def _read_obsidian_json():
    """
    Reads the contents of obsidian.json into a dictionary and returns it.
    See:  https://help.obsidian.md/Advanced+topics/Using+Obsidian+URI#Action+%60open%60
    Returns:
    """

    # Todo:  Modify this function as applicable to support other Operating systems

    # Resolve path to the Obsidian JSON file
    if running_on_wsl() is True:
        wsl_windows_home = _resolve_windows_style_home_under_wsl()
        obsidian_json_location = os.path.join(wsl_windows_home, 'AppData', 'Roaming', 'obsidian', 'obsidian.json')
        pass
        # TODO:  Finish implementing this block
    else:
        # Default to MacOS
        mac_os_location = "~/Library/Application Support"
        obsidian_json_location = os.path.expanduser(os.path.join(mac_os_location, "obsidian", "obsidian.json")) # .replace(' ', '\ ')

    # Read the file
    with open(obsidian_json_location, 'r') as f:
        obsidian_json = json.load(f)

    return obsidian_json


def _get_obsidian_vaults():
    """
    Returns a list of vaults configured in Obsidian
    Returns:  A list of vaults configured in Obsidian
    """

    obsidian_json = _read_obsidian_json()
    vaults = obsidian_json['vaults']
    return vaults


def resolve_vault_name(file_name:str):
    """
    Returns the vault name (e.g. Obsidian Remote Vault) of a given file
    By comparing it's fully qualified path to the list of vaults configured in Obsidian

    Why?  To have more flexibility with the Obsidian URI scheme methods that leverage the Vault name
    Args:
        file_name: The fully qualified path to the note file=
    Returns: A string with just the Vault Name
    """

    vaults = _get_obsidian_vaults()
    vault_name = None
    for vault in vaults.keys():
        vault_path = vaults[vault]['path']

        # Transform as needed for WSL
        if running_on_wsl() is True:
            vault_path = _transform_windows_style_path_to_wsl_equivalent(some_path=vault_path)

        if file_name.startswith(vault_path):
            vault_name = vault_path.split('/')[-1]
            break

    # Raise Exception if we didn't resolve a vault name
    if vault_name is None:
        raise ValueError(f"Unable to resolve vault name for file: {file_name}.  Is it in an Obsidian vault?")

    return vault_name


if __name__ == '__main__':
    j = _get_obsidian_vaults()
