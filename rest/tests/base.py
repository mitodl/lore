"""
LORE test case
"""

from __future__ import unicode_literals
import json

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
)
from rest_framework.reverse import reverse
from django.db.models import Count
from django.contrib.auth.models import User, Permission

from importer.tasks import import_file
from learningresources.tests.base import LoreTestCase
from learningresources.api import get_resources
from roles.api import assign_user_to_repo_group
from roles.permissions import GroupTypes

API_BASE = '/api/v1/'
REPO_BASE = '/api/v1/repositories/'


def as_json(resp):
    """Get JSON from response"""
    return json.loads(resp.content.decode('utf-8'))


# pylint: disable=too-many-public-methods, too-many-arguments
class RESTTestCase(LoreTestCase):
    """
    REST test case
    """

    # pylint: disable=dangerous-default-value
    # Do not mutate these fields!
    DEFAULT_REPO_DICT = {
        'name': 'name',
        'description': 'description',
    }
    DEFAULT_VOCAB_DICT = {
        'name': 'name',
        'description': 'description',
        'required': True,
        'weight': 1000,
        'vocabulary_type': 'f',
        'learning_resource_types': [],
    }
    DEFAULT_TERM_DICT = {
        'label': 'term label',
        'weight': 1000,
    }
    DEFAULT_LR_DICT = {
        "learning_resource_type": -1,
        "static_assets": [],
        "title": "Getting Help",
        "description": "x",
        "content_xml": "<vertical />",
        "materialized_path":
            "/course/chapter[4]/sequential[1]/vertical[3]",
        "url_path": "",
        "parent": 93,
        "copyright": "",
        "xa_nr_views": 0,
        "xa_nr_attempts": 0,
        "xa_avg_grade": 0.0,
        "xa_histogram_grade": 0.0
    }

    def assert_options_head(self, url, expected_status):
        """Assert OPTIONS and HEAD"""
        resp = self.client.options(url)
        self.assertEqual(expected_status, resp.status_code)
        if expected_status == HTTP_200_OK:
            # verify output is proper JSON
            as_json(resp)
            self.assertIn("HEAD", resp['ALLOW'])
            self.assertIn("OPTIONS", resp['ALLOW'])
            self.assertIn("GET", resp['ALLOW'])

        resp = self.client.head(url)
        self.assertEqual(expected_status, resp.status_code)

    def get_repositories(self, expected_status=HTTP_200_OK):
        """Get list of repositories"""
        url = REPO_BASE
        self.assert_options_head(url, expected_status=expected_status)
        resp = self.client.get(url)
        self.assertEqual(expected_status, resp.status_code)
        if expected_status == HTTP_200_OK:
            return as_json(resp)

    def create_repository(self, repo_dict=DEFAULT_REPO_DICT,
                          expected_status=HTTP_201_CREATED,
                          skip_assert=False):
        """Helper function to create repository"""

        resp = self.client.post(REPO_BASE, repo_dict)
        self.assertEqual(expected_status, resp.status_code)
        if resp.status_code == HTTP_201_CREATED:
            result_dict = as_json(resp)
            if not skip_assert:
                for key, value in repo_dict.items():
                    self.assertEqual(value, result_dict[key])

            self.assertIn(reverse(
                'repository-detail', kwargs={
                    'repo_slug': result_dict['slug'],
                }
            ), resp['Location'])

            return result_dict

    def patch_repository(self, repo_slug, repo_dict,
                         expected_status=HTTP_200_OK, skip_assert=False):
        """Update a repository"""
        resp = self.client.patch(
            '{repo_base}{repo_slug}/'.format(
                repo_slug=repo_slug,
                repo_base=REPO_BASE,
            ),
            json.dumps(repo_dict),
            content_type='application/json',
        )
        self.assertEqual(expected_status, resp.status_code)
        if resp.status_code == HTTP_200_OK:
            result_dict = as_json(resp)
            if not skip_assert:
                for key, value in repo_dict.items():
                    self.assertEqual(value, result_dict[key])
            return result_dict

    def put_repository(self, repo_slug, repo_dict,
                       expected_status=HTTP_200_OK, skip_assert=False):
        """Replace a repository"""
        resp = self.client.put(
            '{repo_base}{repo_slug}/'.format(
                repo_slug=repo_slug,
                repo_base=REPO_BASE,
            ),
            json.dumps(repo_dict),
            content_type='application/json',
        )
        self.assertEqual(expected_status, resp.status_code)
        if resp.status_code == HTTP_200_OK:
            result_dict = as_json(resp)
            if not skip_assert:
                for key, value in repo_dict.items():
                    self.assertEqual(value, result_dict[key])

            return result_dict

    def get_repository(self, repo_slug, expected_status=HTTP_200_OK):
        """Get a repository"""
        url = '{repo_base}{slug}/'.format(
            slug=repo_slug,
            repo_base=REPO_BASE,
        )
        self.assert_options_head(url, expected_status=expected_status)

        resp = self.client.get(url)
        self.assertEqual(expected_status, resp.status_code)
        if expected_status == HTTP_200_OK:
            return as_json(resp)

    def delete_repository(self, repo_slug,
                          expected_status=HTTP_204_NO_CONTENT):
        """Delete a repository"""
        resp = self.client.delete('{repo_base}{slug}/'.format(
            slug=repo_slug,
            repo_base=REPO_BASE,
        ))
        self.assertEqual(expected_status, resp.status_code)

    def get_vocabularies(self, repo_slug, expected_status=HTTP_200_OK):
        """Get list of vocabularies"""
        url = '{repo_base}{slug}/vocabularies/'.format(
            slug=repo_slug,
            repo_base=REPO_BASE,
        )
        self.assert_options_head(url, expected_status=expected_status)
        resp = self.client.get(url)
        self.assertEqual(expected_status, resp.status_code)
        if expected_status == HTTP_200_OK:
            return as_json(resp)

    def create_vocabulary(self, repo_slug, vocab_dict=DEFAULT_VOCAB_DICT,
                          expected_status=HTTP_201_CREATED,
                          skip_assert=False):
        """Create a new vocabulary"""
        resp = self.client.post(
            '{repo_base}{slug}/vocabularies/'.format(
                slug=repo_slug,
                repo_base=REPO_BASE,
            ), vocab_dict)
        self.assertEqual(expected_status, resp.status_code)
        if resp.status_code == HTTP_201_CREATED:
            result_dict = as_json(resp)
            if not skip_assert:
                for key, value in vocab_dict.items():
                    self.assertEqual(value, result_dict[key])

            self.assertIn(reverse(
                'vocabulary-detail', kwargs={
                    'repo_slug': repo_slug,
                    'vocab_slug': result_dict['slug'],
                }
            ), resp['Location'])

            return result_dict

    def patch_vocabulary(self, repo_slug, vocab_slug, vocab_dict,
                         expected_status=HTTP_200_OK, skip_assert=False):
        """Update a vocabulary"""
        resp = self.client.patch(
            '{repo_base}{repo_slug}/'
            'vocabularies/{vocab_slug}/'.format(
                repo_slug=repo_slug,
                vocab_slug=vocab_slug,
                repo_base=REPO_BASE,
            ),
            json.dumps(vocab_dict),
            content_type='application/json'
        )
        self.assertEqual(expected_status, resp.status_code)
        if resp.status_code == HTTP_200_OK:
            result_dict = as_json(resp)
            if not skip_assert:
                for key, value in vocab_dict.items():
                    self.assertEqual(value, result_dict[key])
            return result_dict

    def put_vocabulary(self, repo_slug, vocab_slug, vocab_dict,
                       expected_status=HTTP_200_OK, skip_assert=False):
        """Replace a vocabulary"""
        resp = self.client.put(
            '{repo_base}{repo_slug}/'
            'vocabularies/{vocab_slug}/'.format(
                repo_slug=repo_slug,
                vocab_slug=vocab_slug,
                repo_base=REPO_BASE,
            ),
            json.dumps(vocab_dict),
            content_type='application/json',
        )
        self.assertEqual(expected_status, resp.status_code)
        if resp.status_code == HTTP_200_OK:
            result_dict = as_json(resp)
            if not skip_assert:
                for key, value in vocab_dict.items():
                    self.assertEqual(value, result_dict[key])
            return result_dict

    def get_vocabulary(self, repo_slug, vocab_slug,
                       expected_status=HTTP_200_OK):
        """Get a vocabulary"""
        url = '{repo_base}{repo_slug}/vocabularies/{vocab_slug}/'.format(
            repo_slug=repo_slug,
            vocab_slug=vocab_slug,
            repo_base=REPO_BASE,
        )
        self.assert_options_head(url, expected_status=expected_status)
        resp = self.client.get(url)
        self.assertEqual(expected_status, resp.status_code)
        if expected_status == HTTP_200_OK:
            return as_json(resp)

    def delete_vocabulary(self, repo_slug, vocab_slug,
                          expected_status=HTTP_204_NO_CONTENT):
        """Delete a vocabulary"""
        resp = self.client.delete(
            '{repo_base}{repo_slug}/'
            'vocabularies/{vocab_slug}/'.format(
                repo_slug=repo_slug,
                vocab_slug=vocab_slug,
                repo_base=REPO_BASE,
            )
        )
        self.assertEqual(expected_status, resp.status_code)

    def get_terms(self, repo_slug, vocab_slug,
                  expected_status=HTTP_200_OK):
        """Get list of terms"""
        url = '{repo_base}{repo_slug}/vocabularies/{vocab_slug}/terms/'.format(
            repo_slug=repo_slug,
            vocab_slug=vocab_slug,
            repo_base=REPO_BASE,
        )
        self.assert_options_head(url, expected_status=expected_status)
        resp = self.client.get(url)
        self.assertEqual(expected_status, resp.status_code)
        if expected_status == HTTP_200_OK:
            return as_json(resp)

    def create_term(self, repo_slug, vocab_slug, term_dict=DEFAULT_TERM_DICT,
                    expected_status=HTTP_201_CREATED, skip_assert=False):
        """Create a new vocabulary"""
        resp = self.client.post(
            '{repo_base}{repo_slug}/'
            'vocabularies/{vocab_slug}/terms/'.format(
                repo_slug=repo_slug,
                vocab_slug=vocab_slug,
                repo_base=REPO_BASE,
            ), term_dict)
        self.assertEqual(expected_status, resp.status_code)
        if resp.status_code == HTTP_201_CREATED:
            result_dict = as_json(resp)
            if not skip_assert:
                for key, value in term_dict.items():
                    self.assertEqual(value, result_dict[key])

            self.assertIn(reverse(
                'term-detail', kwargs={
                    'term_slug': result_dict['slug'],
                    'vocab_slug': vocab_slug,
                    'repo_slug': repo_slug,
                }
            ), resp['Location'])

            return result_dict

    def patch_term(self, repo_slug, vocab_slug, term_slug, term_dict,
                   expected_status=HTTP_200_OK, skip_assert=False):
        """Update a term"""
        resp = self.client.patch(
            '{repo_base}{repo_slug}/'
            'vocabularies/{vocab_slug}/'
            'terms/{term_slug}/'.format(
                repo_slug=repo_slug,
                vocab_slug=vocab_slug,
                term_slug=term_slug,
                repo_base=REPO_BASE,
            ),
            json.dumps(term_dict),
            content_type='application/json',
        )
        self.assertEqual(expected_status, resp.status_code)
        if resp.status_code == HTTP_200_OK:
            result_dict = as_json(resp)
            if not skip_assert:
                for key, value in term_dict.items():
                    self.assertEqual(value, result_dict[key])
            return result_dict

    def put_term(self, repo_slug, vocab_slug, term_slug, term_dict,
                 expected_status=HTTP_200_OK, skip_assert=False):
        """Replace a term"""
        resp = self.client.put(
            '{repo_base}{repo_slug}/'
            'vocabularies/{vocab_slug}/'
            'terms/{term_slug}/'.format(
                repo_slug=repo_slug,
                vocab_slug=vocab_slug,
                term_slug=term_slug,
                repo_base=REPO_BASE,
            ),
            json.dumps(term_dict),
            content_type='application/json',
        )
        self.assertEqual(expected_status, resp.status_code)
        if resp.status_code == HTTP_200_OK:
            result_dict = as_json(resp)
            if not skip_assert:
                for key, value in term_dict.items():
                    self.assertEqual(value, result_dict[key])
            return result_dict

    def get_term(self, repo_slug, vocab_slug, term_slug,
                 expected_status=HTTP_200_OK):
        """Get a term"""
        url = (
            '{repo_base}{repo_slug}/'
            'vocabularies/{vocab_slug}/terms/{term_slug}/'.format(
                repo_slug=repo_slug,
                vocab_slug=vocab_slug,
                term_slug=term_slug,
                repo_base=REPO_BASE,
            )
        )
        self.assert_options_head(url, expected_status=expected_status)
        resp = self.client.get(url)
        self.assertEqual(expected_status, resp.status_code)
        if expected_status == HTTP_200_OK:
            return as_json(resp)

    def delete_term(self, repo_slug, vocab_slug, term_slug,
                    expected_status=HTTP_204_NO_CONTENT):
        """Delete a term"""
        resp = self.client.delete(
            '{repo_base}{repo_slug}/'
            'vocabularies/{vocab_slug}/'
            'terms/{term_slug}/'.format(
                repo_slug=repo_slug,
                vocab_slug=vocab_slug,
                term_slug=term_slug,
                repo_base=REPO_BASE,
            )
        )
        self.assertEqual(expected_status, resp.status_code)

    def build_members_url(self, urlfor, repo_slug,
                          username=None, group_type=None):
        """
        Helper function to build a url for members.
        """
        self.assertTrue(urlfor in ['base', 'users', 'groups'])
        base_url = '{api_base}repositories/{repo_slug}/members/'
        users_url = '{base_url}users/{username}/groups/'
        groups_url = '{base_url}groups/{group_type}/users/'
        extra_url = '{base_url}{extra}/'
        url_for_repo = base_url.format(
            api_base=API_BASE,
            repo_slug=repo_slug
        )
        if urlfor == 'base':
            return url_for_repo
        elif urlfor == 'users':
            url = users_url.format(base_url=url_for_repo, username=username)
            if group_type is not None:
                url = extra_url.format(base_url=url, extra=group_type)
            return url
        elif urlfor == 'groups':
            url = groups_url.format(
                base_url=url_for_repo,
                group_type=group_type
            )
            if username is not None:
                url = extra_url.format(base_url=url, extra=username)
            return url

    def get_members(self, urlfor, repo_slug,
                    username=None, group_type=None,
                    expected_status=HTTP_200_OK,
                    skip_options_head_test=False):
        """Get members"""
        url = self.build_members_url(urlfor, repo_slug, username, group_type)
        if not skip_options_head_test:
            self.assert_options_head(url, expected_status=expected_status)
        resp = self.client.get(url)
        self.assertEqual(expected_status, resp.status_code)
        if expected_status == HTTP_200_OK:
            return as_json(resp)

    def create_member(self, urlfor, repo_slug, mem_dict,
                      username=None, group_type=None, reverse_str=None,
                      expected_status=HTTP_201_CREATED, skip_assert=False):
        """
        Create member (meaning assigning an user to a repository group)
        """
        url = self.build_members_url(urlfor, repo_slug, username, group_type)
        resp = self.client.post(url, mem_dict)
        self.assertEqual(expected_status, resp.status_code)
        if resp.status_code == HTTP_201_CREATED:
            result_dict = as_json(resp)
            if not skip_assert:
                for key, value in mem_dict.items():
                    self.assertEqual(value, result_dict[key])
            if reverse_str is not None:
                self.assertIn(reverse(
                    reverse_str, kwargs={
                        'username': username or mem_dict['username'],
                        'group_type': group_type or mem_dict['group_type'],
                        'repo_slug': repo_slug,
                    }
                ), resp['Location'])
            return result_dict

    def delete_member(self, urlfor, repo_slug,
                      username=None, group_type=None,
                      expected_status=HTTP_204_NO_CONTENT):
        """
        Delete member (meaning deleting an user from a repository group)
        """
        url = self.build_members_url(urlfor, repo_slug, username, group_type)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, expected_status)

    def get_learning_resources(self, repo_slug, expected_status=HTTP_200_OK):
        """Get learning resources"""
        url = '{repo_base}{repo_slug}/learning_resources/'.format(
            repo_base=REPO_BASE,
            repo_slug=repo_slug,
        )
        self.assert_options_head(url, expected_status=expected_status)
        resp = self.client.get(url)
        self.assertEqual(expected_status, resp.status_code)
        if resp.status_code == HTTP_200_OK:
            return as_json(resp)

    def get_learning_resource(self, repo_slug, learning_resource_id,
                              expected_status=HTTP_200_OK):
        """Get a learning resource"""
        url = '{repo_base}{repo_slug}/learning_resources/{lr_id}/'.format(
            repo_base=REPO_BASE,
            repo_slug=repo_slug,
            lr_id=learning_resource_id,
        )
        self.assert_options_head(url, expected_status=expected_status)
        resp = self.client.get(url)
        self.assertEqual(expected_status, resp.status_code)
        if resp.status_code == HTTP_200_OK:
            return as_json(resp)

    def patch_learning_resource(
            self, repo_slug, learning_resource_id, lr_dict,
            expected_status=HTTP_200_OK, skip_assert=False):
        """Update a learning resource"""
        resp = self.client.patch(
            '{repo_base}{repo_slug}/'
            'learning_resources/{lr_id}/'.format(
                repo_base=REPO_BASE,
                repo_slug=repo_slug,
                lr_id=learning_resource_id
            ),
            json.dumps(lr_dict),
            content_type='application/json',
        )
        self.assertEqual(expected_status, resp.status_code)
        if resp.status_code == HTTP_200_OK:
            result_dict = as_json(resp)
            if not skip_assert:
                for key, value in lr_dict.items():
                    self.assertEqual(value, result_dict[key])
            return result_dict

    def put_learning_resource(
            self, repo_slug, learning_resource_id, lr_dict,
            expected_status=HTTP_200_OK, skip_assert=False):
        """Update a learning resource"""
        resp = self.client.put(
            '{repo_base}{repo_slug}/'
            'learning_resources/{lr_id}/'.format(
                repo_base=REPO_BASE,
                repo_slug=repo_slug,
                lr_id=learning_resource_id
            ),
            json.dumps(lr_dict),
            content_type='application/json',
        )
        self.assertEqual(expected_status, resp.status_code)
        if resp.status_code == HTTP_200_OK:
            result_dict = as_json(resp)
            if not skip_assert:
                for key, value in lr_dict.items():
                    self.assertEqual(value, result_dict[key])
            return result_dict

    def get_static_assets(self, repo_slug, learning_resource_id,
                          expected_status=HTTP_200_OK):
        """Get static assets for learning resource"""
        url = (
            '{repo_base}{repo_slug}/'
            'learning_resources/{lr_id}/static_assets/'.format(
                repo_base=REPO_BASE,
                repo_slug=repo_slug,
                lr_id=learning_resource_id,
            )
        )
        self.assert_options_head(url, expected_status=expected_status)
        resp = self.client.get(url)
        self.assertEqual(expected_status, resp.status_code)
        if resp.status_code == HTTP_200_OK:
            return as_json(resp)

    def get_static_asset(self, repo_slug, learning_resource_id,
                         static_asset_id,
                         expected_status=HTTP_200_OK):
        """Get a static asset"""
        url = (
            '{repo_base}{repo_slug}/learning_resources/{lr_id}/'
            'static_assets/{sa_id}/'.format(
                repo_base=REPO_BASE,
                repo_slug=repo_slug,
                lr_id=learning_resource_id,
                sa_id=static_asset_id,
            )
        )
        self.assert_options_head(url, expected_status=expected_status)
        resp = self.client.get(url)
        self.assertEqual(expected_status, resp.status_code)
        if resp.status_code == HTTP_200_OK:
            return as_json(resp)

    def import_course_tarball(self, repo):
        """
        Import course.xml into repo and return first LearningResource
        which has any StaticAssets
        """
        tarball_file = self.get_course_single_tarball()
        import_file(
            tarball_file, repo.id, self.user.id)
        return get_resources(repo.id).annotate(
            count_assets=Count('static_assets')
        ).filter(count_assets__gt=0).first()


class RESTAuthTestCase(RESTTestCase):
    """REST tests for authorization"""

    def setUp(self):
        super(RESTAuthTestCase, self).setUp()

        # add_repo_user is another user with add_repo permission but who
        # does not have access to self.repo
        self.add_repo_user = User.objects.create_user(
            username="creator_user", password=self.PASSWORD
        )
        add_repo_perm = Permission.objects.get(codename=self.ADD_REPO_PERM)
        self.add_repo_user.user_permissions.add(add_repo_perm)

        # curator_user doesn't have add_repo but have view_repo permission on
        # self.repo
        self.curator_user = User.objects.create_user(
            username="curator_user", password=self.PASSWORD
        )
        assign_user_to_repo_group(
            self.curator_user, self.repo, GroupTypes.REPO_CURATOR)

        # author_user doesn't have manage_taxonomy permission
        self.author_user = User.objects.create_user(
            username="author_user", password=self.PASSWORD
        )
        assign_user_to_repo_group(
            self.author_user, self.repo, GroupTypes.REPO_AUTHOR
        )
