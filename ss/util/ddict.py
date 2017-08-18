from collections import defaultdict
from copy import deepcopy


class Ddict:
    """Multi-level defaultdict that can be converted to a regular dict to prevent assignment of non-existent keys.
    Adapted from https://stackoverflow.com/a/30921635/2333689"""

    def __init__(self):
        pass

    @classmethod
    def ddict(cls):
        return defaultdict(cls.ddict)

    @classmethod
    def to_dict(cls, ddict):
        return cls.to_dict_recursive(deepcopy(ddict))

    @classmethod
    def to_dict_recursive(cls, d):
        for k, v in d.items():
            if isinstance(v, dict):
                d[k] = cls.to_dict_recursive(v)
        return dict(d)
