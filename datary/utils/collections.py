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
            for key, value in (
                (k, exclude_values(values, v)) for (k, v) in args.items())
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


def check_fields(fields, args):
    """Check that every field given in fields is included in args.args.

    - fields (tuple): fieldes to be searched in args
    - args (dict): dictionary whose keys will be checked against fields
    """
    for field in fields:
        if field not in args:
            return False
    return True


def get_element(source, path, separator=r'[/.]'):
    """
    Given a dict and path '/' or '.' separated. Digs into de dict to retrieve
    the specified element.

    Args:
        source (dict): set of nested objects in which the data will be searched
        path (string): '/' or '.' string with attribute names
    """
    return _get_element_by_names(source, re.split(separator, path))


def _get_element_by_names(source, names):
    """
    Given a dict and path '/' or '.' separated. Digs into de dict to retrieve
    the specified element.

    Args:
        source (dict): set of nested objects in which the data will be searched
        path (list): list of attribute names
    """

    if source is None:
        return source

    else:
        if names:
            head, *rest = names
            if isinstance(source, dict) and head in source:
                return _get_element_by_names(source[head], rest)
            elif isinstance(source, list) and head.isdigit():
                return _get_element_by_names(source[int(head)], rest)
            elif not names[0]:
                pass
            else:
                source = None

        return source


def add_element(source, path, value, separator=r'[/.]', override=False):

    return _add_element_by_names(
        source,
        exclude_empty_values(re.split(separator, path)),
        value,
        override)


def _add_element_by_names(source, names, value, override=False):

    if source is None:
        return False

    else:

        if names and names[0]:
            head, *rest = names

            # list and digit head
            if isinstance(source, list) and head.isdigit():
                head = int(head)

            # head not in source :(
            elif head not in source:
                source[head] = {}

            # more heads in rest
            if rest:
                # Head find but isn't a dict or list to navigate for it.
                if not isinstance(source[head], (dict, list)):
                    return False

                _add_element_by_names(source[head], rest, value)

            # it's final head
            else:

                if not override and isinstance(source[head], list):
                    source[head].append(value)

                elif (
                    (not override and isinstance(source[head], dict)) and
                    (isinstance(value, dict))
                ):
                    source[head].update(value)

                else:
                    source[head] = value

        return source


def force_list(element):
    """
    Given an element or a list, concatenates every element and clean it to
    create a full text
    """
    if element is None:
        return []

    if isinstance(element, (collections.Iterator, list)):
        return element
    else:
        return [element]


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


def find_value_in_object(attr, obj):
    """Return values for any key coincidence with attr in obj or any other
    nested dict.
    """

    # Carry on inspecting inside the list or tuple
    if isinstance(obj, (collections.Iterator, list)):
        for item in obj:
            yield from find_value_in_object(attr, item)

    # Final object (dict or entity) inspect inside
    elif isinstance(obj, collections.Mapping):

        # If result is found, inspect inside and return inner results
        if attr in obj:

            # If it is iterable, just return the inner elements (avoid nested
            # lists)
            if isinstance(obj[attr], (collections.Iterator, list)):
                for item in obj[attr]:
                    yield item

            # If not, return just the objects
            else:
                yield obj[attr]

        # Carry on inspecting inside the object
        for item in obj.values():
            if item:
                yield from find_value_in_object(attr, item)


def remove_list_duplicates(lista, unique=False):
    """
    Remove duplicated elements in a list.
    Args:
        lista: List with elements to clean duplicates.
    """
    result = []
    allready = []

    for elem in lista:
        if elem not in result:
            result.append(elem)
        else:
            allready.append(elem)

    if unique:
        for elem in allready:
            result = list(filter((elem).__ne__, result))

    return result


def dict2orderedlist(dic, order_list, default=''):
    """
    Return a list with dict values ordered by a list of key passed in args.
    """
    d = []
    for key_order in order_list:
        d.append(dic.get(key_order, default))
    return d


def get_dimension(array):
    """
    Get dimension of an array getting the number of rows and the max num of
    columns.
    """
    result = [0, 0]

    if all(isinstance(el, list) for el in array):
        result = [len(array), len(max([x for x in array], key=len,))]

    elif array and isinstance(array, list):
        result = [len(array), 1]

    return result
