# -*- coding: utf-8 -*-
import unittest
from collections import OrderedDict
from datary.utils import *


class UtilsCollectionsTestCase(unittest.TestCase):

    obj = {'a': 'a1',
           'aa': None,
           'b': ['b1', 'b2'],
           'c': ['c1', 'c2', 'c3'],
           'd': 'd1',
           'e': 'e1',
           'f': [{'f1': 'ff1', 'f2': 'ff2', 'g': 'ff3'}],
           'g': 'g1'}

    # ###### Manipulate collections functions ############################

    def test_exclude_values(self):
        values = [None, [], '']
        original = {
            'a': None,
            'b': [],
            'c': '',
            'd': False,
            'e': 0,
            'f': [{}, {'fa': 1, 'fb': []}],
        }

        empty_values_filter = exclude_values([], original)
        self.assertEqual(original, empty_values_filter)

        filtered = exclude_values(values, original)
        filtered2 = exclude_empty_values(original)
        assert len(filtered) == 3
        self.assertEqual(len(filtered), len(filtered2))
        assert filtered.get('f', {}) != filtered2.get('f', {})
        self.assertEqual(len(filtered.get('f', {})), 2)
        self.assertEqual(len(filtered2.get('f', {})), 1)

    def test_check_fields(self):
        fields = ('year', 'month', 'day')
        assert check_fields(fields, {'day': 1, 'year': 2014, 'month': 1})
        assert not check_fields(fields, {'day': 1, 'month': 1})

    def test_get_element(self):
        self.assertEqual(get_element(None, ''), None)
        self.assertEqual(get_element({'start': {'day': 1, }}, 'start/day'), 1)
        self.assertEqual(get_element({'start': {'day': 1, }}, 'start.day'), 1)
        self.assertEqual(
            get_element({'start': {'day': 1, }}, 'start.maria'), None)
        self.assertEqual(get_element(
            {'start': {'day': {'name': "Monday", 'num': 1}, }}, 'start/day.num'), 1)

    def test_add_element(self):
        self.assertEqual(add_element(None, '', None), False)

        result = {}
        self.assertEqual(add_element(result, 'a', 1), {'a': 1})
        self.assertEqual(result.get('a'), 1)
        self.assertEqual(len(result.keys()), 1)

        # a is not a dict...
        self.assertEqual(add_element(result, 'a.aa', 2), False)

        # the separator keys not retrieve anything or empty path apply the separator expr.
        self.assertEqual(add_element(result, '', 2, r'-'), result)

        # TEST navigate and create a key - value
        result['a'] = {}

        self.assertEqual(add_element(result, 'a.aa', 2), {'a': {'aa': 2}})
        self.assertEqual(result.get('a', {}).get('aa'), 2)
        self.assertEqual(len(result.get('a').keys()), 1)

        self.assertEqual(add_element(result, 'a.ab', 3), {'a': {'aa': 2, 'ab': 3}})
        self.assertEqual(result.get('a', {}).get('aa'), 2)
        self.assertEqual(result.get('a', {}).get('ab'), 3)
        self.assertEqual(len(result.get('a').keys()), 2)

        # TEST Add to list
        result['a']['aa'] = []

        self.assertEqual(add_element(result, 'a.aa', 2), {'a': {'aa': [2], 'ab': 3}})
        self.assertEqual(add_element(result, 'a.aa', 4), {'a': {'aa': [2, 4], 'ab': 3}})

        # TEST Add to dict
        result['a']['aa'] = {}

        self.assertEqual(add_element(result, 'a.aa', {'aaa': 2}), {'a': {'aa': {'aaa': 2}, 'ab': 3}})
        self.assertEqual(add_element(result, 'a.aa', {'aab': 3}), {'a': {'aa': {'aaa': 2, 'aab': 3}, 'ab': 3}})

    def test_find_value_in_nested_dict(self):
        assert list(find_value_in_object('g', self.obj)) == ['g1', 'ff3']
        assert list(find_value_in_object('c', self.obj)) == ['c1', 'c2', 'c3']

    def test_force_list(self):

        result = force_list(None)
        self.assertEqual(result, [])

        result = force_list([])
        self.assertEqual(result, [])

        result = force_list(['casa'])
        self.assertEqual(result, ['casa'])

        result = force_list('casa')
        self.assertEqual(result, ['casa'])

    def test_flatten(self):
        test = OrderedDict(
            {'a': 2, 'b': 2, 'c': {'ca': 3, 'cb': 'test1', 'cd': [1, 3, 4], 'cc': {'cca': 1}}})
        test_result_1 = collections.OrderedDict([
           ('a', 2), ('b', 2), ('c/ca', 3), ('c/cb', test.get('c', {}).get('cb')), ('c/cc/cca', 1), ('c/cd/1', 3),
           ('c/cd/0', 1), ('c/cd/2', 4)])

        test_result_2 = collections.OrderedDict([
            ('test_a', 2), ('test_c_ca', 3), ('test_c_cd_1', 3), ('test_c_cd_2', 4), ('test_c_cd_0', 1),
            ('test_c_cb', test.get('c', {}).get('cb')), ('test_c_cc_cca', 1), ('test_b', 2)])

        result = flatten(test, '', sep='/')
        result2 = flatten(test, 'test')

        for retrieved_result, test_result in [(result, test_result_1), (result2, test_result_2)]:
            for k, v in test_result.items():
                assert k in retrieved_result
                self.assertEqual(retrieved_result[k], v)

    def test_nested_dict_to_list(self):
        expected = [['', 'b', 'bv2'], ['', 'a', 'av1'], ['c', 'cc', 'ccv1'],
                    ['c', 'ca', 'cav1'], ['c', 'cb', 'cbv1'], ['ccca', 'ccaa', 'ccaav1']]

        test = OrderedDict([
            ('b', 'bv2'),
            ('a', 'av1'),
            ('c', OrderedDict([
                ('cc', 'ccv1'),
                ('ca', 'cav1'),
                ('cb', 'cbv1'),
                ('cca', OrderedDict([
                    ('ccaa', 'ccaav1')])),
            ]))])

        result = nested_dict_to_list("", test)
        for r in result:
            assert r in expected

    def test_remove_duplicates(self):
        expected = [[1], [2, 1, 3], [2, 1, 5], [5], [88]]
        expected1 = [[2, 1, 3], [2, 1, 5], [5], [88]]
        lista = [[1], [2, 1, 3], [1], [2, 1, 5], [5], [88], [1]]

        result = remove_list_duplicates(lista)
        result1 = remove_list_duplicates(lista, unique=True)

        self.assertEqual(result, expected)
        self.assertEqual(result1, expected1)

    def test_dict2orderedlist(self):
        test_dict = {'a': 1, 'b': 2, 'c': 3}

        result1 = dict2orderedlist(test_dict, ['a', 'b', 'c'])
        result2 = dict2orderedlist(test_dict, ['a', 'c'])
        result3 = dict2orderedlist(test_dict, ['c', 'b', 'a'])

        self.assertEqual(result1, [1, 2, 3])
        self.assertEqual(result2, [1, 3])
        self.assertEqual(result3, [3, 2, 1])

    def test_get_dimension(self):

        test = [1, 2, 3]
        test2 = [test, test, test]
        test3 = [test2, test, test2]
        bad_test = "bad_test"

        result1 = get_dimension(test)
        result2 = get_dimension(test2)
        result3 = get_dimension(test3)
        result4 = get_dimension(bad_test)

        self.assertEqual(result1, [1, 3])
        self.assertEqual(result2, [3, 3])
        self.assertEqual(result3, [3, 3])  # could need a fix this case..
        self.assertEqual(result4, [0, 0])
