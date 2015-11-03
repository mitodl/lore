"""
REST tests for courses
"""
from __future__ import unicode_literals

from rest.tests.base import (
    REPO_BASE,
    RESTAuthTestCase,
    RESTTestCase,
)

from learningresources.api import create_course
from learningresources.models import (
    Course,
    LearningResource,
    LearningResourceType,
    Repository,
    StaticAsset,
)
from taxonomy.models import Term, Vocabulary


class TestCourse(RESTTestCase):
    """
    REST tests for Courses.
    """

    def test_list_courses(self):
        """
        Tests the api to list courses in a repo
        """
        res = self.get_courses(repo_slug=self.repo.slug)
        self.assertEqual(res['count'], 1)

        # check content returned
        course_1 = res['results'][0]
        self.assertDictEqual(
            course_1,
            {
                'org': self.course.org,
                'run': self.course.run,
                'course_number': self.course.course_number,
                'id': self.course.id
            }
        )
        # create another course
        course_params = {
            'org': 'my org',
            'repo_id': self.repo.id,
            'course_number': 'second course number',
            'run': "second course run",
            'user_id': self.user.id
        }
        second_course = create_course(**course_params)
        res = self.get_courses(repo_slug=self.repo.slug)
        self.assertEqual(res['count'], 2)

        # check the courses are ordered by creation/id
        course_1 = res['results'][0]
        course_2 = res['results'][1]
        self.assertEqual(course_1['id'], self.course.id)
        self.assertEqual(course_2['id'], second_course.id)
        self.assertTrue(course_1['id'] < course_2['id'])

    def test_get_course(self):
        """
        REST tests to get a Course.
        """
        res = self.get_course(
            repo_slug=self.repo.slug,
            course_id=self.course.id
        )
        self.assertDictEqual(
            res,
            {
                'org': self.course.org,
                'run': self.course.run,
                'course_number': self.course.course_number,
                'id': self.course.id
            }
        )
        self.get_course(
            repo_slug=self.repo.slug,
            course_id='foo',
            expected_status=404
        )
        self.get_course(
            repo_slug=self.repo.slug,
            course_id=1234567,
            expected_status=404
        )
        # try to get the right course but non existing repo
        self.get_course(
            repo_slug='nonsense',
            course_id=self.course.id,
            expected_status=404
        )

        # create another repo
        another_repo_dict = {
            'name': 'another_repo_name',
            'description': 'description',
        }
        repo_res = self.create_repository(another_repo_dict)

        # try to get the right course but on wrong repo
        self.get_course(
            repo_slug=repo_res['slug'],
            course_id=self.course.id,
            expected_status=404
        )

    def count_resources(self, repositories=0, courses=0, learning_resources=0,
                        learning_resource_types=0, static_assetts=0, terms=0,
                        vocabularies=0):
        """
        Helper function to count resources in the database
        """
        # pylint: disable=too-many-arguments
        self.assertEqual(Repository.objects.count(), repositories)
        self.assertEqual(Course.objects.count(), courses)
        self.assertEqual(LearningResource.objects.count(), learning_resources)
        self.assertEqual(LearningResourceType.objects.count(),
                         learning_resource_types)
        self.assertEqual(StaticAsset.objects.count(), static_assetts)
        self.assertEqual(Term.objects.count(), terms)
        self.assertEqual(Vocabulary.objects.count(), vocabularies)
        self.assertEqual(self.get_results()['count'], learning_resources)

    def test_delete_course(self):
        """
        REST tests to delete a Course.
        All learning resources and static assets connected to the course are
        deleted as well.
        Other courses, learning resources types, terms, vocabularies,
        repositories are not deleted.
        Note: learning resources types are created during the import of the
        course but they are related to the repository.
        """
        # trying to delete non existing courses
        self.delete_course(
            repo_slug=self.repo.slug,
            course_id='foo',
            expected_status=404
        )
        self.delete_course(
            repo_slug=self.repo.slug,
            course_id=1234567,
            expected_status=404
        )

        # environment before importing a course
        self.count_resources(
            repositories=1,
            courses=1,
            learning_resources=1,
            learning_resource_types=1
        )

        # Import the course tarball
        self.import_course_tarball(self.repo)
        # create a vocabulary and term
        vocabulary = self.create_vocabulary(self.repo.slug)
        self.create_term(self.repo.slug, vocabulary['slug'])

        # environment before deleting the course
        self.count_resources(
            repositories=1,
            courses=2,
            learning_resources=19,
            learning_resource_types=8,
            static_assetts=5,
            terms=1,
            vocabularies=1
        )

        # make sure of the course that is going to be deleted
        courses = Course.objects.all()
        self.assertEqual(courses[0].id, self.course.id)
        self.assertNotEqual(courses[1].id, self.course.id)

        # try to get the right course but non existing repo
        self.delete_course(
            repo_slug='nonsense',
            course_id=courses[1].id,
            expected_status=404
        )

        # delete the course
        self.delete_course(self.repo.slug, courses[1].id)

        # environment after deleting the course
        self.count_resources(
            repositories=1,
            courses=1,
            learning_resources=1,
            learning_resource_types=8,
            terms=1,
            vocabularies=1
        )

        # the course remaining is the one not deleted
        courses = Course.objects.all()
        self.assertEqual(courses[0].id, self.course.id)

        # and the learning resources remaining are associated with
        # the remaining course
        for learning_resource in LearningResource.objects.all():
            self.assertEqual(
                learning_resource.course.id,
                self.course.id
            )

        # try to delete the remaining course but with the wrong repo
        # create another repo
        another_repo_dict = {
            'name': 'another_repo_name',
            'description': 'description',
        }
        repo_res = self.create_repository(another_repo_dict)
        # and another course in it
        course_params = {
            'org': 'my org',
            'repo_id': repo_res['id'],
            'course_number': 'second course number',
            'run': "second course run",
            'user_id': self.user.id
        }
        second_course = create_course(**course_params)

        # try to get the right course but on wrong repo
        self.delete_course(
            repo_slug=repo_res['slug'],
            course_id=self.course.id,
            expected_status=404
        )
        # again with repo and course swapped
        self.delete_course(
            repo_slug=self.repo.slug,
            course_id=second_course.id,
            expected_status=404
        )


class TestCourseAuthorization(RESTAuthTestCase):
    """
    REST tests for authorization of Courses.
    """

    def test_get_courses(self):
        """
        Authorizations for get courses
        Any user of the repo can see courses
        """
        # administrator of the repo (already logged in)
        self.get_courses(repo_slug=self.repo.slug)
        self.logout()

        # curator
        self.login(self.curator_user.username)
        self.get_courses(repo_slug=self.repo.slug)
        self.logout()

        # author
        self.login(self.author_user.username)
        self.get_courses(repo_slug=self.repo.slug)
        self.logout()

        # user without repo
        self.login(self.user_norepo)
        self.get_courses(repo_slug=self.repo.slug, expected_status=403)
        self.logout()

        # anonymous
        self.get_courses(repo_slug=self.repo.slug, expected_status=403)

    def test_create_courses(self):
        """
        Test post method
        """
        res = self.client.post(
            '{repo_base}{slug}/courses/'.format(
                slug=self.repo.slug,
                repo_base=REPO_BASE,
            ),
            {}
        )
        self.assertEqual(res.status_code, 405)

    def test_get_course(self):
        """
        Authorizations for get a course
        Any user of the repo can see courses
        """
        # administrator of the repo (already logged in)
        self.get_course(repo_slug=self.repo.slug, course_id=self.course.id)
        self.logout()

        # curator
        self.login(self.curator_user.username)
        self.get_course(repo_slug=self.repo.slug, course_id=self.course.id)
        self.logout()

        # author
        self.login(self.author_user.username)
        self.get_course(repo_slug=self.repo.slug, course_id=self.course.id)
        self.logout()

        # user without repo
        self.login(self.user_norepo)
        self.get_course(
            repo_slug=self.repo.slug,
            course_id=self.course.id,
            expected_status=403
        )
        self.logout()

        # anonymous
        self.get_course(
            repo_slug=self.repo.slug,
            course_id=self.course.id,
            expected_status=403
        )

    def test_delete_course(self):
        """
        Authorizations for delete a course
        Only user with import permission (admin and curator) can delete a repo
        """
        course_params = {
            'org': 'my org',
            'repo_id': self.repo.id,
            'course_number': 'second course number',
            'run': "second course run",
            'user_id': self.user.id
        }

        # anonymous user
        self.logout()
        self.delete_course(
            self.repo.slug,
            self.course.id,
            expected_status=403
        )

        # user not belonging to repo
        self.login(self.user_norepo.username)
        self.delete_course(
            self.repo.slug,
            self.course.id,
            expected_status=403
        )
        self.logout()

        # author
        self.login(self.author_user.username)
        self.delete_course(
            self.repo.slug,
            self.course.id,
            expected_status=403
        )
        self.logout()

        # curator
        self.login(self.curator_user.username)
        self.delete_course(
            self.repo.slug,
            self.course.id
        )
        self.logout()

        # recreate course
        self.course = create_course(**course_params)

        # administrator
        self.login(self.user.username)
        self.delete_course(
            self.repo.slug,
            self.course.id
        )

    def test_put_patch_course(self):
        """
        Test post method
        """
        res = self.client.put(
            '{repo_base}{slug}/courses/{course_id}/'.format(
                slug=self.repo.slug,
                repo_base=REPO_BASE,
                course_id=self.course.id
            ),
            {}
        )
        self.assertEqual(res.status_code, 405)
        res = self.client.patch(
            '{repo_base}{slug}/courses/{course_id}/'.format(
                slug=self.repo.slug,
                repo_base=REPO_BASE,
                course_id=self.course.id
            ),
            {}
        )
        self.assertEqual(res.status_code, 405)
