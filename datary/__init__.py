# -*- coding: utf-8 -*-
import os
import re
import json
import random
import requests
import structlog

from datetime import datetime
from urllib.parse import urljoin
from requests import RequestException

from datary.utils import (flatten, nested_dict_to_list, get_element, force_list,
                          exclude_empty_values, add_element, get_dimension,
                          remove_list_duplicates, dict2orderedlist)

from . import version

logger = structlog.getLogger(__name__)
URL_BASE = "http://api.datary.io/"


class Datary():

    __version__ = version.__version__

    DATARY_VISIBILITY_OPTION = ['public', 'private', 'commercial']
    DATARY_CATEGORIES = [
        "business",
        "climate",
        "consumer",
        "education",
        "energy",
        "finance",
        "government",
        "health",
        "legal",
        "media",
        "nature",
        "science",
        "sports",
        "socioeconomics",
        "telecommunications",
        "transportation",
        "other"
    ]

    # Datary Entity Meta Field Allowed
    ALLOWED_DATARY_META_FIELDS = [
        "axisHeaders",
        "caption",
        "citation",
        "description",
        "dimension",
        "downloadUrl",
        "includesAxisHeaders",
        "lastUpdateAt",
        "period",
        "propOrder",
        "rootAleas",
        "size",
        "sha1",
        "sourceUrl",
        "summary",
        "title",
        "traverseOnly",
        "bigdata",
        "dimension"]

    def __init__(self, *args, **kwargs):
        """
        Init Datary class
        """

        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.token = kwargs.get('token')
        self.commit_limit = int(kwargs.get('commit_limit', 30))

        # If a token is not in the params, we retrieve it with the username and
        # password
        if not self.token and self.username and self.password:
            self.token = self.get_user_token(self.username, self.password)

        self.headers = kwargs.get('headers', {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Bearer {}".format(self.token)
        })

##########################################################################
#                             Auth & Request
##########################################################################

    def get_user_token(self, user=None, password=None):
        """
        ===========   =============   ================================
        Parameter     Type            Description
        ===========   =============   ================================
        user          str             Datary username
        password      str             Datary password
        ===========   =============   ================================

        Returns:
            (str) User's token given a username and password.

        """
        payload = {
            "username": user or self.username,
            "password": password or self.password,
        }

        url = urljoin(URL_BASE, "/connection/signIn")
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = self.request(
            url, 'POST', **{'headers': self.headers, 'data': payload})

        # Devuelve el token del usuario.
        user_token = str(response.headers.get("x-set-token", ''))

        if user_token:
            self.headers['Authorization'] = 'Bearer {}'.format(user_token)

        return user_token

    def sign_out(self):

        url = urljoin(URL_BASE, "connection/signOut")

        # Make sign_out request.
        response = self.request(url, 'GET')

        if response:
            self.token = None
            logger.info('Sign Out Succesfull!')

        else:
            logger.error(
                "Fail to make Sign Out succesfully :(",
                response=response)

    def request(self, url, http_method, **kwargs):
        """
        Sends request to Datary passing config through arguments.

        ===========   =============   ================================
        Parameter     Type            Description
        ===========   =============   ================================
        url           str             destination url
        http_method   str
        ===========   =============   ================================

        Returns:
            content(): if HTTP response between the 200 range

        Raises:
            - Unknown HTTP method
            - Fail request to datary

        """
        try:
            #  HTTP GET Method
            if http_method == 'GET':
                content = requests.get(url, **kwargs)

            # HTTP POST Method
            elif http_method == 'POST':
                content = requests.post(url, **kwargs)

            # HTTP DELETE Method
            elif http_method == 'DELETE':
                content = requests.delete(url, **kwargs)

            # Unkwown HTTP Method
            else:
                logger.error(
                    'Do not know {} as HTTP method'.format(http_method))
                raise Exception(
                    'Do not know {} as HTTP method'.format(http_method))

            # Check for correct request status code.
            if 199 < content.status_code < 300:
                return content
            else:
                logger.error(
                    "Fail Request to datary ",
                    url=url, http_method=http_method,
                    code=content.status_code,
                    text=content.text,
                    kwargs=kwargs)

        # Request Exception
        except RequestException as e:
            logger.error(
                "Fail request to Datary - {}".format(e),
                url=url,
                http_method=http_method,
                requests_args=kwargs)

##########################################################################
#                             Repository Methods
##########################################################################

    def create_repo(self, repo_name=None, repo_category='other', **kwargs):
        """
        Creates repository using Datary's Api

        ==============  =============   ======================================
        Parameter       Type            Description
        ==============  =============   ======================================
        repo_name       str             repo name,
        repo_category   str             repo category name.
        description     str             repo description info.
        visibility      str             public, private, commercial.
        licenseName     str             repo license.
        amount          int             price of the repo in cents if commertial.
        currency        str             currency (by default "eur").
        modality        str             "one-time" | "recurring" (by default)
        interval        str             "day" | "week" | "month" | "year" (by default).
        period          int             number of interval between billing (by default 1).
        ==============  =============   ======================================

        Returns:
            (dict) created repository's description

        """

        if not kwargs.get('repo_uuid'):
            url = urljoin(URL_BASE, "me/repos")
            visibility = kwargs.get('visibility', 'commercial')

            payload = {
                'name': repo_name,
                'category': repo_category if repo_category in self.DATARY_CATEGORIES else 'other',
                'description': kwargs.get('description', '{} description'.format(repo_name)),
                'visibility': visibility if visibility in self.DATARY_VISIBILITY_OPTION else 'commercial',
                'licenseName': kwargs.get('license', 'proprietary'),
                'amount': kwargs.get('amount'),
                'currency':  kwargs.get('currency', 'eur'),
                'modality': kwargs.get('modality', 'recurring'),
                'interval': kwargs.get('interval', 'year'),
                'period': kwargs.get('period', 1),
                # 'defaultInitialization': kwargs.get('initialization', False)
            }

            # Create repo request.
            response = self.request(
                url, 'POST', **{'data': payload, 'headers': self.headers})

        # TODO: Refactor in a future the creation process in API returns a repo
        # description.
        describe_response = self.get_describerepo(
            repo_name=repo_name, **kwargs)
        return describe_response if describe_response else {}

    def get_describerepo(self, repo_uuid=None, repo_name=None, **kwargs):
        """
        ==============  =============   ====================================
        Parameter       Type            Description
        ==============  =============   ====================================
        repo_uuid       str             repository uuid
        repo_name       str             repository name
        ==============  =============   ====================================

        Returns:
            (list or dict) repository with the given repo_uuid.

        """
        logger.info("Getting Datary user repo and wdir uuids")
        url = urljoin(
            URL_BASE,
            "repos/{}".format(repo_uuid) if repo_uuid else "me/repos")

        response = self.request(url, 'GET', **{'headers': self.headers})

        repos_data = response.json() if response else {}
        repo = {}

        # TODO: refactor
        if isinstance(repos_data, list) and (repo_uuid or repo_name):
            for repo_data in repos_data:
                if repo_uuid and repo_data.get('uuid') == repo_uuid:
                    repo = repo_data
                    break

                elif repo_name and repo_data.get('name') == repo_name:
                    repo = repo_data
                    break
        else:
            repo = repos_data

        return repo

    def delete_repo(self, repo_uuid=None, **kwargs):
        """
        Deletes repo using Datary's Api

        ==============  =============   ====================================
        Parameter       Type            Description
        ==============  =============   ====================================
        repo_uuid       str              repository uuid
        repo_name       str             repository name
        ==============  =============   ====================================

        Raises:
            No repo id error

        """
        logger.info("Deleting Datary user repo")

        if not repo_uuid:
            raise ValueError('Must pass the repo uuid to delete the repo.')

        url = urljoin(URL_BASE, "repos/{}".format(repo_uuid))
        response = self.request(url, 'DELETE', **{'headers': self.headers})

        return response.text if response else None

##########################################################################
#                             Filetree Methods
##########################################################################

    def get_commit_filetree(self, repo_uuid, commit_sha1):
        """
        ==============  =============   ====================================
        Parameter       Type            Description
        ==============  =============   ====================================
        repo_uuid       int             repository id
        commit_sha1     str             filetree sha1
        ==============  =============   ====================================

        Returns:
            filetree of all commits done in a repo.

        """
        url = urljoin(URL_BASE, "commits/{}/filetree".format(commit_sha1))

        params = {'namespace': repo_uuid}

        response = self.request(
            url, 'GET', **{'headers': self.headers, 'params': params})

        return response.json() if response else {}

    def get_wdir_filetree(self, wdir_uuid):
        """
        ==============  =============   ====================================
        Parameter       Type            Description
        ==============  =============   ====================================
        wdir_uuid       str             working directory id
        ==============  =============   ====================================

        Returns:
            filetree of a repo workdir.

        """

        url = urljoin(URL_BASE, "workdirs/{}/filetree".format(wdir_uuid))

        response = self.request(url, 'GET', **{'headers': self.headers})

        return response.json() if response else {}

    def get_wdir_changes(self, wdir_uuid=None, **kwargs):
        """
        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str              working directory id
        ================  =============   ====================================

        Returns:
            (dict) changes in workdir.
        """

        # try to take wdir_uuid with kwargs
        if not wdir_uuid:
            wdir_uuid = self.get_describerepo(**kwargs).get('workdir', {}).get('uuid')

        url = urljoin(URL_BASE, "workdirs/{}/changes".format(wdir_uuid))
        response = self.request(url, 'GET', **{'headers': self.headers})

        return response.json() if response else {}

    def format_wdir_changes_to_filetreeformat(self, wdir_changes_tree):
        """
        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_changes_tree dict            working changes tree
        ================  =============   ====================================

        Returns:
            (dict) changes in workdir formatting as filetree format.
        """

        return {os.path.join(item.get('dirname', ''), item.get('basename', '')): item.get('inode', 'unkwown_dataset_uuid') for sublist in force_list(wdir_changes_tree) for item in force_list(sublist)}


##########################################################################
#                             Datasets Methods
##########################################################################

    def get_metadata(self, repo_uuid, dataset_sha1):
        """
        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        repo_uuid         int             repository id
        dataset_sha1  str
        ================  =============   ====================================

        Returns:
            (dict) dataset metadata

        """

        url = urljoin(
            URL_BASE,
            "datasets/{}/metadata".format(dataset_sha1))

        params = {'namespace': repo_uuid}

        response = self.request(
            url, 'GET', **{'headers': self.headers, 'params': params})
        if not response:
            logger.error(
                "Not metadata retrieved.",
                repo_uuid=repo_uuid,
                dataset_sha1=dataset_sha1)

        return response.json() if response else {}

    def get_original(self, dataset_sha1, repo_uuid='', wdir_uuid=''):
        """
        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        repo_uuid         str             repository uuid
        wdir_uuid         str             workingdir uuid
        dataset_sha1      str             dataset uuid
        ================  =============   ====================================

        Returns:
            (dict) dataset original data
        """
        response = None

        if (repo_uuid or wdir_uuid) and dataset_sha1:

            url = urljoin(URL_BASE, "datasets/{}/original".format(dataset_sha1))
            params = exclude_empty_values({'namespace': repo_uuid, 'scope': wdir_uuid})
            response = self.request(url, 'GET', **{'headers': self.headers, 'params': params})
            if not response:
                logger.error(
                    "Not original retrieved.",
                    repo_uuid=repo_uuid,
                    dataset_sha1=dataset_sha1)

        return response.json() if response else {}

    def get_dataset_uuid(self, wdir_uuid, path='', filename=''):
        """
        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        repo_uuid         str             repo uuid.
        wdir_uuid         str             wdir uuid.
        path              str             path of the file in Datary.
        filename          str             filename of the file in Datary.
        ================  =============   ====================================

        Returns:
            (string) uuid dataset original data
        """

        filepath = os.path.join(path, filename)

        # retrieve wdir filetree
        wdir_filetree = self.get_wdir_filetree(wdir_uuid)

        # retrieve last commit filetree
        wdir_changes_filetree = self.format_wdir_changes_to_filetreeformat(self.get_wdir_changes(wdir_uuid).values())

        # retrieve dataset uuid
        dataset_uuid = get_element(wdir_changes_filetree, filepath) or get_element(wdir_filetree, filepath) or {}

        return dataset_uuid

    version 2
    http://{{host}}/workdirs/{{wd-pub}}/filetree?pathname=test1/test2(test3/file_test123





##########################################################################
#                             Categories Methods
##########################################################################

    def get_categories(self):
        """
        Returns:
            the predefined categories in the system.

        """
        url = urljoin(URL_BASE, "search/categories")

        response = self.request(url, 'GET', **{'headers': self.headers})
        return response.json() if response else self.DATARY_CATEGORIES

##########################################################################
#                            Commits method's
##########################################################################

    COMMIT_ACTIONS = {'add': '+', 'update': 'm', 'delete': '-'}

    def commit(self, repo_uuid, commit_message):
        """
        Commits changes.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        repo_uuid         int             repository uuid
        commit_message    str             message commit description
        ================  =============   ====================================

        """
        logger.info("Commiting changes...")

        url = urljoin(URL_BASE, "repos/{}/commits".format(repo_uuid))

        response = self.request(
            url,
            'POST',
            **{'data': {
                'message': commit_message},
                'headers': self.headers})
        if response:
            logger.info("Changes commited")

    def recollect_last_commit(self, repo={}):
        """
        Parameter:
            (dict) repo

        Raises:
            - No repo found with given uuid.
            - No sha1 in repo.
            - No filetree in repo.
            - Fail retrieving last commit.

        Returns:
            Last commit in list with the path, filename, sha1.

        """
        ftree = {}
        last_commit = []
        filetree_matrix = []

        try:

            # retrieve last filetree commited
            ftree = self.get_last_commit_filetree(repo)

            # List of Path | Filename | Sha1
            filetree_matrix = nested_dict_to_list("", ftree)

            # Take metadata to retrieve sha-1 and compare with
            for path, filename, dataset_sha1 in filetree_matrix:
                metadata = self.get_metadata(repo.get('uuid'), dataset_sha1)
                # append format path | filename | data (not required) | sha1
                last_commit.append((path, filename, None, metadata.get("sha1")))
        except Exception:
            logger.warning(
                "Fail recollecting last commit",
                repo=repo,
                ftree={},
                last_commit=[])

        return last_commit

    def get_last_commit_filetree(self, repo={}):

        ftree = {}

        try:
            # check if have the repo.
            if 'apex' not in repo:
                repo.update(self.get_describerepo(repo.get('uuid')))

            if not repo:
                logger.info('No repo found with this uuid', repo=repo)
                raise Exception(
                    "No repo found with uuid {}".format(repo.get('uuid')))

            last_sha1 = repo.get("apex", {}).get("commit")

            if not last_sha1:
                logger.info('Repo hasnt any sha1 in apex', repo=repo)
                raise Exception(
                    'Repo hasnt any sha1 in apex {}'.format(repo))

            ftree = self.get_commit_filetree(repo.get('uuid'), last_sha1)
            if not ftree:
                logger.info('No ftree found with repo_uuid',
                            repo=repo, sha1=last_sha1)
                raise Exception(
                    "No ftree found with repo_uuid {} , last_sha1 {}".
                    format(repo.get('uuid'), last_sha1))

        except Exception as ex:
            logger.warning("Fail getting last commit - {}".format(ex), repo=repo)

        return ftree

    def make_index(self, lista):
        """
        Transforms commit list into an index using path + filename as key
        and sha1 as value.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        lista             list            list of commits
        ================  =============   ====================================

        """
        result = {}
        for path, filename, data, sha1 in lista:
            result[os.path.join(path, filename)] = {'path': path,
                                                    'filename': filename,
                                                    'data': data,
                                                    'sha1': sha1}
        return result

    def compare_commits(self, last_commit, actual_commit, changes=[], strict=True, **kwargs):
        """
        Compare two commits and retrieve hot elements to change
        and the action to do.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        last_commit       list            [path|filename|sha1]
        actual_commit     list            [path|filename|sha1]
        ================  =============   ====================================

        Returns:
            Difference between both commits.

        Raises:
            Fail comparing commits.

        """
        difference = {'update': [], 'delete': [], 'add': []}

        try:
            # make index
            last_index = self.make_index(last_commit)
            actual_index = self.make_index(actual_commit)

            last_index_keys = list(last_index.keys())

            for key, value in actual_index.items():

                # Update
                if key in last_index_keys:
                    last_index_sha1 = last_index.get(key, {}).get('sha1')
                    # sha1 values don't match
                    if value.get('sha1') != last_index_sha1:
                        difference['update'].append(value)

                    # Pop last inspected key
                    last_index_keys.remove(key)

                # Add
                else:
                    difference['add'].append(value)

            # Remove elements when stay in last_commit and not in actual if
            # stric is enabled else omit this
            difference['delete'] = [last_index.get(
                key, {}) for key in last_index_keys if strict]

        except Exception as ex:
            logger.error(
                'Fail comparing commits - {}'.format(ex),
                last_commit=last_commit, actual_commit=actual_commit)

        return difference

    def add_commit(self, wdir_uuid, last_commit, actual_commit, **kwargs):
        """
        Given the last commit and actual commit,
        takes hot elements to ADD, UPDATE or DELETE.

        ================  =============   =======================
        Parameter         Type            Description
        ================  =============   =======================
        wdir_uuid         str             working directory uuid
        last_commit       list            [path|filename|sha1]
        actual_commit     list            [path|filename|sha1]
        ================  =============   =======================

        """
        # compares commits and retrieves hot elements -> new, modified, deleted
        hot_elements = self.compare_commits(
            last_commit, actual_commit, strict=kwargs.get('strict', False))

        logger.info(
            "There are hot elements to commit ({} add; {} update; {} delete;"
            .format(
                len(hot_elements.get('add')),
                len(hot_elements.get('update')),
                len(hot_elements.get('delete'))))

        for element in hot_elements.get('add', []):
            self.add_file(wdir_uuid, element)

        for element in hot_elements.get('update', []):
            self.modify_file(wdir_uuid, element, **kwargs)

        for element in hot_elements.get('delete', []):
            self.delete_file(wdir_uuid, element)

    def commit_diff_tostring(self, difference):
        """
        Turn commit comparation done to visual print format.

        Returns:
            (str) result: ([+|u|-] filepath/filename)

        Raises:
            Fail translating commit differences to string

        """
        result = ""

        if difference:
            try:
                result = "Changes at {}\n".format(datetime.now().strftime("%d/%m/%Y-%H:%M"))
                for action in sorted(list(self.COMMIT_ACTIONS.keys())):
                    result += "{}\n*****************\n".format(action.upper())
                    for commit_data in difference.get(action, []):
                        result += "{}  {}/{}\n".format(
                            self.COMMIT_ACTIONS.get(action, '?'),
                            commit_data.get('path'),
                            commit_data.get('filename'))
            except Exception as ex:
                logger.error(
                    'Fail translating commit differences to string - {}'.format(ex))

        return result

##########################################################################
#                              Add methods
##########################################################################

    def add_dir(self, wdir_uuid, path, dirname):
        """
        (DEPRECATED)
        Creates a new directory.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             working directory uuid
        path              str             path to the new directory
        dirname           str             name of the new directory
        ================  =============   ====================================

        """
        logger.info(
            "Add new directory to Datary.",
            path=os.path.join(path, dirname))

        url = urljoin(URL_BASE, "workdirs/{}/changes".format(wdir_uuid))

        payload = {"action": "add",
                   "filemode": 40000,
                   "dirname": path,
                   "basename": dirname}

        response = self.request(
            url, 'POST', **{'data': payload, 'headers': self.headers})
        if response:
            logger.info(
                "Directory has been created in workdir.",
                url=url,
                wdir_uuid=wdir_uuid,
                dirname=dirname)

    def add_file(self, wdir_uuid, element):
        """
        Adds a new file.
        If the file is to be created within a new path
        it also creates all necesary directories.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             working directory uuid
        element           list            [path, filename, data, sha1]
        dirname           str             directory name
        ================  =============   ====================================

         """
        logger.info("Add new file to Datary.")

        url = urljoin(URL_BASE, "workdirs/{}/changes".format(wdir_uuid))

        payload = {"action": "add",
                   "filemode": 100644,
                   "dirname": element.get('path'),
                   "basename": element.get('filename'),
                   "kern": json.dumps(element.get('data', {}).get('kern')),
                   "meta": json.dumps(element.get('data', {}).get('meta'))}

        response = self.request(
            url, 'POST', **{'data': payload, 'headers': self.headers})
        if response:
            logger.info(
                "File has been Added to workdir.",
                wdir_uuid=wdir_uuid,
                element=element)

##########################################################################
#                              Modify methods
##########################################################################
    _ROWZERO_HEADER_CONFIDENCE_VALUE = 0.5

    def modify_request(self, wdir_uuid, element):
        url = urljoin(URL_BASE, "workdirs/{}/changes".format(wdir_uuid))

        payload = {
            "action": "modify",
            "filemode": 100644,
            "dirname": element.get('path'),
            "basename": element.get('filename'),
            "kern": json.dumps(element.get('data', {}).get('kern')),
            "meta": json.dumps(element.get('data', {}).get('meta'))}

        response = self.request(url, 'POST', **{'data': payload, 'headers': self.headers})

        if response:
            logger.info(
                "File has been modified in workdir.",
                url=url,
                payload=payload,
                element=element)

    def modify_file(self, wdir_uuid, element, mod_style='override', **kwargs):
        """
        Modifies an existing file in Datary.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             working directory uuid
        element           list            [path, filename, data, sha1]
        mod_style         str o callable  'override' by default,
                                          'update-append' mod_style,
                                          'update-row' mod_style,
                                           <callable> function to use.
        ================  =============   ====================================
        """
        # Override method
        if mod_style == 'override':
            self.override_file(wdir_uuid, element)

        # Update Append method
        elif mod_style == 'update-append':
            self.update_append_file(wdir_uuid, element)

        # TODO: ADD update-row method

        # Inject own modify solution method
        elif callable(mod_style):
            mod_style(wdir_uuid, element, callback_request=self.modify_request)

        # Default..
        else:
            logger.error('NOT VALID modify style passed.')

    def override_file(self, wdir_uuid, element):
        """
        Override an existing file in Datary.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             working directory uuid
        element           list            [path, filename, data, sha1]
        ================  =============   ====================================

        """
        logger.info("Override an existing file in Datary.")

        self.modify_request(wdir_uuid, element)

    def update_append_file(self, wdir_uuid, element):
        """
        Update append an existing file in Datary.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             working directory uuid
        element           list            [path, filename, data, sha1]
        ================  =============   ====================================

        """
        logger.info("Update an existing file in Datary.")
        try:

            # retrieve original dataset_uuid from datary
            stored_dataset_uuid = self.get_dataset_uuid(
                 wdir_uuid=wdir_uuid,
                 path=element.get('path', ''),
                 filename=element.get('filename', ''))

            # retrieve original dataset from datary
            stored_element = self.get_original(
                dataset_uuid=stored_dataset_uuid,
                wdir_uuid=wdir_uuid)

            # update elements
            self.update_elements(stored_element, element)

            # send modify request
            self.modify_request(wdir_uuid, stored_element)

        except Exception as ex:
            logger.error('Update append failed - {}'.format(ex))

    def update_elements(self, stored_element, update_element):
        """
        Update one element with other.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        stored_element    dict            element stored to update
        update_element    dict            update element
        ================  =============   ====================================
        """
        logger.info("Updating element")

        # LIST stored element
        if isinstance(stored_element.get('kern'), list) and isinstance(update_element.get('data', {}).get('kern'), list):

            # Check if rowzero is header..
            is_rowzero_header = self._calculate_rowzero_header_confindence(
                    stored_element.get('meta', {}).get('axisHeaders', {}).get('*'),  # stored element axisheader
                    stored_element.get('kern', [[]])[0]              # stored element first row
                    )

            # update kern
            stored_element['kern'] = self._update_arrays_elements(
                original_array=stored_element.get('kern', {}),
                update_array=update_element.get('data', {}).get('kern', {}),
                is_rowzero_header=is_rowzero_header
                )

            # update meta
            stored_element['meta'] = self._reload_meta(
                kern=stored_element.get('kern', {}),
                original_meta=stored_element.get('meta', {}),
                path_key='',
                rowzero_header=is_rowzero_header)

        # DICT stored element
        elif isinstance(stored_element.get('kern'), dict) and isinstance(update_element.get('data', {}).get('kern'), dict):
            element_keys = set([re.split("[0-9]", x)[0] for x in list(flatten(update_element.get('data', {}).get('kern'), sep='/').keys())])

            # add element
            for element_keypath in element_keys:
                pass

                is_rowzero_header = self._calculate_rowzero_header_confindence(
                    stored_element.get('meta', {}).get('axisHeaders', {}).get(element_keypath, []),        # stored element axisheader
                    get_element(stored_element.get('kern', {}), element_keypath+"/0") or []                # stored element first row
                    )

                # update kern
                updated_keypath_array = self._update_arrays_elements(
                    original_array=get_element(stored_element.get('kern', {}), element_keypath) or [],
                    update_array=get_element(update_element.get('data', {}).get('kern', {}), element_keypath),
                    is_rowzero_header=is_rowzero_header
                    )

                # Update meta
                updated_keypath_meta = self._reload_meta(
                    kern=updated_keypath_array,
                    original_meta=stored_element.get('meta', {}),
                    path_key=element_keypath,
                    rowzero_header=is_rowzero_header)

                # add updated kern to keypath
                add_element(stored_element.get('kern', {}), element_keypath, updated_keypath_array)

                # add updated meta to stored element
                add_element(stored_element, 'meta', updated_keypath_meta, override=True)

        else:
            logger.warning('Not compatible type elements to update {} - {}'.format(
                type(stored_element.get('kern')).__name__,
                type(update_element.get('data', {}).get('kern')).__name__,))

    def _reload_meta(self, kern, original_meta, path_key='', is_rowzero_header=False):
        """
        Reload element meta by default.
            - update axisheaders
            - update dimension

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        kern              dict or list    element kern.
        original_meta     dict            element meta.
        path_key          str             path keys to array in a dict.
        is_rowzero_header    boolean         Rowzero contains array header.
        ================  =============   ====================================
        """
        updated_meta = {}
        updated_meta.update(original_meta)

        try:
            rows = get_element(kern, '/'.join(exclude_empty_values([path_key])))
            row_zero = rows[0]

            # Update axisheaders
            axisheaders = {
                path_key + "": [x[0] for x in rows],
                path_key + "/*": row_zero if is_rowzero_header else ['Header'] * len(row_zero)
            }

            add_element(updated_meta, '/'.join(["axisHeaders", path_key]), axisheaders, override=True)

            # Update dimension
            add_element(updated_meta, '/'.join(["dimension", path_key]), get_dimension(kern), override=True)

        except Exception as ex:
            logger.error('Fail reloading meta.. - {}'.format(ex))
            updated_meta = original_meta

        return updated_meta

    def _calculate_rowzero_header_confindence(self, axisheaders, row_zero):
        """
        Calculate the cofidence index if the first row contains headers comparing
        this headers with the axisheaders. If this index is lower than the
        _ROWZERO_HEADER_CONFIDENCE_VALUE we think that the data in row_zero doesnt contains
        headers.
        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        axisheaders       list            list of axisheaders
        rowzero           list            list with firt row of the element.
        ================  =============   ====================================
        """

        row_zero_header_confidence = 0

        if axisheaders:
            row_zero_header_confidence = float(sum([axisheaders.count(x) for x in row_zero]))/len(axisheaders)

        return row_zero_header_confidence > self._ROWZERO_HEADER_CONFIDENCE_VALUE

    def _merge_headers(self, header1, header2):
        """
        Merge 2 headers without losing the header 1 order and removing repeated
        elements from header2 in header1.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        header1           list            1st element header, must maintain its order
        header2           list            2nd element header
        ================  =============   ====================================
        """

        return remove_list_duplicates(header1 + header2)

    def _update_arrays_elements(self, original_array, update_array, is_rowzero_header):

        result = []

        # row zero contains data headers
        if is_rowzero_header:
            merged_headers = self._merge_headers(original_array[0], update_array[0])
            result.append(merged_headers)

            for data in original_array[1:]:
                result.append(dict2orderedlist(zip(original_array[0], data), merged_headers, default=''))

            for data in update_array[1:]:
                result.append(dict2orderedlist(zip(update_array[0], data), merged_headers, default=''))

        # row zero contains data headers
        else:
            original_array.extend(update_array)

        return result


##########################################################################
#                              Delete methods
##########################################################################

    def delete_dir(self, wdir_uuid, path, dirname):
        """
        Delete directory.
        -- NOT IN USE --

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             working directory uuid
        path              str             path to directory
        dirname           str             directory name
        ================  =============   ====================================

        """
        logger.info(
            "Delete directory in workdir.",
            wdir_uuid=wdir_uuid,
            dirname=dirname,
            path=os.path.join(path, dirname))

        url = urljoin(URL_BASE, "workdirs/{}/changes".format(wdir_uuid))

        payload = {"action": "delete",
                   "filemode": 40000,
                   "dirname": path,
                   "basename": dirname}

        response = self.request(
            url, 'GET', **{'data': payload, 'headers': self.headers})

        # TODO: No delete folder permitted yet.
        if response:
            logger.info(
                "Directory has been deleted in workdir",
                wdir_uuid=wdir_uuid,
                url=url,
                payload=payload)

    def delete_file(self, wdir_uuid, element):
        """
        Delete file.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             working directory uuid
        element           Dic             element with path & filename
        ================  =============   ====================================

        """
        logger.info(
            "Delete file in workdir.",
            element=element,
            wdir_uuid=wdir_uuid)

        url = urljoin(URL_BASE, "workdirs/{}/changes".format(wdir_uuid))

        payload = {"action": "remove",
                   "filemode": 100644,
                   "dirname": element.get('path'),
                   "basename": element.get('filename')
                   }

        response = self.request(
            url, 'POST', **{'data': payload, 'headers': self.headers})
        if response:
            logger.info("File has been deleted.")

    def delete_inode(self, wdir_uuid, inode):
        """
        Delete using inode.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             working directory uuid
        inode             str             directory or file inode.
        ================  =============   ====================================
        """
        logger.info("Delete by inode.", wdir_uuid=wdir_uuid, inode=inode)

        url = urljoin(URL_BASE, "workdirs/{}/changes".format(wdir_uuid))
        payload = {"action": "remove", "inode": inode}

        response = self.request(
            url, 'POST', **{'data': payload, 'headers': self.headers})

        if response:
            logger.info("Element has been deleted using inode.")

    def clear_index(self, wdir_uuid):
        """
        Clear changes in repo.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             working directory uuid
        ================  =============   ====================================
        """

        url = urljoin(URL_BASE, "workdirs/{}/changes".format(wdir_uuid))

        response = self.request(url, 'DELETE', **{'headers': self.headers})
        if response:
            logger.info("Repo index has been cleared.")
            return True

        return False

    def clean_repo(self, repo_uuid, **kwargs):
        """
        Clean repo data from datary & algolia.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        repo_uuid         str             repository uuid
        ================  =============   ====================================
        """
        repo = self.get_describerepo(repo_uuid=repo_uuid, **kwargs)

        if repo:
            wdir_uuid = repo.get('workdir', {}).get('uuid')

            # clear changes
            self.clear_index(wdir_uuid)

            # get filetree
            filetree = self.get_wdir_filetree(wdir_uuid)

            # flatten filetree to list
            flatten_filetree = flatten(filetree, sep='/')

            # TODO: REMOVE THIS SHIT..
            # add foo file, workingdir cant be empty..
            foo_element = {
                'path': '',
                'filename': 'foo_{}'.format(random.randint(0, 99)),
                'data': {'meta': {}, 'kern': []}
                }

            self.add_file(wdir_uuid, foo_element)
            self.commit(repo_uuid, 'Commit foo file to clean repo')

            for path in [x for x in flatten_filetree.keys() if '__self' not in x]:
                self.delete_file(wdir_uuid, {'path': "/".join(path.split('/')[:-1]), 'filename': path.split('/')[-1]})

            self.commit(repo_uuid, 'Commit delete all files to clean repo')

        else:
            logger.error('Fail to clean_repo, repo not found in datary.')

##########################################################################
#                              Members methods
##########################################################################

    def get_members(self, member_uuid='', member_name='', **kwargs):
        """
        ==============  =============   ====================================
        Parameter       Type            Description
        ==============  =============   ====================================
        member_uuid     str             member_uuid uuid
        member_name     str             member_name
        limit           int             number of results limit (default=20)
        ==============  =============   ====================================

        Returns:
            (list or dict) repository with the given member_uuid or member_name.
        """

        logger.info("Getting Datary members")

        url = urljoin(
            URL_BASE,
            "search/members")

        response = self.request(url, 'GET', **{'headers': self.headers, 'params': {'limit': kwargs.get('limit', 20)}})

        members_data = response.json() if response else {}
        member = {}

        if member_name or member_uuid:
            for member_data in members_data:
                if member_uuid and member_data.get('uuid') == member_uuid:
                    member = member_data
                    break

                elif member_name and member_data.get('username') == member_name:
                    member = member_data
                    logger.info(member)
                    break
        else:
            member = members_data

        return member


class Datary_SizeLimitException(Exception):
    """
    Datary exception for size limit exceed
    """

    def __init__(self, msg='', src_path='', size=-1):
        self.msg = msg
        self.src_path = src_path
        self.size = size

    def __str__(self):
        return "{};{};{}".format(self.msg, self.src_path, self.size)
