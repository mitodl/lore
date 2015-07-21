"""
Repository REST tests
"""

from __future__ import unicode_literals

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
from rest.serializers import RepositorySerializer
from learningresources.models import Repository


# pylint: disable=invalid-name
class TestRepository(RESTTestCase):
    """Repository REST tests"""

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


# pylint: disable=too-many-ancestors
class TestRepositoryAuthorization(RESTAuthTestCase):
    """Repository authorization REST tests"""

    def test_repository_create(self):
        """Test create repository authorization"""
        # switch to add_repo_user
        self.logout()
        self.login(self.add_repo_user.username)

        # add_repo_user creates a repository
        new_repo_slug = self.create_repository()['slug']

        self.get_repository(new_repo_slug)
        self.get_repository(self.repo.slug, expected_status=HTTP_403_FORBIDDEN)
        repos = self.get_repositories()
        self.assertEqual(1, repos['count'])

        # duplicate repository, now that we assigned another repo
        # with same name to user
        self.create_repository(expected_status=HTTP_400_BAD_REQUEST)

        # switch to curator_user
        self.logout()
        self.login(self.curator_user.username)

        self.create_repository({
            'name': 'newname',
            'description': 'description',
        }, expected_status=HTTP_403_FORBIDDEN)

        # switch to user with no permissions for repo
        self.logout()
        self.login(self.user_norepo.username)

        self.create_repository({
            'name': 'newname',
            'description': 'description',
        }, expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.create_repository({
            'name': 'newname',
            'description': 'description',
        }, expected_status=HTTP_403_FORBIDDEN)

    def test_repository_patch_put(self):
        """Test updating repository"""
        # switch to add_repo_user
        self.logout()
        self.login(self.add_repo_user.username)

        input_dict = {
            'name': self.repo.name,
            'description': 'new description'
        }
        self.patch_repository(self.repo.slug, input_dict,
                              expected_status=HTTP_403_FORBIDDEN)
        self.put_repository(self.repo.slug, input_dict,
                            expected_status=HTTP_403_FORBIDDEN)

        # switch to curator_user
        self.logout()
        self.login(self.curator_user.username)
        self.patch_repository(self.repo.slug, input_dict,
                              expected_status=HTTP_405_METHOD_NOT_ALLOWED)
        self.put_repository(self.repo.slug, input_dict,
                            expected_status=HTTP_405_METHOD_NOT_ALLOWED)

        # switch to user with no permissions for repo
        self.logout()
        self.login(self.user_norepo.username)
        self.patch_repository(self.repo.slug, input_dict,
                              expected_status=HTTP_403_FORBIDDEN)
        self.put_repository(self.repo.slug, input_dict,
                            expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.patch_repository(self.repo.slug, input_dict,
                              expected_status=HTTP_403_FORBIDDEN)
        self.put_repository(self.repo.slug, input_dict,
                            expected_status=HTTP_403_FORBIDDEN)

    def test_repository_delete(self):
        """Test deleting repository"""
        # switch to add_repo_user
        self.logout()
        self.login(self.add_repo_user.username)

        self.delete_repository(self.repo.slug,
                               expected_status=HTTP_403_FORBIDDEN)

        self.logout()
        self.login(self.curator_user.username)

        # curator does have view_repo but nobody is allowed
        # to delete repositories
        self.delete_repository(self.repo.slug,
                               expected_status=HTTP_405_METHOD_NOT_ALLOWED)

        # switch to user with no permissions for repo
        self.logout()
        self.login(self.user_norepo.username)
        self.delete_repository(self.repo.slug,
                               expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.delete_repository(self.repo.slug,
                               expected_status=HTTP_403_FORBIDDEN)

    def test_repository_get(self):
        """Test list and view repository"""

        # switch to add_repo_user
        self.logout()
        self.login(self.add_repo_user.username)

        # add_repo_user shouldn't be able to see any repositories yet
        self.get_repository(self.repo.slug, expected_status=HTTP_403_FORBIDDEN)
        repos = self.get_repositories()
        self.assertEqual(0, repos['count'])

        # add_repo_user creates a repository
        new_repo_slug = self.create_repository()['slug']

        self.get_repository(new_repo_slug)
        repos = self.get_repositories()
        self.assertEqual(1, repos['count'])

        # switch to curator_user
        self.logout()
        self.login(self.curator_user.username)

        self.assertEqual(1, self.get_repositories()['count'])
        self.get_repository(new_repo_slug,
                            expected_status=HTTP_403_FORBIDDEN)
        self.get_repository(self.repo.slug)

        # switch to user_norepo
        self.logout()
        self.login(self.user_norepo.username)

        self.assertEqual(0, self.get_repositories()['count'])
        self.get_repository(self.repo.slug,
                            expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.get_repositories(expected_status=HTTP_403_FORBIDDEN)
        self.get_repository(self.repo.slug,
                            expected_status=HTTP_403_FORBIDDEN)
