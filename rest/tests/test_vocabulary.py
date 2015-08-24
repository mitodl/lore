"""
REST tests relating to vocabularies and terms
"""

from __future__ import unicode_literals

import logging

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
)

from rest.tests.base import (
    RESTAuthTestCase,
    RESTTestCase,
    REPO_BASE,
    as_json,
)
from rest.serializers import (
    VocabularySerializer,
    TermSerializer,
)
from taxonomy.models import Vocabulary, Term
from learningresources.models import LearningResourceType

log = logging.getLogger(__name__)


class TestVocabulary(RESTTestCase):
    """
    REST tests relating to vocabularies and terms
    """
    def test_vocabularies(self):
        """
        Test for Vocabulary
        """

        original_count = self.get_vocabularies(self.repo.slug)['count']

        self.create_vocabulary(self.repo.slug)
        vocabularies = self.get_vocabularies(self.repo.slug)
        self.assertEqual(
            original_count + 1,
            self.get_vocabularies(self.repo.slug)['count'],
        )
        new_vocab_slug = vocabularies['results'][0]['slug']

        self.get_vocabulary(self.repo.slug, new_vocab_slug)

        # test PUT and PATCH
        input_dict = {
            'name': 'other name',
            'description': 'description',
            'required': True,
            'weight': 1000,
            'vocabulary_type': 'f',
            'learning_resource_types': [],
        }

        # patch with missing slug
        self.patch_vocabulary(
            self.repo.slug, "missing", {'name': 'rename'},
            expected_status=HTTP_404_NOT_FOUND
        )

        output_dict = self.patch_vocabulary(
            self.repo.slug, new_vocab_slug, {'name': 'rename'})
        new_vocab_slug = output_dict['slug']
        self.assertEqual('rename',
                         Vocabulary.objects.get(slug=new_vocab_slug).name)

        # put with missing slug
        self.put_vocabulary(self.repo.slug, "missing slug", input_dict,
                            expected_status=HTTP_404_NOT_FOUND)

        output_dict = self.put_vocabulary(
            self.repo.slug, new_vocab_slug, input_dict)
        new_vocab_slug = output_dict['slug']
        self.assertEqual(input_dict['name'],
                         Vocabulary.objects.get(slug=new_vocab_slug).name)
        # never created a duplicate
        self.assertEqual(
            original_count + 1,
            self.get_vocabularies(self.repo.slug)['count'],
        )

        # try deleting a vocabulary
        self.delete_vocabulary(self.repo.slug, new_vocab_slug)

        vocabularies = self.get_vocabularies(self.repo.slug)
        self.assertEqual(
            original_count,
            self.get_vocabularies(self.repo.slug)['count'],
        )

        # test missing repository
        self.create_vocabulary("missing", input_dict,
                               expected_status=HTTP_404_NOT_FOUND)
        self.get_vocabularies("missing", expected_status=HTTP_404_NOT_FOUND)
        self.get_vocabulary("missing", "missing",
                            expected_status=HTTP_404_NOT_FOUND)

        # test create with missing required
        dict_missing_required = dict(input_dict)
        del dict_missing_required['required']
        dict_missing_required['name'] = 'new name'

        # we should get a 400 error for validation
        self.create_vocabulary(self.repo.slug, dict_missing_required,
                               expected_status=HTTP_400_BAD_REQUEST)

        # as anonymous
        self.logout()
        self.get_vocabularies("missing", expected_status=HTTP_403_FORBIDDEN)
        self.get_vocabulary("missing", "missing",
                            expected_status=HTTP_403_FORBIDDEN)

    def test_other_vocabulary(self):
        """Test that two repositories have two different vocabularies"""

        # missing fields
        input_dict = {
            'name': 'name',
            'description': 'description',
        }
        self.create_vocabulary(self.repo.slug, input_dict,
                               expected_status=HTTP_400_BAD_REQUEST)

        other_repo_dict = self.create_repository(input_dict)

        vocab1_dict = {
            'name': 'name',
            'description': 'description',
            'required': True,
            'weight': 1000,
            'vocabulary_type': 'f',
        }

        resp = self.client.post(
            '{repo_base}{repo_slug}/'.format(
                repo_slug=self.repo.slug,
                repo_base=REPO_BASE,
            ),
            vocab1_dict,
        )
        self.assertEqual(HTTP_405_METHOD_NOT_ALLOWED, resp.status_code)

        vocab1_dict = self.create_vocabulary(self.repo.slug, vocab1_dict)

        # test duplicate vocabulary
        self.create_vocabulary(self.repo.slug, vocab1_dict,
                               expected_status=HTTP_400_BAD_REQUEST)

        vocab2_dict = dict(vocab1_dict)
        vocab2_dict['name'] = 'name 2'  # use different name to change slug

        # The assertions in self.create_vocabulary assume these don't exist.
        del vocab2_dict['slug']
        del vocab2_dict['id']
        del vocab2_dict['terms']

        vocab2_dict = self.create_vocabulary(
            other_repo_dict['slug'], vocab2_dict)

        repositories = self.get_repositories()
        self.assertEqual(2, repositories['count'])

        vocabularies = self.get_vocabularies(self.repo.slug)
        self.assertEqual(2, vocabularies['count'])

        vocabularies = self.get_vocabularies(other_repo_dict['slug'])
        self.assertEqual(2, vocabularies['count'])

        # test getting both vocabs with both repos
        self.get_vocabulary(
            self.repo.slug, vocab1_dict['slug'])
        self.get_vocabulary(
            other_repo_dict['slug'], vocab1_dict['slug'],
            expected_status=HTTP_404_NOT_FOUND
        )
        self.get_vocabulary(
            self.repo.slug, vocab2_dict['slug'],
            expected_status=HTTP_404_NOT_FOUND
        )
        self.get_vocabulary(
            other_repo_dict['slug'], vocab2_dict['slug']
        )

    def test_vocabulary_filter_type(self):
        """Test filtering learning resource types for vocabularies"""
        self.create_vocabulary(self.repo.slug)

        learning_resource_type = LearningResourceType.objects.first()

        # in the future this should be handled within the API
        Vocabulary.objects.first().learning_resource_types.add(
            learning_resource_type
        )

        resp = self.client.get("{repo_base}{repo_slug}/vocabularies/".format(
            repo_base=REPO_BASE,
            repo_slug=self.repo.slug,
        ))
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertEqual(2, as_json(resp)['count'])

        resp = self.client.get(
            "{repo_base}{repo_slug}"
            "/vocabularies/?type_name={name}".format(
                repo_base=REPO_BASE,
                repo_slug=self.repo.slug,
                name=learning_resource_type.name,
            ))
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertEqual(1, as_json(resp)['count'])

        resp = self.client.get(
            "{repo_base}{repo_slug}"
            "/vocabularies/?type_name={name}".format(
                repo_base=REPO_BASE,
                repo_slug=self.repo.slug,
                name="missing",
            ))
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertEqual(0, as_json(resp)['count'])

    def test_term(self):
        """Test REST access for term"""
        vocab1_slug = self.create_vocabulary(self.repo.slug)['slug']
        terms = self.get_terms(self.repo.slug, vocab1_slug)
        self.assertEqual(1, terms['count'])  # There's always "not set."

        input_dict = {
            "label": "term label",
            "weight": 3000,
        }
        self.create_term(self.repo.slug, "missing", input_dict,
                         expected_status=HTTP_404_NOT_FOUND)
        self.create_term("missing", vocab1_slug, input_dict,
                         expected_status=HTTP_404_NOT_FOUND)
        output_dict = self.create_term(self.repo.slug, vocab1_slug, input_dict)
        new_term_slug = output_dict['slug']
        self.get_term(self.repo.slug, vocab1_slug, new_term_slug)

        # delete a term
        self.delete_term(
            self.repo.slug, vocab1_slug, new_term_slug
        )

        terms = self.get_terms(self.repo.slug, vocab1_slug)
        self.assertEqual(1, terms['count'])

        self.create_term(self.repo.slug, vocab1_slug, input_dict)
        # create term again, prevented due to duplicate data validation error
        self.create_term(
            self.repo.slug, vocab1_slug, input_dict,
            expected_status=HTTP_400_BAD_REQUEST
        )

        # patch with missing slug fails
        self.patch_term(
            self.repo.slug, vocab1_slug, "missing", {'label': 'rename'},
            expected_status=HTTP_404_NOT_FOUND
        )

        # successful rename (this changes the slug too)
        output_dict = self.patch_term(
            self.repo.slug, vocab1_slug, new_term_slug, {'label': 'rename'}
        )
        new_term_slug = output_dict['slug']
        self.assertEqual('rename',
                         Term.objects.get(slug=new_term_slug).label)

        # put with missing slug
        self.put_term(
            self.repo.slug, vocab1_slug, "missing slug", input_dict,
            expected_status=HTTP_404_NOT_FOUND
        )

        # successful PUT
        output_dict = self.put_term(
            self.repo.slug, vocab1_slug, new_term_slug, input_dict
        )
        new_term_slug = output_dict['slug']
        self.assertEqual(input_dict['label'],
                         Term.objects.get(slug=new_term_slug).label)
        # never created a duplicate
        self.assertEqual(
            2,
            self.get_terms(self.repo.slug, vocab1_slug)['count'],
        )

        # test missing repository slug
        self.get_term(self.repo.slug, vocab1_slug, "missing",
                      expected_status=HTTP_404_NOT_FOUND)
        self.get_terms(self.repo.slug, "missing",
                       expected_status=HTTP_404_NOT_FOUND)

        # create a second vocabulary so we can test that terms only show up
        # with their parent vocabularies
        vocab2_slug = self.create_vocabulary(
            self.repo.slug,
            {
                "name": "other name",
                "description": "description",
                "required": True,
                "vocabulary_type": Vocabulary.FREE_TAGGING,
                "weight": 1000,
            }
        )['slug']

        self.delete_term(self.repo.slug, vocab1_slug, new_term_slug)
        # verify deleting twice fails with 404
        self.delete_term(self.repo.slug, vocab1_slug, new_term_slug,
                         expected_status=HTTP_404_NOT_FOUND)

        # make sure terms only show up under vocabulary they belong to
        input_dict = {
            "label": "term label 2",
            "weight": 3000,
        }

        term1 = self.create_term(self.repo.slug, vocab1_slug, input_dict)
        term2 = self.create_term(self.repo.slug, vocab2_slug, input_dict)
        self.create_term(self.repo.slug, vocab1_slug)

        # vocab1 has the term previously created and term1
        # that was just created
        # vocab2 has only term2
        terms = self.get_terms(self.repo.slug, vocab1_slug)
        self.assertEqual(3, terms['count'])
        terms = self.get_terms(self.repo.slug, vocab2_slug)
        self.assertEqual(2, terms['count'])

        # we shouldn't find term2 in vocab1 and vice versa
        self.get_term(self.repo.slug, vocab1_slug, term1['slug'])
        self.get_term(self.repo.slug, vocab1_slug, term2['slug'],
                      expected_status=HTTP_404_NOT_FOUND)
        self.get_term(self.repo.slug, vocab2_slug, term1['slug'],
                      expected_status=HTTP_404_NOT_FOUND)
        self.get_term(self.repo.slug, vocab2_slug, term2['slug'])

        # as anonymous
        self.logout()
        self.get_term(self.repo.slug, vocab1_slug, term1['slug'],
                      expected_status=HTTP_403_FORBIDDEN)
        self.get_term(self.repo.slug, vocab1_slug, term2['slug'],
                      expected_status=HTTP_403_FORBIDDEN)
        self.get_term(self.repo.slug, vocab2_slug, term1['slug'],
                      expected_status=HTTP_403_FORBIDDEN)
        self.get_term(self.repo.slug, vocab2_slug, term2['slug'],
                      expected_status=HTTP_403_FORBIDDEN)

    def test_delete_propagation(self):
        """Test delete propagation"""

        # create two vocabularies
        vocab1_slug = self.create_vocabulary(
            self.repo.slug,
            {
                "name": "name1",
                "description": "description",
                "required": True,
                "vocabulary_type": Vocabulary.FREE_TAGGING,
                "weight": 1000,
            }
        )['slug']
        vocab2_slug = self.create_vocabulary(
            self.repo.slug,
            {
                "name": "name2",
                "description": "description",
                "required": True,
                "vocabulary_type": Vocabulary.FREE_TAGGING,
                "weight": 1000,
            }
        )['slug']

        # create term1 within vocab1 and term2 within vocab2
        term1_slug = self.create_term(
            self.repo.slug,
            vocab1_slug,
            {
                "label": "name1",
                "weight": 1000
            }
        )['slug']
        term2_slug = self.create_term(
            self.repo.slug,
            vocab2_slug,
            {
                "label": "name2",
                "weight": 1000
            }
        )['slug']

        # test delete propagation
        self.delete_vocabulary(self.repo.slug, vocab1_slug)

        # vocab1 was deleted and term1 is now also deleted
        # but term2 and vocab2 are not deleted
        self.get_term(self.repo.slug, vocab1_slug, term1_slug,
                      expected_status=HTTP_404_NOT_FOUND)
        self.get_term(self.repo.slug, vocab1_slug, term2_slug,
                      expected_status=HTTP_404_NOT_FOUND)
        self.get_term(self.repo.slug, vocab2_slug, term1_slug,
                      expected_status=HTTP_404_NOT_FOUND)
        self.get_term(self.repo.slug, vocab2_slug, term2_slug)

    def test_vocabulary_pagination(self):
        """Test pagination for collections"""
        # Ordering by ID is required, because due to the ORM's laziness,
        # grabbing vocabs[0] later might return a different item.
        vocabs = Vocabulary.objects.filter(
            repository__id=self.repo.id).order_by('id')
        # The curator status vocabulary will be there by default, and
        # should still be the only thing there.
        self.assertEqual(vocabs.count(), 1)
        expected = [
            VocabularySerializer(Vocabulary.objects.create(
                repository=self.repo,
                name="name{i}".format(i=i),
                description="description",
                required=True,
                vocabulary_type=Vocabulary.FREE_TAGGING,
                weight=1000,
            )).data for i in range(40)]

        # The curator status vocabulary will be first by ID.
        expected.append(VocabularySerializer(vocabs[0]).data)
        expected.sort(key=lambda x: x["id"])

        resp = self.client.get(
            '{repo_base}{repo_slug}/vocabularies/'.format(
                repo_slug=self.repo.slug,
                repo_base=REPO_BASE,
            ))
        self.assertEqual(HTTP_200_OK, resp.status_code)
        vocabularies = as_json(resp)
        self.assertEqual(41, vocabularies['count'])

        # Sort both lists in preparation for comparisons.
        expected.sort(key=lambda x: x["id"])
        from_api = sorted(vocabularies['results'], key=lambda x: x["id"])

        expected_count = 20
        self.assertEqual(expected_count, len(from_api))
        self.assertEqual(
            expected[:expected_count],
            from_api,
        )

        resp = self.client.get(
            '{repo_base}{repo_slug}/vocabularies/?page=2'.format(
                repo_slug=self.repo.slug,
                repo_base=REPO_BASE,
            ))
        self.assertEqual(HTTP_200_OK, resp.status_code)
        vocabularies = as_json(resp)
        from_api = sorted(vocabularies['results'], key=lambda x: x["id"])
        self.assertEqual(expected_count, len(from_api))
        self.assertEqual(41, vocabularies['count'])
        self.assertEqual(
            from_api,
            expected[expected_count:expected_count*2],
        )

    def test_term_pagination(self):
        """Test pagination for collections"""

        vocab_slug = self.create_vocabulary(self.repo.slug)['slug']
        not_set = self.get_terms(self.repo.slug, vocab_slug)["results"][0]

        expected = [
            self.create_term(
                self.repo.slug,
                vocab_slug,
                {
                    "label": "name{i}".format(i=i),
                    "weight": 1000,
                }
            ) for i in range(40)]
        expected.insert(0, not_set)
        terms = self.get_terms(self.repo.slug, vocab_slug)
        self.assertEqual(41, terms['count'])
        self.assertEqual([TermSerializer(x).data for x in expected[:20]],
                         terms['results'])

        resp = self.client.get(
            '{repo_base}{repo_slug}/vocabularies/'
            '{vocab_slug}/terms/?page=2'.format(
                repo_slug=self.repo.slug,
                repo_base=REPO_BASE,
                vocab_slug=vocab_slug,
            ))
        self.assertEqual(HTTP_200_OK, resp.status_code)
        terms = as_json(resp)
        self.assertEqual(41, terms['count'])
        self.assertEqual([TermSerializer(x).data
                          for x in expected[20:40]], terms['results'])

    def test_immutable_fields_vocabulary(self):
        """Test immutable fields for vocabulary"""

        vocab_dict = {
            'id': -1,
            'name': 'name 2',
            'slug': 'name 2',
            'description': 'description',
            'required': True,
            'weight': 1000,
            'vocabulary_type': 'f',
            'repository': -9,
            'learning_resource_types': [],
            'terms': [self.DEFAULT_TERM_DICT],
        }

        def assert_not_changed(new_dict):
            """Check that fields have not changed"""
            # These keys should be different since they are immutable or set by
            # the serializer.
            for field in ('id', 'slug', 'terms'):
                self.assertNotEqual(vocab_dict[field], new_dict[field])

            # repository is set internally and should not show up in output.
            self.assertNotIn('repository', new_dict)
            vocabulary = Vocabulary.objects.get(slug=new_dict['slug'])
            self.assertEqual(self.repo.id, vocabulary.repository.id)

        result = self.create_vocabulary(self.repo.slug, vocab_dict,
                                        skip_assert=True)
        assert_not_changed(result)
        vocab_slug = result['slug']

        result = self.patch_vocabulary(
            self.repo.slug, vocab_slug, vocab_dict, skip_assert=True)
        assert_not_changed(result)
        vocab_slug = result['slug']

        result = self.put_vocabulary(
            self.repo.slug, vocab_slug, vocab_dict, skip_assert=True)
        assert_not_changed(result)

    def test_immutable_fields_term(self):
        """Test immutable fields for term"""
        vocab_slug = self.create_vocabulary(
            self.repo.slug, skip_assert=True)['slug']
        term_dict = {
            'id': -1,
            'slug': 'sluggy',
            "label": "term label",
            "weight": 3000,
            "vocabulary": -1,
        }

        def assert_not_changed(new_dict):
            """Check that fields have not changed"""
            # These keys should be different since they are immutable or set by
            # the serializer.
            for field in ('id', 'slug'):
                self.assertNotEqual(term_dict[field], new_dict[field])

            # vocabulary is set internally and should not show up in output.
            self.assertNotIn('vocabulary', new_dict)
            term = Term.objects.get(slug=new_dict['slug'])
            self.assertEqual(vocab_slug, term.vocabulary.slug)

        result = self.create_term(
            self.repo.slug, vocab_slug, term_dict, skip_assert=True
        )
        assert_not_changed(result)
        term_slug = result['slug']

        result = self.put_term(
            self.repo.slug, vocab_slug, term_slug,
            term_dict, skip_assert=True
        )
        assert_not_changed(result)
        term_slug = result['slug']

        result = self.patch_term(
            self.repo.slug, vocab_slug, term_slug, term_dict, skip_assert=True
        )
        assert_not_changed(result)

    def test_vocabulary_learning_resource_types(self):
        """
        Test learning_resource_types field on vocabularies
        """
        vocab_dict = self.create_vocabulary(self.repo.slug)
        vocab_slug = vocab_dict['slug']
        self.assertEqual([], vocab_dict['learning_resource_types'])

        # PATCH invalid or missing type
        self.patch_vocabulary(self.repo.slug, vocab_slug, {
            "learning_resource_types": ["chapter"]
        }, expected_status=HTTP_400_BAD_REQUEST)
        self.patch_vocabulary(self.repo.slug, vocab_slug, {
            "learning_resource_types": [""]
        }, expected_status=HTTP_400_BAD_REQUEST)
        self.patch_vocabulary(self.repo.slug, vocab_slug, {
            "learning_resource_types": None
        }, expected_status=HTTP_400_BAD_REQUEST)

        # duplicates are removed
        result_dict = self.patch_vocabulary(self.repo.slug, vocab_slug, {
            "learning_resource_types": ["example", "example"]
        }, skip_assert=True)
        self.assertEqual(["example"], result_dict['learning_resource_types'])

        # we can make it empty again
        self.patch_vocabulary(self.repo.slug, vocab_slug, {
            "learning_resource_types": []
        })

        # PUT works
        vocab_copy = dict(self.DEFAULT_VOCAB_DICT)
        vocab_copy['learning_resource_types'] = ['example']
        self.put_vocabulary(self.repo.slug, vocab_slug, vocab_copy)

        # test POST new vocabulary with invalid type
        self.delete_vocabulary(self.repo.slug, vocab_slug)
        vocab_copy['learning_resource_types'] = ['invalid']
        self.create_vocabulary(self.repo.slug, vocab_copy,
                               expected_status=HTTP_400_BAD_REQUEST)

        # POST with valid type
        vocab_copy['learning_resource_types'] = ['example']
        vocab_slug = self.create_vocabulary(
            self.repo.slug, vocab_copy)['slug']

        self.assertEqual(
            ['example'],
            self.get_vocabulary(
                self.repo.slug, vocab_slug)['learning_resource_types'])


class TestVocabularyAuthorization(RESTAuthTestCase):
    """
    Tests relating to term and vocabulary authorization
    """
    def test_vocabulary_create(self):
        """Test create vocabulary"""
        self.logout()
        self.login(self.curator_user.username)
        original_count = self.get_vocabularies(self.repo.slug)['count']

        self.create_vocabulary(self.repo.slug)
        self.assertEqual(
            original_count + 1,
            self.get_vocabularies(self.repo.slug)['count'],
        )

        # login as author which doesn't have manage_taxonomy permissions
        self.logout()
        self.login(self.author_user.username)

        vocab_dict = dict(self.DEFAULT_VOCAB_DICT)
        vocab_dict['name'] = 'other_name'  # prevent name collision

        # author does not have create access
        self.create_vocabulary(
            self.repo.slug, vocab_dict,
            expected_status=HTTP_403_FORBIDDEN
        )

        # make sure at least view_repo is needed
        self.logout()
        self.login(self.user_norepo.username)

        self.create_vocabulary(self.repo.slug, vocab_dict,
                               expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.create_vocabulary(self.repo.slug, vocab_dict,
                               expected_status=HTTP_403_FORBIDDEN)

    def test_vocabulary_put_patch(self):
        """Test update vocabulary"""
        vocab_slug = self.create_vocabulary(self.repo.slug)['slug']

        self.logout()
        self.login(self.curator_user.username)

        self.patch_vocabulary(self.repo.slug, vocab_slug,
                              self.DEFAULT_VOCAB_DICT)
        self.put_vocabulary(self.repo.slug, vocab_slug,
                            self.DEFAULT_VOCAB_DICT)

        # login as author which doesn't have manage_taxonomy permissions
        self.logout()
        self.login(self.author_user.username)

        self.patch_vocabulary(self.repo.slug, vocab_slug,
                              self.DEFAULT_VOCAB_DICT,
                              expected_status=HTTP_403_FORBIDDEN)
        self.put_vocabulary(self.repo.slug, vocab_slug,
                            self.DEFAULT_VOCAB_DICT,
                            expected_status=HTTP_403_FORBIDDEN)

        # make sure at least view_repo is needed
        self.logout()
        self.login(self.user_norepo.username)
        self.patch_vocabulary(self.repo.slug, vocab_slug,
                              self.DEFAULT_VOCAB_DICT,
                              expected_status=HTTP_403_FORBIDDEN)
        self.put_vocabulary(self.repo.slug, vocab_slug,
                            self.DEFAULT_VOCAB_DICT,
                            expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.patch_vocabulary(self.repo.slug, vocab_slug,
                              self.DEFAULT_VOCAB_DICT,
                              expected_status=HTTP_403_FORBIDDEN)
        self.put_vocabulary(self.repo.slug, vocab_slug,
                            self.DEFAULT_VOCAB_DICT,
                            expected_status=HTTP_403_FORBIDDEN)

    def test_vocabulary_delete(self):
        """Test delete vocabulary"""
        vocab_slug = self.create_vocabulary(self.repo.slug)['slug']

        # login as author which doesn't have manage_taxonomy permissions
        self.logout()
        self.login(self.author_user.username)

        self.delete_vocabulary(self.repo.slug, vocab_slug,
                               expected_status=HTTP_403_FORBIDDEN)

        # curator does have manage_taxonomy permissions
        self.logout()
        self.login(self.curator_user.username)
        self.delete_vocabulary(self.repo.slug, vocab_slug)

        # vocab is missing
        self.create_term(self.repo.slug, vocab_slug,
                         expected_status=HTTP_404_NOT_FOUND)
        self.delete_vocabulary(self.repo.slug, vocab_slug,
                               expected_status=HTTP_404_NOT_FOUND)

        # recreate vocab so we can delete it
        vocab_slug = self.create_vocabulary(self.repo.slug)['slug']

        # author has view_repo but delete not allowed
        self.logout()
        self.login(self.author_user.username)
        self.delete_vocabulary(self.repo.slug, vocab_slug,
                               expected_status=HTTP_403_FORBIDDEN)

        # make sure at least view_repo is needed
        self.logout()
        self.login(self.user_norepo.username)

        self.delete_vocabulary(self.repo.slug, vocab_slug,
                               expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.delete_vocabulary(self.repo.slug, vocab_slug,
                               expected_status=HTTP_403_FORBIDDEN)

    def test_vocabulary_get(self):
        """Test get vocabulary and vocabularies"""
        original_count = self.get_vocabularies(self.repo.slug)['count']
        vocab_slug = self.create_vocabulary(self.repo.slug)['slug']

        # author_user has view_repo permissions
        self.logout()
        self.login(self.author_user.username)
        self.assertEqual(
            original_count + 1,
            self.get_vocabularies(self.repo.slug)['count'],
        )
        self.get_vocabulary(self.repo.slug, vocab_slug)

        # user_norepo has no view_repo permission
        self.logout()
        self.login(self.user_norepo.username)
        self.get_vocabularies(
            self.repo.slug, expected_status=HTTP_403_FORBIDDEN)
        self.get_vocabulary(self.repo.slug, vocab_slug,
                            expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.get_vocabularies(
            self.repo.slug, expected_status=HTTP_403_FORBIDDEN)
        self.get_vocabulary(self.repo.slug, vocab_slug,
                            expected_status=HTTP_403_FORBIDDEN)

    def test_term_create(self):
        """Test create term"""
        vocab_slug = self.create_vocabulary(self.repo.slug)['slug']
        original_count = self.get_terms(self.repo.slug, vocab_slug)['count']

        # curator has manage_taxonomy permission
        self.logout()
        self.login(self.curator_user.username)

        self.create_term(self.repo.slug, vocab_slug)
        self.assertEqual(original_count + 1, self.get_terms(
            self.repo.slug, vocab_slug)['count'])

        # login as author which doesn't have manage_taxonomy permissions
        self.logout()
        self.login(self.author_user.username)

        term_dict = dict(self.DEFAULT_TERM_DICT)
        term_dict['label'] = 'other_name'  # prevent name collision

        # author does not have create access
        self.create_term(
            self.repo.slug, vocab_slug, term_dict,
            expected_status=HTTP_403_FORBIDDEN
        )

        # make sure at least view_repo is needed
        self.logout()
        self.login(self.user_norepo.username)
        self.create_term(
            self.repo.slug, vocab_slug, term_dict,
            expected_status=HTTP_403_FORBIDDEN
        )

        # as anonymous
        self.logout()
        self.create_term(
            self.repo.slug, vocab_slug, term_dict,
            expected_status=HTTP_403_FORBIDDEN
        )

    def test_term_put_patch(self):
        """Test update term"""
        vocab_slug = self.create_vocabulary(self.repo.slug)['slug']
        term_slug = self.create_term(self.repo.slug, vocab_slug)['slug']

        self.logout()
        self.login(self.curator_user.username)

        self.patch_term(self.repo.slug, vocab_slug, term_slug,
                        self.DEFAULT_TERM_DICT)
        self.put_term(self.repo.slug, vocab_slug, term_slug,
                      self.DEFAULT_TERM_DICT)

        # login as author which doesn't have manage_taxonomy permissions
        self.logout()
        self.login(self.author_user.username)

        self.patch_term(self.repo.slug, vocab_slug, term_slug,
                        self.DEFAULT_TERM_DICT,
                        expected_status=HTTP_403_FORBIDDEN)
        self.put_term(self.repo.slug, vocab_slug, term_slug,
                      self.DEFAULT_TERM_DICT,
                      expected_status=HTTP_403_FORBIDDEN)

        # make sure at least view_repo is needed
        self.logout()
        self.login(self.user_norepo.username)

        self.patch_term(self.repo.slug, vocab_slug, term_slug,
                        self.DEFAULT_TERM_DICT,
                        expected_status=HTTP_403_FORBIDDEN)
        self.put_term(self.repo.slug, vocab_slug, term_slug,
                      self.DEFAULT_TERM_DICT,
                      expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.patch_term(self.repo.slug, vocab_slug, term_slug,
                        self.DEFAULT_TERM_DICT,
                        expected_status=HTTP_403_FORBIDDEN)
        self.put_term(self.repo.slug, vocab_slug, term_slug,
                      self.DEFAULT_TERM_DICT,
                      expected_status=HTTP_403_FORBIDDEN)

    def test_term_delete(self):
        """Test delete term"""
        vocab_slug = self.create_vocabulary(self.repo.slug)['slug']
        term_slug = self.create_term(self.repo.slug, vocab_slug)['slug']

        # login as author which doesn't have manage_taxonomy permissions
        self.logout()
        self.login(self.author_user.username)

        self.delete_term(self.repo.slug, vocab_slug, term_slug,
                         expected_status=HTTP_403_FORBIDDEN)

        # curator does have manage_taxonomy permissions
        self.logout()
        self.login(self.curator_user.username)
        self.delete_term(self.repo.slug, vocab_slug, term_slug)

        # make sure at least view_repo is needed
        self.logout()
        self.login(self.user_norepo.username)
        self.delete_term(self.repo.slug, vocab_slug, term_slug,
                         expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.delete_term(self.repo.slug, vocab_slug, term_slug,
                         expected_status=HTTP_403_FORBIDDEN)

    def test_term_get(self):
        """Test retrieve term"""
        vocab_slug = self.create_vocabulary(self.repo.slug)['slug']
        term_slug = self.create_term(self.repo.slug, vocab_slug)['slug']
        expected_count = self.get_terms(self.repo.slug, vocab_slug)['count']

        # author_user has view_repo permissions
        self.logout()
        self.login(self.author_user.username)
        self.assertEqual(expected_count, self.get_terms(
            self.repo.slug, vocab_slug)['count'])
        self.get_term(self.repo.slug, vocab_slug, term_slug)

        # user_norepo has no view_repo permission
        self.logout()
        self.login(self.user_norepo.username)
        self.get_terms(self.repo.slug, vocab_slug,
                       expected_status=HTTP_403_FORBIDDEN)
        self.get_term(self.repo.slug, vocab_slug, term_slug,
                      expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.get_terms(self.repo.slug, vocab_slug,
                       expected_status=HTTP_403_FORBIDDEN)
        self.get_term(self.repo.slug, vocab_slug, term_slug,
                      expected_status=HTTP_403_FORBIDDEN)
