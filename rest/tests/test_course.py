"""
REST tests for courses
"""
from __future__ import unicode_literals

from rest.tests.base import (
    RESTAuthTestCase,
    RESTTestCase,
)

from learningresources.api import create_course


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
