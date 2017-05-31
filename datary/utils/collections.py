# -*- coding: utf-8 -*-
import re
import structlog
import collections

logger = structlog.getLogger(__name__)


def exclude_values(values, args):
    """Exclude data with specific value.

    - value (list): values to filter
    - args (dict): dictionary which will be filtered
    """

    if isinstance(args, dict):
        return {
            key: value
            for key, value in ((k, exclude_values(values, v)) for (k, v) in args.items())
            if value not in values
        }
    elif isinstance(args, list):
        return [
            item
            for item in [exclude_values(values, i) for i in args]
            if item not in values
        ]
    else:
        return args


def exclude_empty_values(args):
    """Exclude None, empty strings and empty lists using exclude_values."""
    return exclude_values(['', 'None', None, [], {}], args)


def nested_dict_to_list(path, dic):
    """
    Transform nested dict to list
    """
    result = []

    for key, value in dic.items():
        # omit __self value key..
        if key != '__self':
            if isinstance(value, dict):
                aux = path + key + "/"
                result.extend(nested_dict_to_list(aux, value))
            else:
                if path.endswith("/"):
                    path = path[:-1]

                result.append([path, key, value])
    return result


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


def get_element(source, path, separator=r'[/.]'):
    """
    Given a dict and path '/' or '.' separated. Digs into de dict to retrieve the specified element.

    Args:
        source (dict): set of nested objects in which the data will be searched
        path (string): '/' or '.' string with attribute names
    """
    return _get_element_by_names(source, re.split(separator, path))


def _get_element_by_names(source, names):
    """
    Given a dict and path '/' or '.' separated. Digs into de dict to retrieve the specified element.

    Args:
        source (dict): set of nested objects in which the data will be searched
        path (list): list of attribute names
    """

    if source is None:
        return source

    else:
        if names:
            head, *rest = names
            if head in source:
                return _get_element_by_names(source[head], rest)
            elif head.isdigit():
                return _get_element_by_names(source[int(head)], rest)
            elif not names[0]:
                pass
            else:
                source = None

        return source


def add_element(source, path, value, separator=r'[/.]'):
    return _add_element_by_names(source, exclude_empty_values(re.split(separator, path)), value)


def _add_element_by_names(source, names, value):

    if source is None:
        return False

    else:
        if names and names[0]:
            head, *rest = names
            if head not in source:
                source[head] = {}

            if rest:
                # Head find but isn't a dict no navigate for it.
                if not isinstance(source[head], dict):
                    return False

                _add_element_by_names(source[head], rest, value)

            else:

                if isinstance(source[head], list):
                    source[head].append(value)

                elif isinstance(source[head], dict) and isinstance(value, dict):
                    source[head].update(value)

                else:
                    source[head] = value

        return source
