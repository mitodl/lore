"""Tests for search engine indexing."""
from __future__ import unicode_literals

from search.sorting import LoreSortingFields
from search.tests.base import SearchTestCase


class TestIndexing(SearchTestCase):
    """Test Elasticsearch indexing."""

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
        term = self.terms[0]
        self.assertTrue(self.count_faceted_results(
            self.vocabulary.name, term.label) == 0)
        self.resource.terms.add(term)
        self.assertTrue(self.count_faceted_results(
            self.vocabulary.name, term.label) == 1)
        self.resource.terms.remove(term)
        self.assertTrue(self.count_faceted_results(
            self.vocabulary.name, term.label) == 0)

    def test_strip_xml(self):
        """Indexed content_xml should have XML stripped."""
        xml = "<tag>you're it</tag>"
        self.resource.content_xml = xml
        self.resource.save()
        self.assertTrue(self.count_results("you're it") == 1)
        self.assertTrue(self.count_results(xml) == 0)

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
        self.assertEqual(self.count_results(''), 3)
        # sorting by number of views
        results = self.search(
            '',
            sorting=LoreSortingFields.SORT_BY_NR_VIEWS[0]
        )
        # expected position (res2, res3, res1)
        top_res = results[0]
        self.assertEqual(
            top_res.nr_views,
            res2.xa_nr_views
        )
        # sorting by number of attempts
        results = self.search(
            '',
            sorting=LoreSortingFields.SORT_BY_NR_ATTEMPTS[0]
        )
        # expected position (res3, res1, res2)
        top_res = results[0]
        self.assertEqual(
            top_res.nr_attempts,
            res3.xa_nr_attempts
        )
        # sorting by average grade
        results = self.search(
            '',
            sorting=LoreSortingFields.SORT_BY_AVG_GRADE[0]
        )
        # expected position (res1, res3, res2)
        top_res = results[0]
        self.assertEqual(
            top_res.avg_grade,
            res1.xa_avg_grade
        )
