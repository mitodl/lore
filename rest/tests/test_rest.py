"""
Unit tests for REST api
"""
from __future__ import unicode_literals

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
)

from learningresources.models import Repository
from taxonomy.models import Vocabulary, Term

from rest.serializers import (
    RepositorySerializer,
    VocabularySerializer,
    TermSerializer,
)
from .base import (
    RESTTestCase,
    REPO_BASE,
    API_BASE,
    as_json,
)


class TestRest(RESTTestCase):
    """
    REST test
    """

    def test_repositories(self):
        """
        Test for Repository
        """
        repositories = self.get_repositories()
        self.assertEqual(1, repositories['count'])

        self.create_repository()
        repositories = self.get_repositories()
        self.assertEqual(2, repositories['count'])
        repo_slug = repositories['results'][1]['slug']

        # test PUT and PATCH
        input_dict = {
            'name': 'name',
            'description': 'description',
        }
        input_dict_changed = {
            'name': 'name',
            'description': 'changed description',
        }

        # patch with missing slug
        self.patch_repository(
            "missing", {'name': 'rename'},
            expected_status=HTTP_404_NOT_FOUND
        )

        self.patch_repository(
            repo_slug, {'name': 'rename'},
            expected_status=HTTP_405_METHOD_NOT_ALLOWED)

        # put with missing slug
        self.put_repository("missing slug", input_dict,
                            expected_status=HTTP_404_NOT_FOUND)

        self.put_repository(
            repo_slug, input_dict,
            expected_status=HTTP_405_METHOD_NOT_ALLOWED)

        # verify change of data
        self.put_repository(
            repo_slug, input_dict_changed,
            expected_status=HTTP_405_METHOD_NOT_ALLOWED)

        # never created a duplicate
        self.assertEqual(2, Repository.objects.count())

        # call to verify HTTP_OK
        self.get_repository(repo_slug)

        # delete a repository
        self.delete_repository(repo_slug,
                               expected_status=HTTP_405_METHOD_NOT_ALLOWED)

        repositories = self.get_repositories()
        self.assertEqual(2, repositories['count'])

        vocab_slug = self.create_vocabulary(self.repo.slug)['slug']
        vocabularies = self.get_vocabularies(self.repo.slug)
        self.assertEqual(1, vocabularies['count'])

        self.delete_repository(self.repo.slug,
                               expected_status=HTTP_405_METHOD_NOT_ALLOWED)

        self.delete_vocabulary(self.repo.slug, vocab_slug)

        vocabularies = self.get_vocabularies(self.repo.slug)
        self.assertEqual(0, vocabularies['count'])

        self.delete_repository(self.repo.slug,
                               expected_status=HTTP_405_METHOD_NOT_ALLOWED)

        self.get_repositories()
        self.get_repository("missing", expected_status=HTTP_404_NOT_FOUND)

        # as anonymous
        self.logout()
        self.get_repositories(expected_status=HTTP_403_FORBIDDEN)
        self.get_repository("missing", expected_status=HTTP_403_FORBIDDEN)

    def test_vocabularies(self):
        """
        Test for Vocabulary
        """

        vocabularies = self.get_vocabularies(self.repo.slug)
        self.assertEqual(0, vocabularies['count'])

        self.create_vocabulary(self.repo.slug)

        vocabularies = self.get_vocabularies(self.repo.slug)
        self.assertEqual(1, vocabularies['count'])
        new_vocab_slug = vocabularies['results'][0]['slug']

        self.get_vocabulary(self.repo.slug, new_vocab_slug)

        # test PUT and PATCH
        input_dict = {
            'name': 'other name',
            'description': 'description',
            'required': True,
            'weight': 1000,
            'vocabulary_type': 'f',
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
        self.assertEqual(1, Vocabulary.objects.count())

        # try deleting a vocabulary
        self.delete_vocabulary(self.repo.slug, new_vocab_slug)

        vocabularies = self.get_vocabularies(self.repo.slug)
        self.assertEqual(0, vocabularies['count'])

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

        # this is ignored in POST but the assertions assume these don't exist
        del vocab2_dict['slug']
        del vocab2_dict['id']

        vocab2_dict = self.create_vocabulary(
            other_repo_dict['slug'], vocab2_dict)

        repositories = self.get_repositories()
        self.assertEqual(2, repositories['count'])

        vocabularies = self.get_vocabularies(self.repo.slug)
        self.assertEqual(1, vocabularies['count'])

        vocabularies = self.get_vocabularies(other_repo_dict['slug'])
        self.assertEqual(1, vocabularies['count'])

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

    def test_term(self):
        """Test REST access for term"""
        vocab1_slug = self.create_vocabulary(self.repo.slug)['slug']
        terms = self.get_terms(self.repo.slug, vocab1_slug)
        self.assertEqual(0, terms['count'])

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
        self.assertEqual(0, terms['count'])

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
        self.assertEqual(1, Term.objects.count())

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
        self.assertEqual(2, terms['count'])
        terms = self.get_terms(self.repo.slug, vocab2_slug)
        self.assertEqual(1, terms['count'])

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

    def test_repository_pagination(self):
        """Test pagination for collections"""

        expected = [
            self.create_repository(
                {
                    'name': "name{i}".format(i=i),
                    "description": "description"
                }
            ) for i in range(40)]

        repositories = self.get_repositories()

        # 40 we created + self.repo
        self.assertEqual(41, repositories['count'])
        self.assertEqual(
            [RepositorySerializer(
                Repository.objects.get(id=x['id'])).data
             for x in expected[:19]],
            repositories['results'][1:20])

        resp = self.client.get(
            '{repo_base}?page=2'.format(
                repo_base=REPO_BASE,
            ))
        self.assertEqual(HTTP_200_OK, resp.status_code)
        repositories = as_json(resp)
        self.assertEqual(41, repositories['count'])
        self.assertEqual(
            [RepositorySerializer(Repository.objects.get(id=x['id'])).data
             for x in expected[19:39]], repositories['results'])

    def test_vocabulary_pagination(self):
        """Test pagination for collections"""

        expected = [
            self.create_vocabulary(
                self.repo.slug,
                {
                    "name": "name{i}".format(i=i),
                    "description": "description",
                    "required": True,
                    "vocabulary_type": Vocabulary.FREE_TAGGING,
                    "weight": 1000,
                }
            ) for i in range(40)]

        resp = self.client.get(
            '{repo_base}{repo_slug}/vocabularies/'.format(
                repo_slug=self.repo.slug,
                repo_base=REPO_BASE,
            ))
        self.assertEqual(HTTP_200_OK, resp.status_code)
        vocabularies = as_json(resp)
        self.assertEqual(40, vocabularies['count'])
        self.assertEqual([VocabularySerializer(x).data for x in expected[:20]],
                         vocabularies['results'])

        resp = self.client.get(
            '{repo_base}{repo_slug}/vocabularies/?page=2'.format(
                repo_slug=self.repo.slug,
                repo_base=REPO_BASE,
            ))
        self.assertEqual(HTTP_200_OK, resp.status_code)
        vocabularies = as_json(resp)
        self.assertEqual(40, vocabularies['count'])
        self.assertEqual([VocabularySerializer(x).data
                          for x in expected[20:40]], vocabularies['results'])

    def test_term_pagination(self):
        """Test pagination for collections"""

        vocab_slug = self.create_vocabulary(self.repo.slug)['slug']

        expected = [
            self.create_term(
                self.repo.slug,
                vocab_slug,
                {
                    "label": "name{i}".format(i=i),
                    "weight": 1000,
                }
            ) for i in range(40)]

        terms = self.get_terms(self.repo.slug, vocab_slug)
        self.assertEqual(40, terms['count'])
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
        self.assertEqual(40, terms['count'])
        self.assertEqual([TermSerializer(x).data
                          for x in expected[20:40]], terms['results'])

    def test_immutable_fields(self):
        """Test fields which are supposed to be immutable"""

        repo_dict = {
            'id': -1,
            'slug': 'sluggy',
            'name': 'other name',
            'description': 'description',
            'date_created': "2015-01-01",
            'created_by': self.user_norepo.id,
        }
        result = self.create_repository(repo_dict, skip_assert=True)
        # these keys should be different since they are immutable or set by
        # the serializer
        self.assertNotEqual(repo_dict['id'], result['id'])
        self.assertNotEqual(repo_dict['slug'], result['slug'])
        self.assertNotEqual(repo_dict['date_created'], result['date_created'])
        self.assertNotIn('created_by', result)
        repository = Repository.objects.get(slug=result['slug'])
        self.assertEqual(repository.created_by.id, self.user.id)
        repo_dict = result

        vocab_dict = {
            'id': -1,
            'name': 'name 2',
            'slug': 'name 2',
            'description': 'description',
            'required': True,
            'weight': 1000,
            'vocabulary_type': 'f',
            'repository': -9
        }
        result = self.create_vocabulary(repo_dict['slug'], vocab_dict,
                                        skip_assert=True)
        # these keys should be different since they are immutable or set by
        # the serializer
        self.assertNotEqual(vocab_dict['id'], result['id'])
        self.assertNotEqual(vocab_dict['slug'], result['slug'])
        self.assertNotIn('repository', result)
        vocabulary = Vocabulary.objects.get(slug=result['slug'])
        self.assertEqual(repository.id, vocabulary.repository.id)
        vocab_dict = result

        term_dict = {
            'id': -1,
            'slug': 'sluggy',
            "label": "term label",
            "weight": 3000,
            "vocabulary": -1,
        }
        result = self.create_term(
            repo_dict['slug'], vocab_dict['slug'], term_dict,
            skip_assert=True
        )
        # these keys should be different since they are immutable or set by
        # the serializer
        self.assertNotEqual(term_dict['id'], result['id'])
        self.assertNotEqual(term_dict['slug'], result['slug'])
        self.assertNotIn('vocabulary', result)
        term = Term.objects.get(slug=result['slug'])
        self.assertEqual(vocabulary.id, term.vocabulary.id)

    def test_root(self):
        """
        Test root of API
        """
        resp = self.client.get(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)
        resp = self.client.post(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)
        resp = self.client.head(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)
        resp = self.client.patch(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)
        resp = self.client.put(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)
        resp = self.client.options(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)

        self.logout()
        resp = self.client.get(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)
        resp = self.client.post(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)
        resp = self.client.head(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)
        resp = self.client.patch(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)
        resp = self.client.put(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)
        resp = self.client.options(API_BASE)
        self.assertEqual(HTTP_404_NOT_FOUND, resp.status_code)
