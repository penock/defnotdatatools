"""
defnotdatatools.misc module is for stuff that either doesn't belong in another module, or stuff that's in such an early stage of development that we're not sure what to call the module it'll eventually go into.

For how to import, see defnotdatatools/README.md.
"""


# < Setup > ============================================================================

import os
import sys


# < Constants > ===============================================================



# < File system related > ===============================================================

def validate_path(path, must_exist=True):
    """
    Raises an Error if the path is invalid.

    Args:
      must_exist: boolean specifying whether we require the path to already exist. Defaults to True

    Returns: None
    """
    if not isinstance(path, str):
        raise TypeError("Invalid path '{}': it's not a string".format(path))
    if not path.strip() == path:
        raise ValueError("Invalid path '{}': has whitespace at start or end".format(path))
    if must_exist and not os.path.exists(path):
        raise FileNotFoundError("path '{}' must exist".format(path))

def git_current_hash(dot_git_folder_path='./.git', len_of_hash=6):
    """Returns current folder's git hash (first 6 characters)"""
    with open(os.path.join(dot_git_folder_path, 'HEAD')) as f_HEAD:
        # This .git/HEAD file has contents like "ref: refs/heads/master\n", hence the 5:-1 below
        # to just extract the path of the file we want (eg "refs/heads/master")
        # Devnote: using regex would be more robust
        head_hash_file_path = f_HEAD.read()[5:-1]
    with open(os.path.join(dot_git_folder_path, head_hash_file_path)) as f_head_hash:
        return str(f_head_hash.read()[:len_of_hash])


# < Misc > ======================================================================

def sod_keys_within(sod, within=None):
    """
    For a sod (Sequence of Dicts), returns sorted set list of keys from dicts 
    at a given key ("within"), or if within is None then it's the root keys.

    Note: the "within" has no way of going more than 1 level deep currently.
    """
    assert isinstance(sod, Sequence)
    keys = set()
    for d in sod:
        assert isinstance(d, dict)
        if within is None:
            keys = keys.union(d.keys())
        else:
            assert isinstance(d[within], dict)
            keys = keys.union(d[within].keys())
    return sorted(list(keys))
