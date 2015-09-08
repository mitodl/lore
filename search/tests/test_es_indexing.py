"""
Tests for Elasticsearch indexing.

Note that this file started out as a copy
of search/tests/test_indexing.py, and was modified to use
the Elasticsearch and Elasticsearch-DSL libraries instead of Haystack.
"""

from __future__ import unicode_literals

import logging

from learningresources.tests.base import LoreTestCase
from learningresources.models import LearningResource
from importer.api import import_course_from_file
from search.search_indexes import cache
from search.sorting import LoreSortingFields
from search.tests.base_es import SearchTestCase
from search.utils import index_resources, search_index, refresh_index

log = logging.getLogger(__name__)


def set_cache_timeout(seconds):
    """Override the cache timeout for testing."""
    cache.default_timeout = seconds
    cache.clear()


class TestImport(LoreTestCase):
    """
    Test indexing on import.
    """
    def setUp(self):
        """
        Return location of the local copy of the "simple" course for testing.
        """
        super(TestImport, self).setUp()
        self.course_zip = self.get_course_zip()

    def test_import(self):
        """
        Indexing should occur on course import.
        """
        results = search_index()
        original_count = results.count()
        import_course_from_file(self.course_zip, self.repo.id, self.user.id)
        refresh_index()
        results = search_index()
        self.assertEqual(results.count(), original_count + 18)
        self.assertEqual(results.page_count(), 2)

        # Ensure the correct number of results are returned in each page.
        self.assertEqual(len(results.get_page(1)), 10)
        self.assertEqual(len(results.get_page(2)), 9)
        self.assertEqual(len(results.get_page(3)), 0)

        # Make sure the .all() function (a convenience function which
        # returns a generator), returns all the records without explicit
        # pagination.
        count = 0
        for _ in results.all():
            count += 1
        self.assertEqual(count, results.count())

    def test_update(self):
        """
        Items should only be indexed on update, not creation.

        During course import, a bulk indexing will occur.
        """
        orig_count = search_index().count()
        new_resource = LearningResource.objects.create(
            course=self.resource.course,
            learning_resource_type=self.resource.learning_resource_type,
            title="accordion music",
            content_xml="<blah>foo</blah>",
            materialized_path="/foo",
            url_name="url_name2",
        )
        self.assertEqual(search_index().count(), orig_count)  # no indexing
        new_resource.save()  # triggers post_save signal with created=False
        self.assertEqual(search_index().count(), orig_count + 1)

    def test_search_fields(self):
        """
        The content_xml, title, and description should be searchable
        by partial matches.
        """
        new_resource = LearningResource.objects.create(
            course=self.resource.course,
            learning_resource_type=self.resource.learning_resource_type,
            title="accordion music",
            content_xml="<blah>foo</blah>",
            materialized_path="/foo",
            url_name="url_name2",
            description="the quick brown fox",
            description_path="silver",
        )

        new_resource.save()  # to trigger indexing
        refresh_index()

        self.assertEqual(search_index("accordion").count(), 1)
        self.assertEqual(search_index("fox brown").count(), 1)
        self.assertEqual(search_index("foo").count(), 1)

    def test_delete(self):
        """
        Items should be removed from the index when they are deleted.

        """
        orig_count = search_index().count()
        self.resource.delete()
        self.assertEqual(search_index().count(), orig_count - 1)


class TestIndexing(SearchTestCase):
    """Test Elasticsearch indexing."""

    def setUp(self):
        """Remember old caching settings."""
        super(TestIndexing, self).setUp()
        self.original_timeout = cache.default_timeout

    def tearDown(self):
        """Restore old caching settings."""
        super(TestIndexing, self).tearDown()
        cache.default_timeout = self.original_timeout

    def test_index_on_save(self):
        """Index a LearningObject upon creation."""
        search_text = "The quick brown fox."
        self.assertTrue(self.count_results(search_text) == 0)
        self.resource.content_xml = search_text
        self.resource.save()
        self.assertTrue(self.count_results(search_text) == 1)

    def test_index_vocabulary(self):
        """
        Test that LearningResource indexes are updated when a
        a term is added or removed.
        """
        set_cache_timeout(0)
        term = self.terms[0]
        self.assertEqual(self.count_faceted_results(
            self.vocabulary.name, term.label), 0)
        self.resource.terms.add(term)
        refresh_index()
        self.assertEqual(self.count_faceted_results(
            self.vocabulary.name, term.label), 1)
        self.resource.terms.remove(term)
        refresh_index()
        self.assertEqual(self.count_faceted_results(
            self.vocabulary.name, term.label), 0)

    def test_strip_xml(self):
        """Indexed content_xml should have XML stripped."""
        xml = "<tag>you're it</tag>"
        self.resource.content_xml = xml
        self.resource.save()
        refresh_index()
        self.assertTrue(self.count_results("you're it") == 1)
        self.assertTrue(self.count_results("tag") == 0)

    def test_sorting(self):
        """Test sorting for search"""
        # remove the default resource to control the environment
        self.resource.delete()
        # create some resources
        res1 = self.create_resource(**dict(
            resource_type="example",
            title="silly example 1",
            content_xml="<blah>blah 1</blah>",
            mpath="/blah1",
            xa_nr_views=1001,
            xa_nr_attempts=99,
            xa_avg_grade=9.9
        ))
        res2 = self.create_resource(**dict(
            resource_type="example",
            title="silly example 2",
            content_xml="<blah>blah 2</blah>",
            mpath="/blah2",
            xa_nr_views=1003,
            xa_nr_attempts=98,
            xa_avg_grade=6.8
        ))
        res3 = self.create_resource(**dict(
            resource_type="example",
            title="silly example 3",
            content_xml="<blah>blah 3</blah>",
            mpath="/blah3",
            xa_nr_views=1002,
            xa_nr_attempts=101,
            xa_avg_grade=7.3
        ))
        res4 = self.create_resource(**dict(
            resource_type="example",
            title="silly example 4",
            content_xml="<blah>blah 4</blah>",
            mpath="/blah3",
            xa_nr_views=1003,
            xa_nr_attempts=101,
            xa_avg_grade=9.9
        ))
        index_resources([res1, res2, res3, res4])
        refresh_index()
        self.assertEqual(self.count_results(), 4)
        # sorting by number of views
        results = self.search(
            query=None,
            sorting=LoreSortingFields.SORT_BY_NR_VIEWS[0]
        )
        # expected position res2, res4
        top_res = results[0]
        sec_res = results[1]
        self.assertEqual(
            top_res.id,
            res2.id
        )
        self.assertEqual(
            sec_res.id,
            res4.id
        )
        # sorting by number of attempts
        results = self.search(
            query=None,
            sorting=LoreSortingFields.SORT_BY_NR_ATTEMPTS[0]
        )
        # expected position res3, res4
        top_res = results[0]
        sec_res = results[1]
        self.assertEqual(
            top_res.id,
            res3.id
        )
        self.assertEqual(
            sec_res.id,
            res4.id
        )
        # sorting by average grade
        results = self.search(
            query=None,
            sorting=LoreSortingFields.SORT_BY_AVG_GRADE[0]
        )
        # expected position res1, res4
        top_res = results[0]
        sec_res = results[1]
        self.assertEqual(
            top_res.id,
            res1.id
        )
        self.assertEqual(
            sec_res.id,
            res4.id
        )
