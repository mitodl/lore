"""
REST tests for LearningResources and static assets
"""

from __future__ import unicode_literals
import os

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
)

from rest.tests.base import (
    RESTTestCase,
    RESTAuthTestCase,
    REPO_BASE,
    as_json,
    API_BASE,
)
from learningresources.api import get_resources
from learningresources.models import (
    LearningResource,
    LearningResourceType,
    Repository,
    get_preview_url,
)
from importer.tasks import import_file
from taxonomy.models import Vocabulary
from roles.permissions import GroupTypes
from roles.api import assign_user_to_repo_group


class TestLearningResource(RESTTestCase):
    """
    REST tests for LearningResources and StaticAssets
    """

    def test_immutable_fields_learning_resource(self):
        """Test immutable fields for term"""
        resource = self.import_course_tarball(self.repo)
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
        """Test for an invalid LearningResource id."""
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

    def test_learning_resource_filter(self):
        """Test for filtering LearningResources by ids."""

        def get_filtered(ids, expected_status=HTTP_200_OK):
            """Return list of LearningResources in shopping cart."""
            url_base = "{repo_base}{repo_slug}/learning_resources/".format(
                repo_base=REPO_BASE,
                repo_slug=self.repo.slug,
            )
            resp = self.client.get("{url_base}?id={ids}".format(
                url_base=url_base,
                ids=",".join([str(s) for s in ids])
            ))
            self.assertEqual(expected_status, resp.status_code)
            if expected_status == HTTP_200_OK:
                return sorted([x['id'] for x in as_json(resp)['results']])

        self.import_course_tarball(self.repo)
        self.assertEqual([], get_filtered([]))
        get_filtered(["not-a-number"],
                     expected_status=HTTP_400_BAD_REQUEST)
        self.assertEqual([], get_filtered([-1]))

        all_ids = list(get_resources(
            self.repo.id).values_list('id', flat=True))
        self.assertEqual(sorted(all_ids), get_filtered(all_ids))
        self.assertEqual(
            sorted(all_ids[:5]), get_filtered(all_ids[:5]))

    def test_filefield_serialization(self):
        """Make sure that URL output is turned on in settings."""
        resource = self.import_course_tarball(self.repo)
        static_assets = self.get_static_assets(
            self.repo.slug, resource.id)['results']
        self.assertTrue(static_assets[0]['asset'].startswith("http"))

    def test_add_term_to_learning_resource(self):
        """
        Add a term to a LearningResource via PATCH.
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

        self.assertEqual(
            [],
            self.get_learning_resource(self.repo.slug, lr_id)['terms']
        )

        self.patch_learning_resource(
            self.repo.slug, lr_id, {"terms": [supported_term_slug]})
        self.patch_learning_resource(
            self.repo.slug, lr_id, {"terms": ["missing"]},
            expected_status=HTTP_400_BAD_REQUEST)
        self.patch_learning_resource(
            self.repo.slug, lr_id, {"terms": [unsupported_term_slug]},
            expected_status=HTTP_400_BAD_REQUEST)
        new_term_dict = dict(self.DEFAULT_TERM_DICT)
        new_term_dict.update(label='term label 2')
        # create another term for the supported vocabulary
        supported_term_slug_2 = self.create_term(
            self.repo.slug,
            vocab1_slug,
            term_dict=new_term_dict
        )['slug']
        # trying to add the both terms to the learning resource will result
        # in a bad request
        self.patch_learning_resource(
            self.repo.slug,
            lr_id,
            {"terms": [supported_term_slug, supported_term_slug_2]},
            expected_status=HTTP_400_BAD_REQUEST
        )
        # but if the vocabulary is modified to accept multiple terms
        new_vocab_dict = dict(self.DEFAULT_VOCAB_DICT)
        new_vocab_dict.update(multi_terms=True)
        self.patch_vocabulary(
            repo_slug=self.repo.slug,
            vocab_slug=vocab1_slug,
            vocab_dict=new_vocab_dict
        )
        Vocabulary.objects.get(slug=vocab1_slug).learning_resource_types.add(
            resource.learning_resource_type
        )
        # adding two terms will be fine
        self.patch_learning_resource(
            self.repo.slug,
            lr_id,
            {"terms": [supported_term_slug, supported_term_slug_2]}
        )

    def test_learning_resource_types(self):
        """
        Get from learning_resource_types.
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

    def test_preview_url(self):
        """
        Assert preview url behavior for LearningResources.
        """
        learning_resource = LearningResource.objects.first()
        expected_jump_to_id_url = (
            "https://www.sandbox.edx.org/courses/"
            "test-org/infinity/Febtober/jump_to_id/url_name1"
        )
        self.assertEqual(
            expected_jump_to_id_url,
            get_preview_url(learning_resource)
        )

        resource_dict = self.get_learning_resource(
            self.repo.slug, learning_resource.id)
        self.assertEqual(
            expected_jump_to_id_url, resource_dict['preview_url'])

        learning_resource.url_name = None
        self.assertEqual(
            "https://www.sandbox.edx.org/courses/"
            "test-org/infinity/Febtober/courseware",
            get_preview_url(learning_resource)
        )

    def test_learning_resource_exports_invalid_methods(self):
        """
        Test invalid methods for session-based shopping cart
        for LearningResource exports.
        """

        collection_url = (
            "{repo_base}{repo_slug}/learning_resource_exports/{user}/".format(
                repo_base=REPO_BASE,
                repo_slug=self.repo.slug,
                user=self.user.username
            )
        )
        lr_id = LearningResource.objects.first().id
        detail_url = (
            "{repo_base}{repo_slug}/learning_resource_exports/"
            "{user}/{lr_id}/".format(
                repo_base=REPO_BASE,
                repo_slug=self.repo.slug,
                user=self.user.username,
                lr_id=lr_id,
            )
        )

        # PUT and PATCH not supported
        resp = self.client.patch(collection_url, {})
        self.assertEqual(HTTP_405_METHOD_NOT_ALLOWED, resp.status_code)
        resp = self.client.put(collection_url, {})
        self.assertEqual(HTTP_405_METHOD_NOT_ALLOWED, resp.status_code)
        resp = self.client.patch(detail_url, {})
        self.assertEqual(HTTP_405_METHOD_NOT_ALLOWED, resp.status_code)
        resp = self.client.put(detail_url, {})
        self.assertEqual(HTTP_405_METHOD_NOT_ALLOWED, resp.status_code)

        # POST not supported on detail url
        resp = self.client.post(detail_url, {})
        self.assertEqual(HTTP_405_METHOD_NOT_ALLOWED, resp.status_code)

    def test_learning_resource_exports_anonymous(self):
        """Make sure anonymous users are forbidden."""
        lr_id = get_resources(self.repo.id).first().id
        self.logout()

        self.get_learning_resource_export(
            self.repo.slug, lr_id, username="sarah",
            expected_status=HTTP_403_FORBIDDEN)
        self.get_learning_resource_exports(
            self.repo.slug, username="sarah",
            expected_status=HTTP_403_FORBIDDEN)
        self.create_learning_resource_export(
            self.repo.slug, {"id": lr_id}, username="sarah",
            expected_status=HTTP_403_FORBIDDEN)
        self.delete_learning_resource_export(
            self.repo.slug, lr_id,
            username="sarah",
            expected_status=HTTP_403_FORBIDDEN)
        self.delete_learning_resource_exports(
            self.repo.slug, username="sarah",
            expected_status=HTTP_403_FORBIDDEN)

    def test_learning_resource_exports_not_a_number(self):
        """
        Don't cause 500 error for non-numeric ids.
        """
        lr_id = "notanumber"

        self.get_learning_resource_export(
            self.repo.slug, lr_id, expected_status=HTTP_404_NOT_FOUND)
        self.create_learning_resource_export(
            self.repo.slug, {"id": lr_id},
            expected_status=HTTP_400_BAD_REQUEST)
        self.delete_learning_resource_export(
            self.repo.slug, lr_id, expected_status=HTTP_404_NOT_FOUND)


class TestLearningResourceAuthorization(RESTAuthTestCase):
    """
    REST tests for authorization of LearningResources and static assets.
    """

    def test_resource_get(self):
        """Test retrieve LearningResource."""
        self.assertEqual(
            1, self.get_learning_resources(self.repo.slug)['count'])

        resource = self.import_course_tarball(self.repo)
        lr_id = resource.id

        # author_user has view_repo permissions
        self.logout()
        self.login(self.author_user.username)
        self.assertEqual(
            1 + self.toy_resource_count,
            self.get_learning_resources(self.repo.slug)['count']
        )
        self.get_learning_resource(self.repo.slug, lr_id)

        # user_norepo has no view_repo permission
        self.logout()
        self.login(self.user_norepo.username)
        self.get_learning_resources(
            self.repo.slug, expected_status=HTTP_403_FORBIDDEN)
        self.get_learning_resource(
            self.repo.slug, lr_id, expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.get_learning_resources(
            self.repo.slug, expected_status=HTTP_403_FORBIDDEN)
        self.get_learning_resource(
            self.repo.slug, lr_id, expected_status=HTTP_403_FORBIDDEN)

    def test_resource_post(self):
        """Test create LearningResource."""
        resp = self.client.post(
            '{repo_base}{repo_slug}/learning_resources/'.format(
                repo_base=REPO_BASE,
                repo_slug=self.repo.slug,
            ),
            self.DEFAULT_LR_DICT
        )
        self.assertEqual(resp.status_code, HTTP_405_METHOD_NOT_ALLOWED)

    def test_resource_delete(self):
        """Test delete LearningResource."""
        resource = self.import_course_tarball(self.repo)
        lr_id = resource.id

        resp = self.client.delete(
            '{repo_base}{repo_slug}/learning_resources/{lr_id}/'.format(
                repo_base=REPO_BASE,
                repo_slug=self.repo.slug,
                lr_id=lr_id,
            ),
            self.DEFAULT_LR_DICT
        )
        self.assertEqual(resp.status_code, HTTP_405_METHOD_NOT_ALLOWED)

    def test_resource_put_patch(self):
        """Test update LearningResource."""
        resource = self.import_course_tarball(self.repo)
        lr_id = resource.id

        new_description_dict = {"description": "new description"}

        # as curator who has add_edit_metadata permission
        self.logout()
        self.login(self.curator_user.username)
        self.patch_learning_resource(
            self.repo.slug, lr_id, new_description_dict
        )
        new_description_dict['description'] += "_"
        new_description_dict['terms'] = []
        self.put_learning_resource(
            self.repo.slug, lr_id, new_description_dict
        )

        # author does have add_edit_metadata permission
        self.logout()
        self.login(self.author_user.username)
        new_description_dict['description'] += "_"
        self.patch_learning_resource(
            self.repo.slug, lr_id, new_description_dict
        )
        new_description_dict['description'] += "_"
        self.put_learning_resource(
            self.repo.slug, lr_id, new_description_dict
        )

        # as anonymous
        self.logout()
        new_description_dict['description'] += "_"
        self.patch_learning_resource(
            self.repo.slug, lr_id, new_description_dict,
            expected_status=HTTP_403_FORBIDDEN
        )
        self.put_learning_resource(
            self.repo.slug, lr_id, new_description_dict,
            expected_status=HTTP_403_FORBIDDEN
        )

    def test_static_assets_get(self):
        """Test for getting StaticAssets from LearningResources."""
        def get_resource_with_asset(type_name):
            """
            Get a LearningResource with a StaticAsset.
            """
            for resource in get_resources(self.repo.id):
                if (resource.learning_resource_type.name != type_name or
                        resource.static_assets.count() == 0):
                    continue
                return resource
        self.import_course_tarball(self.repo)
        # Most static assets within a course will be associated with multiple
        # resources due to the hierarchy. For the test course, we know that
        # there is no overlap between the html and video, making them
        # suitable for this test.
        resource1 = get_resource_with_asset("html")
        resource2 = get_resource_with_asset("video")
        static_asset1 = resource1.static_assets.first()
        static_asset2 = resource2.static_assets.first()
        lr1_id = resource1.id

        # add a second StaticAsset to another LearningResource
        resource2.static_assets.add(static_asset2)
        lr2_id = resource2.id
        # make sure the result for an asset contains a name and an url
        resp = self.get_static_asset(self.repo.slug, lr1_id, static_asset1.id)
        self.assertTrue('asset' in resp)
        self.assertTrue('name' in resp)
        self.assertTrue(static_asset1.asset.url in resp['asset'])
        self.assertEqual(
            resp['name'],
            os.path.basename(static_asset1.asset.name)
        )

        # make sure static assets only show up in their proper places
        self.get_static_asset(self.repo.slug, lr1_id, static_asset1.id)
        self.assertEqual(
            2, self.get_static_assets(self.repo.slug, lr1_id)['count'])
        self.get_static_asset(self.repo.slug, lr1_id, static_asset2.id,
                              expected_status=HTTP_404_NOT_FOUND)
        self.get_static_asset(self.repo.slug, lr2_id, static_asset1.id,
                              expected_status=HTTP_404_NOT_FOUND)
        self.get_static_asset(self.repo.slug, lr2_id, static_asset2.id)
        self.assertEqual(
            1, self.get_static_assets(self.repo.slug, lr2_id)['count'])

        # author_user has view_repo permissions
        self.logout()
        self.login(self.author_user.username)
        self.assertEqual(
            2, self.get_static_assets(self.repo.slug, lr1_id)['count'])
        self.get_static_asset(self.repo.slug, lr1_id, static_asset1.id)

        # user_norepo has no view_repo permission
        self.logout()
        self.login(self.user_norepo.username)
        self.get_static_assets(self.repo.slug, lr1_id,
                               expected_status=HTTP_403_FORBIDDEN)
        self.get_static_asset(self.repo.slug, lr1_id, static_asset1.id,
                              expected_status=HTTP_403_FORBIDDEN)

        # as anonymous
        self.logout()
        self.get_static_assets(self.repo.slug, lr1_id,
                               expected_status=HTTP_403_FORBIDDEN)
        self.get_static_asset(self.repo.slug, lr1_id, static_asset1.id,
                              expected_status=HTTP_403_FORBIDDEN)

    def test_static_assets_create(self):
        """Test for creating StaticAsset from learning_resources."""
        lr_id = get_resources(self.repo.id).first().id
        resp = self.client.post(
            '{repo_base}{repo_slug}/learning_resources/'
            '{lr_id}/static_assets/'.format(
                repo_base=REPO_BASE,
                repo_slug=self.repo.slug,
                lr_id=lr_id,
            ),
            self.DEFAULT_LR_DICT
        )
        self.assertEqual(resp.status_code, HTTP_405_METHOD_NOT_ALLOWED)

    def test_static_assets_put_patch(self):
        """Test for updating StaticAssets from learning_resources."""
        resource = self.import_course_tarball(self.repo)
        static_asset = resource.static_assets.first()
        lr_id = resource.id

        resp = self.client.put(
            '{repo_base}{repo_slug}/learning_resources/'
            '{lr_id}/static_assets/{sa_id}/'.format(
                repo_base=REPO_BASE,
                repo_slug=self.repo.slug,
                lr_id=lr_id,
                sa_id=static_asset.id,
            ),
            self.DEFAULT_LR_DICT
        )
        self.assertEqual(resp.status_code, HTTP_405_METHOD_NOT_ALLOWED)
        resp = self.client.patch(
            '{repo_base}{repo_slug}/learning_resources/'
            '{lr_id}/static_assets/{sa_id}/'.format(
                repo_base=REPO_BASE,
                repo_slug=self.repo.slug,
                lr_id=lr_id,
                sa_id=static_asset.id,
            ),
            self.DEFAULT_LR_DICT
        )
        self.assertEqual(resp.status_code, HTTP_405_METHOD_NOT_ALLOWED)

    def test_static_assets_delete(self):
        """Test for deleting StaticAssets from learning_resources."""
        resource = self.import_course_tarball(self.repo)
        static_asset = resource.static_assets.first()
        lr_id = resource.id

        resp = self.client.delete(
            '{repo_base}{repo_slug}/learning_resources/'
            '{lr_id}/static_assets/{sa_id}/'.format(
                repo_base=REPO_BASE,
                repo_slug=self.repo.slug,
                lr_id=lr_id,
                sa_id=static_asset.id,
            ),
            self.DEFAULT_LR_DICT
        )
        self.assertEqual(resp.status_code, HTTP_405_METHOD_NOT_ALLOWED)

    def test_learning_resource_exports(self):
        """Test for creating LearningResource ids in session shopping cart."""

        # set up our data
        self.logout()
        self.login(self.add_repo_user)

        repo_slug1 = self.repo.slug
        repo_slug2 = self.create_repository()['slug']
        repo2 = Repository.objects.get(slug=repo_slug2)

        # 'add_repo_user' will be able to see both repos
        assign_user_to_repo_group(
            self.add_repo_user, self.repo, GroupTypes.REPO_ADMINISTRATOR)
        self.import_course_tarball(repo2)

        repo1_lrid1 = get_resources(self.repo.id).all()[0].id
        repo2_lrid1 = get_resources(repo2.id).all()[0].id
        repo2_lrid2 = get_resources(repo2.id).all()[1].id

        self.logout()
        self.login(self.user)

        # make sure we start with an empty shopping cart
        self.assertEqual([],
                         self.get_learning_resource_exports(
                             repo_slug1)['results'])
        self.create_learning_resource_export(self.repo.slug, {
            'id': repo1_lrid1
        })
        self.assertEqual([{'id': repo1_lrid1}],
                         self.get_learning_resource_exports(
                             repo_slug1)['results'])

        # user doesn't have access to repo2
        self.get_learning_resource_exports(
            repo_slug2, expected_status=HTTP_403_FORBIDDEN)

        self.logout()
        self.login(self.add_repo_user)

        # make sure that session is not shared between users
        # user has an id in repo1 but add_repo_user does not
        self.assertEqual([], self.get_learning_resource_exports(
            repo_slug1
        )['results'])

        # don't store duplicates
        self.create_learning_resource_export(repo_slug1, {"id": repo1_lrid1})
        self.create_learning_resource_export(repo_slug1, {"id": repo1_lrid1})
        self.assertEqual(
            [{"id": repo1_lrid1}],
            self.get_learning_resource_exports(
                repo_slug1
            )['results'])

        # make sure export ids are confined to their own repos
        self.create_learning_resource_export(repo_slug2, {
            'id': repo2_lrid1
        })
        # not affected by POST in previous line
        self.assertEqual([{'id': repo1_lrid1}],
                         self.get_learning_resource_exports(
                             repo_slug1)['results'])
        # contains the new item
        self.assertEqual([{'id': repo2_lrid1}],
                         self.get_learning_resource_exports(
                             repo_slug2)['results'])

        # make sure we can't add export ids that don't belong to the repo
        self.create_learning_resource_export(repo_slug1, {
            'id': repo2_lrid1
        }, expected_status=HTTP_403_FORBIDDEN)

        # make sure detail view will 404 if out of bounds
        self.assertEqual(repo1_lrid1, self.get_learning_resource_export(
            repo_slug1, repo1_lrid1)['id'])
        self.get_learning_resource_export(
            repo_slug1, repo2_lrid1,
            expected_status=HTTP_404_NOT_FOUND)
        self.get_learning_resource_export(
            repo_slug2, repo1_lrid1,
            expected_status=HTTP_404_NOT_FOUND)
        self.assertEqual(repo2_lrid1, self.get_learning_resource_export(
            repo_slug2, repo2_lrid1)['id'])

        self.create_learning_resource_export(repo_slug2, {"id": repo2_lrid1})
        self.create_learning_resource_export(repo_slug2, {"id": repo2_lrid2})

        # finally, delete all of the things
        self.assertEqual(
            1, self.get_learning_resource_exports(repo_slug2)['count'])
        self.delete_learning_resource_exports(repo_slug2)
        self.assertEqual(
            0, self.get_learning_resource_exports(repo_slug2)['count'])

        # make sure deleting an empty list doesn't cause problems
        self.delete_learning_resource_exports(repo_slug2)
        self.assertEqual(
            0, self.get_learning_resource_exports(repo_slug2)['count'])

        # repo1 is unaffected
        self.assertEqual(
            1, self.get_learning_resource_exports(repo_slug1)['count'])
        self.delete_learning_resource_export(repo_slug1, repo1_lrid1)
        self.get_learning_resource_export(
            repo_slug1, repo1_lrid1, expected_status=HTTP_404_NOT_FOUND)

        self.logout()
        self.login(self.user)

        # Populate shopping cart one more time.
        self.create_learning_resource_export(repo_slug1, {"id": repo1_lrid1})

        self.logout()
        self.login(self.user)

        # After logout and login session was cleared
        self.assertEqual(
            0, self.get_learning_resource_exports(repo_slug1)['count'])

    def test_export_with_incorrect_username(self):
        """Make sure we enforce the username in the URL."""
        resp = self.client.get(
            "{repo_base}{repo_slug}/learning_resource_exports/missing/".format(
                repo_base=REPO_BASE,
                repo_slug=self.repo.slug,
            ))
        self.assertEqual(HTTP_403_FORBIDDEN, resp.status_code)

        resource = self.repo.course_set.first().resources.first()
        self.create_learning_resource_export(self.repo.slug, {
            "id": resource.id
        })
        resp = self.client.get(
            "{repo_base}{repo_slug}/learning_resource_exports/missing/"
            "{lr_id}/".format(
                repo_base=REPO_BASE,
                repo_slug=self.repo.slug,
                lr_id=resource.id,
            )
        )
        self.assertEqual(HTTP_403_FORBIDDEN, resp.status_code)
