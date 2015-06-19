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

from learningresources.tests.base import LoreTestCase

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
    }
    DEFAULT_TERM_DICT = {
        'label': 'term label',
        'weight': 1000,
    }

    def assert_options_head(self, url, expected_status):
        """Assert OPTIONS and HEAD"""
        resp = self.client.options(url)
        self.assertEqual(expected_status, resp.status_code)
        # verify output is proper JSON
        as_json(resp)
        self.assertIn("HEAD", resp['ALLOW'])
        self.assertIn("OPTIONS", resp['ALLOW'])
        self.assertIn("GET", resp['ALLOW'])

        resp = self.client.head(url)
        self.assertEqual(expected_status, resp.status_code)

    def get_repositories(self, expected_status=HTTP_200_OK,
                         skip_options_head_test=False):
        """Get list of repositories"""
        url = REPO_BASE
        if not skip_options_head_test:
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

    def get_repository(self, repo_slug, expected_status=HTTP_200_OK,
                       skip_options_head_test=False):
        """Get a repository"""
        url = '{repo_base}{slug}/'.format(
            slug=repo_slug,
            repo_base=REPO_BASE,
        )
        if not skip_options_head_test:
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

    def get_vocabularies(self, repo_slug, expected_status=HTTP_200_OK,
                         skip_options_head_test=False):
        """Get list of vocabularies"""
        url = '{repo_base}{slug}/vocabularies/'.format(
            slug=repo_slug,
            repo_base=REPO_BASE,
        )
        if not skip_options_head_test:
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
                       expected_status=HTTP_200_OK,
                       skip_options_head_test=False):
        """Get a vocabulary"""
        url = '{repo_base}{repo_slug}/vocabularies/{vocab_slug}/'.format(
            repo_slug=repo_slug,
            vocab_slug=vocab_slug,
            repo_base=REPO_BASE,
        )
        if not skip_options_head_test:
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
                  expected_status=HTTP_200_OK,
                  skip_options_head_test=False):
        """Get list of terms"""
        url = '{repo_base}{repo_slug}/vocabularies/{vocab_slug}/terms/'.format(
            repo_slug=repo_slug,
            vocab_slug=vocab_slug,
            repo_base=REPO_BASE,
        )
        if not skip_options_head_test:
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
                 expected_status=HTTP_200_OK,
                 skip_options_head_test=False):
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
        if not skip_options_head_test:
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
