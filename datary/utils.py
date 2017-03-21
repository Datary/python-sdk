import collections


def flatten(d, parent_key='', sep='_'):
    """
    Transform dictionary multilevel values to one level dict, concatenating
    the keys with sep between them.
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            if isinstance(v, list):
                list_keys = [str(i) for i in range(0, len(v))]
                items.extend(
                    flatten(dict(zip(list_keys, v)), new_key, sep=sep).items())
            else:
                items.append((new_key, v))
    return collections.OrderedDict(items)
