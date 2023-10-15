"""
This module contains helper functions
"""

import os
import json


def _read_obsidian_json():
    """
    Reads the contents of obsidian.json into a dictionary and returns it.
    See:  https://help.obsidian.md/Advanced+topics/Using+Obsidian+URI#Action+%60open%60
    Returns:
    """

    # TODO:  If I decide I want to support more than MacOS, I'll need to add some logic here to determine the OS

    mac_os_location = "~/Library/Application Support"
    obsidian_json_location = os.path.expanduser(os.path.join(mac_os_location, "obsidian", "obsidian.json")) # .replace(' ', '\ ')

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
        if file_name.startswith(vault_path):
            vault_name = vault_path.split('/')[-1]
            break

    # Raise Exception if we didn't resolve a vault name
    if vault_name is None:
        raise ValueError(f"Unable to resolve vault name for file: {file_name}.  Is it in an Obsidian vault?")

    return vault_name


if __name__ == '__main__':
    j = _get_obsidian_vaults()
    pass