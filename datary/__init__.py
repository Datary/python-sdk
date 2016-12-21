# -*- coding: utf-8 -*-
import os
import json

import requests
from requests import RequestException
import structlog

from urllib.parse import urljoin

logger = structlog.getLogger(__name__)
URL_BASE = "http://api.datary.io/"


class Datary():

    DATARY_VISIBILITY_OPTION = ['public', 'private', 'commercial']
    DATARY_CATEGORIES = [
        "business",
        "climate",
        "consumer",
        "socioeconomics",
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
        "telecomunications",
        "transportation",
        "other"
    ]

    def __init__(self, *args, **kwargs):
        """
        Init Datary class

        Args:
            - username
            - password
            - token
            - headers
        """
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.token = kwargs.get('token')
        self.commit_limit = kwargs.get('commit_limit', 30)

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
        Get user's token, given a user's name and password.

        Args:
            - user: Datary username
            - password: Datary password of the username introduced
        """
        payload = {
            "username": user or self.username,
            "password": password or self.password,
        }

        url = urljoin(URL_BASE, "/connection/signIn")
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = self.request(url, 'POST', **{'headers': self.headers, 'data': payload})

        # Devuelve el token del usuario.
        user_token = str(response.headers.get("x-set-token", ''))

        if user_token:
            self.headers['Authorization'] = 'Bearer {}'.format(user_token)

        return user_token

    def request(self, url, http_method, **kwargs):
        """
        Make request to Datary passing config by arguments.
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
                logger.error('Do not know {} as HTTP method'.format(http_method))
                raise Exception('Do not know {} as HTTP method'.format(http_method))

            # Check for correct request status code.
            if 199 < content.status_code < 300:
                return content
            else:
                logger.error("Fail Request to datary ", url=url, http_method=http_method, code=content.status_code, text=content.text, kwargs=kwargs)

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
        Create repo using Datary's Api

        Args:
            - name: Repository name.
            - description: Repository description info.
            - visibility: Respository visibility.
            - license: Reposotory license.
            - initialization: if True create a new repository file.
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
                # 'defaultInitialization': kwargs.get('initialization', False)
            }

            # Create repo request.
            response = self.request(url, 'POST', **{'data': payload, 'headers': self.headers})

        # TODO: Refactor in a future the creation process in API returns a repo description.
        describe_response = self.get_describerepo(repo_name=repo_name, **kwargs)
        return describe_response if describe_response else {}

    def get_describerepo(self, repo_uuid=None, repo_name=None, **kwargs):
        """
        Returns repo's, given a repo_uuid.

        Args:
            - repo_uuid:
        """
        logger.info("Getting Datary user repo and wdir uuids")
        url = urljoin(URL_BASE, "repos/{}".format(repo_uuid) if repo_uuid else "me/repos")
        response = self.request(url, 'GET', **{'headers': self.headers})
        repos_data = response.json() if response.text else {}
        repo = None

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
        Delete repo using Datary's Api

        Args:
            - repo_uuid: Repository uuid.
        """
        logger.info("Delete Datary user repo")

        if not repo_uuid:
            raise ValueError('Must pass the repo uuid to delete the repo.')
        url = urljoin(URL_BASE, "repos/{}".format(repo_uuid))
        response = self.request(url, 'DELETE', **{'headers': self.headers})
        return response.text

##########################################################################
#                             Filetree Methods
##########################################################################

    def get_commit_filetree(self, repo_uuid, commit_sha1):
        """
        Get the filetree of a repo's commit done.
        """
        url = urljoin(URL_BASE, "commits/{}/filetree".format(commit_sha1))
        params = {'namespace': repo_uuid}
        response = self.request(url, 'GET', **{'headers': self.headers, 'params': params})

        return response.json() if response else {}

    def get_wdir_filetree(self, wdir_uuid):
        """
        Get the filetree of a repo workingdir.
        """

        url = urljoin(URL_BASE, "workingDirs/{}/filetree".format(wdir_uuid))
        response = self.request(url, 'GET', **{'headers': self.headers})

        return response.json() if response else {}

##########################################################################
#                             Datasets Methods
##########################################################################

    def get_metadata(self, repo_uuid, datary_file_sha1):

        url = urljoin(URL_BASE, "datasets/{}/metadata".format(datary_file_sha1))
        params = {'namespace': repo_uuid}
        response = self.request(url, 'GET', **{'headers': self.headers, 'params': params})

        if not response:
            logger.error("Not metadata retrieved.", repo_uuid=repo_uuid, datary_file_sha1=datary_file_sha1)

        return response.json() if response else {}

##########################################################################
#                             Categories Methods
##########################################################################

    def get_categories(self):
        """
        Get categories avaible in the system.
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

        Args:
            - repo_uuid: Repository id.
            - commit_message: Message commit description.

        """
        logger.info("Commiting changes...")
        url = urljoin(URL_BASE, "repos/{}/commits".format(repo_uuid))
        response = self.request(
            url, 'POST', **{'data': {"message": commit_message}, 'headers': self.headers})

        if response:
            logger.info("Changes commited")

    def recollect_last_commit(self, repo={}):
        """
        Take the last commit in list with the path, filename, sha1

        """
        ftree = {}
        last_commit = []
        filetree_matrix = []

        try:
            # check if have the repo.
            if 'apex' not in repo:
                repo.update(self.get_describerepo(repo.get('uuid')))

            if not repo:
                logger.info('No repo found with this uuid', repo=repo)
                raise Exception("No repo found with uuid {}".format(repo.get('uuid')))

            last_sha1 = repo.get("apex", {}).get("commit")

            if not last_sha1:
                logger.info('Repo hasnt any sha1 in apex', repo=repo)
                raise Exception('Repo hasnt any sha1 in apex {}'.format(repo))

            ftree = self.get_commit_filetree(repo.get('uuid'), last_sha1)
            if not ftree:
                logger.info('No ftree found with repo_uuid', repo=repo, sha1=last_sha1)
                raise Exception(
                    "No ftree found with repo_uuid {} , last_sha1 {}".format(repo.get('uuid'), last_sha1))

            # List of Path | Filename | Sha1
            filetree_matrix = nested_dict_to_list("", ftree)

            # Take metadata to retrieve sha-1 and compare with
            for path, filename, datary_file_sha1 in filetree_matrix:
                metadata = self.get_metadata(repo.get('uuid'), datary_file_sha1)
                # append format path | filename | data (not required) | sha1
                last_commit.append((path, filename, None, metadata.get("sha1")))
        except Exception:
            logger.warning(
                "Fail recollecting last commit", repo=repo, ftree={}, last_commit=[])

        return last_commit

    def make_index(self, lista):
        """
        Transforma a commit list into an index using path + filename as key
        and sha1 as value.

        Args:
            - lista: list to tranform in index format.
        """
        result = {}
        for path, filename, data, sha1 in lista:
            result[os.path.join(path, filename)] = {'path': path,
                                                    'filename': filename,
                                                    'data': data,
                                                    'sha1': sha1}
        return result

    def compare_commits(self, last_commit, actual_commit, strict=True):
        """
        Compare two commits and retrieve hot elements to change and the action to do.
        """
        diference = {'update': [], 'delete': [], 'add': []}

        try:
            # make index
            last_index = self.make_index(last_commit)
            actual_index = self.make_index(actual_commit)

            last_index_keys = list(last_index.keys())

            for key, value in actual_index.items():

                # Update
                if key in last_index_keys:

                    if value.get('sha1') != last_index.get(key, {}).get('sha1'):
                        diference['update'].append(value)

                    # Pop last inspected key
                    last_index_keys.remove(key)

                # Add
                else:
                    diference['add'].append(value)

            # Remove elements when stay in last_commit and not in actual if stric is enabled else omit this
            diference['delete'] = [last_index.get(key, {}) for key in last_index_keys if strict]

        except Exception as ex:
            logger.error('Fail compare commits - {}'.format(ex), last_commit=last_commit, actual_commit=actual_commit)

        return diference

    def add_commit(self, wdir_uuid, last_commit, actual_commit, **kwargs):
        """
        Take last commit vs actual commit and take hot elements to ADD or DELETE.

        Args:
            - wdir_uuid:
            - last_commit: list with last commit done files in format path|filename|sha1
            - actual_commit: list with actual files to commit in format path|filename|sha1
        """
        # take hot elements -> new, modified, deleted
        hot_elements = self.compare_commits(last_commit, actual_commit, kwargs.get('strict', False))

        logger.info("There are hot elements to commit ({} add; {} update; {} delete;".format(
            len(hot_elements.get('add')),
            len(hot_elements.get('update')),
            len(hot_elements.get('delete'))))

        for element in hot_elements.get('add', []):
            self.add_file(wdir_uuid, element)

        for element in hot_elements.get('update', []):
            self.modify_file(wdir_uuid, element)

        for element in hot_elements.get('delete', []):
            self.delete_file(wdir_uuid, element)

    def commit_diff_tostring(self, difference):
        """
        Turn commit comparation done to visual print format.
        - Format: [+|u|-] filepath/filename
        """
        result = ""
        try:
            for action in sorted(list(self.COMMIT_ACTIONS.keys())):
                result += "{}\n*****************\n".format(action)
                for commit_data in difference.get(action, []):
                    result += "{}  {}/{}\n".format(
                        self.COMMIT_ACTIONS.get(action, '?'),
                        commit_data.get('path'),
                        commit_data.get('filename'))
        except Exception as ex:
            result = ""
            logger.error('Fail translate commit differences to string - {}'.format(ex))
        return result

##########################################################################
#                              Add methods
##########################################################################
    def add_dir(self, wdir_uuid, path, dirname):
        """
        Adds a new directory. (DEPRECATED)
        Args:

        - wdir_uuid
        - path
        - dirname
        """
        logger.info("Add new directory to Datary.", path=os.path.join(path, dirname))
        url = urljoin(URL_BASE, "workingDirs/{}/changes".format(wdir_uuid))
        payload = {"action": "add", "filemode": 40000, "dirname": path, "basename": dirname}
        response = self.request(url, 'POST', **{'data': payload, 'headers': self.headers})

        if response:
            logger.info("Directory has been created in workingdir.", url=url, wdir_uuid=wdir_uuid, dirname=dirname)

    def add_file(self, wdir_uuid, element):
        """
        Adds a new file.
        The api allow to pass a file with a new path and it manage to create all dirs.
        Args:

        - wdir_uuid
        - element: list with path, name, data, sha1
         """
        logger.info("Add new file to Datary.")
        url = urljoin(URL_BASE, "workingDirs/{}/changes".format(wdir_uuid))
        payload = {"action": "add", "filemode": 100644, "dirname": element.get('path'),
                   "basename": element.get('filename'), "slug": json.dumps(element.get('data'))}

        response = self.request(url, 'POST', **{'data': payload, 'headers': self.headers})
        if response:
            logger.info("File has been Added to workingdir.", wdir_uuid=wdir_uuid, element=element)

##########################################################################
#                              Modify methods
##########################################################################

    def modify_file(self, wdir_uuid, element):
        """
        Modifies an existing file in Datary.
        01 >> Calls Datary API.
        02 >> Double checks whether the file has not yet been modified.
        03 >> If it has already been modified passes, if not modifies it.
        04 >> Logs all possible results.
        """
        logger.info("Modify an existing file in Datary.")

        url = urljoin(URL_BASE, "workingDirs/{}/changes".format(wdir_uuid))
        payload = {"action": "modify", "filemode": 100644, "dirname": element.get('path'),
                   "basename": element.get('filename'), "slug": json.dumps(element.get('data'))}

        response = self.request(
            url, 'POST', **{'data': payload, 'headers': self.headers})

        if response:
            logger.info("File has been modified in workingdir.", url=url, payload=payload, element=element)

##########################################################################
#                              Delete methods
##########################################################################

    def delete_dir(self, wdir_uuid, path, dirname):
        """
        Delete directory.
        -- NOT IN USE --
        """
        logger.info(
            "Delete directory in workingdir.", wdir_uuid=wdir_uuid, dirname=dirname, path=os.path.join(path, dirname))
        url = urljoin(URL_BASE, "workingDirs/{}/changes".format(wdir_uuid))
        payload = {"action": "delete", "filemode": 40000,
                   "dirname": path, "basename": dirname}
        response = self.request(url, 'GET', **{'data': payload, 'headers': self.headers})
        # TODO: No delete permitted yet.
        if response:
            logger.info("Directory has been deleted in workingdir", wdir_uuid=wdir_uuid, url=url, payload=payload)

    def delete_file(self, wdir_uuid, element):
        """
        Delete file.
        -- NOT IN USE --
        """
        logger.info("Delete file in workingdir.", element=element, wdir_uuid=wdir_uuid)
        # TODO: No delete permitted yet.
        raise NotImplementedError('delete_file function is not implemented --NOT IN USE--')

        url = urljoin(URL_BASE, "workingDirs/{}/changes".format(wdir_uuid))
        payload = {"action": "delete", "filemode": 100644, "dirname": element.get('path'),
                   "basename": element.get('filename'), "slug": json.dumps(element.get('data'))}
        response = self.request(url, 'POST', **{'data': payload, 'headers': self.headers})

        if response:
            logger.info("File has been deleted.")


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


def nested_dict_to_list(path, dic):
    """
    Transform nested dict to list
    """
    result = []

    for key, value in dic.items():
        if isinstance(value, dict):
            aux = path + key + "/"
            result.extend(nested_dict_to_list(aux, value))
        else:
            if path.endswith("/"):
                path = path[:-1]

            result.append([path, key, value])
    return result
