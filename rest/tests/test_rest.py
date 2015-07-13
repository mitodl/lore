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

from importer.tasks import import_file
from learningresources.models import (
    Repository,
    LearningResource,
    LearningResourceType,
)
from learningresources.api import get_resources
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
        self.assertEqual(1, as_json(resp)['count'])

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
            Vocabulary.objects.create(
                repository=self.repo,
                name="name{i}".format(i=i),
                description="description",
                required=True,
                vocabulary_type=Vocabulary.FREE_TAGGING,
                weight=1000,
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

    # for some reason Pylint has issues with this name
    # pylint: disable=invalid-name
    def test_immutable_fields_repository(self):
        """Test repository immutable fields"""
        repo_dict = {
            'id': -1,
            'slug': 'sluggy',
            'name': 'other name',
            'description': 'description',
            'date_created': "2015-01-01",
            'created_by': self.user_norepo.id,
        }

        def assert_not_changed(new_dict):
            """Check that fields have not changed"""
            # These keys should be different since they are immutable or set by
            # the serializer.
            for field in ('id', 'slug', 'date_created'):
                self.assertNotEqual(repo_dict[field], new_dict[field])

            # created_by is set internally and should not show up in output.
            self.assertNotIn('created_by', new_dict)
            repository = Repository.objects.get(slug=new_dict['slug'])
            self.assertEqual(repository.created_by.id, self.user.id)

        assert_not_changed(self.create_repository(repo_dict, skip_assert=True))

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

    def test_immutable_fields_learning_resource(self):
        """Test immutable fields for term"""
        self.import_course_tarball(self.repo)
        resource = LearningResource.objects.first()
        lr_id = resource.id

        lr_dict = {
            "id": 99,
            "learning_resource_type": 4,
            "static_assets": [3],
            "title": "Getting Help",
            "description": "description",
            "content_xml": "...",
            "materialized_path":
                "/course/chapter[4]/sequential[1]/vertical[3]",
            "url_path": "url_path",
            "parent": 22,
            "copyright": "copyright",
            "xa_nr_views": 1,
            "xa_nr_attempts": 2,
            "xa_avg_grade": 3.0,
            "xa_histogram_grade": 4.0,
            "terms": [],
            "preview_url": "",
        }

        def assert_not_changed(new_dict):
            """Check that fields have not changed"""
            # These keys should be different since they are immutable or set by
            # the serializer.
            fields = (
                'id', 'learning_resource_type', 'static_assets', 'title',
                'content_xml', 'materialized_path', 'url_path', 'parent',
                'copyright', 'xa_nr_views', 'xa_nr_attempts', 'xa_avg_grade',
                'xa_histogram_grade', 'preview_url'
            )
            for field in fields:
                self.assertNotEqual(lr_dict[field], new_dict[field])

        assert_not_changed(
            self.patch_learning_resource(self.repo.slug, lr_id, lr_dict,
                                         skip_assert=True))
        assert_not_changed(
            self.put_learning_resource(self.repo.slug, lr_id, lr_dict,
                                       skip_assert=True))

    def test_missing_learning_resource(self):
        """Test for an invalid learning resource id"""
        repo_slug1 = self.repo.slug
        resource1 = self.import_course_tarball(self.repo)
        lr1_id = resource1.id

        # import from a different course so it's not a duplicate course
        zip_file = self.get_course_zip()
        new_repo_dict = self.create_repository()
        repo_slug2 = new_repo_dict['slug']
        repo_id2 = new_repo_dict['id']
        import_file(
            zip_file, repo_id2, self.user.id)
        resource2 = get_resources(repo_id2).first()
        lr2_id = resource2.id

        # repo_slug1 should own lr1_id and repo_slug2 should own lr2_id
        self.get_learning_resource(repo_slug1, lr1_id)
        self.get_learning_resource(repo_slug2, lr1_id,
                                   expected_status=HTTP_404_NOT_FOUND)
        self.get_learning_resource(repo_slug1, lr2_id,
                                   expected_status=HTTP_404_NOT_FOUND)
        self.get_learning_resource(repo_slug2, lr2_id)

    def test_filefield_serialization(self):
        """Make sure that URL output is turned on in settings"""
        resource = self.import_course_tarball(self.repo)
        static_assets = self.get_static_assets(
            self.repo.slug, resource.id)['results']
        self.assertTrue(static_assets[0]['asset'].startswith("http"))

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

    def test_add_term_to_learning_resource(self):
        """
        Add a term to a learning resource via PATCH
        """

        resource = self.import_course_tarball(self.repo)
        lr_id = resource.id

        vocab1_slug = self.create_vocabulary(self.repo.slug)['slug']
        supported_term_slug = self.create_term(
            self.repo.slug, vocab1_slug)['slug']

        # This should change soon but for now we can't set this via API
        Vocabulary.objects.get(slug=vocab1_slug).learning_resource_types.add(
            resource.learning_resource_type
        )

        vocab_dict = dict(self.DEFAULT_VOCAB_DICT)
        vocab_dict['name'] += " changed"
        vocab2_slug = self.create_vocabulary(
            self.repo.slug, vocab_dict)['slug']
        unsupported_term_slug = self.create_term(
            self.repo.slug, vocab2_slug)['slug']

        self.assertEqual([], self.get_learning_resource(
            self.repo.slug, lr_id)['terms'])

        self.patch_learning_resource(
            self.repo.slug, lr_id, {"terms": [supported_term_slug]})
        self.patch_learning_resource(
            self.repo.slug, lr_id, {"terms": ["missing"]},
            expected_status=HTTP_400_BAD_REQUEST)
        self.patch_learning_resource(
            self.repo.slug, lr_id, {"terms": [unsupported_term_slug]},
            expected_status=HTTP_400_BAD_REQUEST)

    def test_learning_resource_types(self):
        """
        Get from learning_resource_types
        """
        base_url = "{}learning_resource_types/".format(API_BASE)

        resp = self.client.get(base_url)
        self.assertEqual(HTTP_200_OK, resp.status_code)
        types = as_json(resp)

        self.assertEqual(sorted([lrt.name for lrt
                                 in LearningResourceType.objects.all()]),
                         sorted([t['name'] for t in types['results']]))

        # nothing besides GET, OPTION, HEAD allowed
        resp = self.client.options(base_url)
        self.assertEqual(HTTP_200_OK, resp.status_code)
        resp = self.client.head(base_url)
        self.assertEqual(HTTP_200_OK, resp.status_code)
        resp = self.client.post(base_url, {})
        self.assertEqual(HTTP_405_METHOD_NOT_ALLOWED, resp.status_code)
        resp = self.client.patch(base_url, {})
        self.assertEqual(HTTP_405_METHOD_NOT_ALLOWED, resp.status_code)
        resp = self.client.put(base_url, {})
        self.assertEqual(HTTP_405_METHOD_NOT_ALLOWED, resp.status_code)

        # restricted to logged in users
        self.logout()
        resp = self.client.get(base_url)
        self.assertEqual(HTTP_403_FORBIDDEN, resp.status_code)

        # but otherwise unrestricted
        self.login(self.user_norepo)
        resp = self.client.get(base_url)
        self.assertEqual(HTTP_200_OK, resp.status_code)
        types = as_json(resp)

        self.assertEqual(sorted([lrt.name for lrt
                                 in LearningResourceType.objects.all()]),
                         sorted([t['name'] for t in types['results']]))

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

    def test_preview_url(self):
        """
        Assert preview url behavior for learning resources
        """
        learning_resource = LearningResource.objects.first()
        expected_jump_to_id_url = (
            "https://www.sandbox.edx.org/courses/"
            "test-org/infinity/Febtober/jump_to_id/url_name1"
        )
        self.assertEqual(
            expected_jump_to_id_url,
            learning_resource.get_preview_url()
        )

        resource_dict = self.get_learning_resource(
            self.repo.slug, learning_resource.id)
        self.assertEqual(
            expected_jump_to_id_url, resource_dict['preview_url'])

        learning_resource.url_name = None
        self.assertEqual(
            "https://www.sandbox.edx.org/courses/"
            "test-org/infinity/Febtober/courseware",
            learning_resource.get_preview_url()
        )
