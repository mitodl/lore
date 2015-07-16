"""
Tests for search sorting options.
"""

from __future__ import unicode_literals

from django.test.testcases import TestCase

from search.sorting import LoreSortingFields


class SortingTest(TestCase):
    """Test sorting options"""

    def test_all_sorting_options(self):
        """Test all_sorting_options method"""
        self.assertEqual(
            LoreSortingFields.all_sorting_options(),
            [
                LoreSortingFields.SORT_BY_NR_VIEWS,
                LoreSortingFields.SORT_BY_NR_ATTEMPTS,
                LoreSortingFields.SORT_BY_AVG_GRADE,
            ]
        )

    def test_all_sorting_fields(self):
        """Test all_sorting_fields method"""
        self.assertEqual(
            LoreSortingFields.all_sorting_fields(),
            [
                LoreSortingFields.SORT_BY_NR_VIEWS[0],
                LoreSortingFields.SORT_BY_NR_ATTEMPTS[0],
                LoreSortingFields.SORT_BY_AVG_GRADE[0],
            ]
        )

    def test_get_sorting_option(self):
        """Test get_sorting_option method"""
        self.assertEqual(
            LoreSortingFields.get_sorting_option(
                LoreSortingFields.SORT_BY_NR_VIEWS[0]
            ),
            LoreSortingFields.SORT_BY_NR_VIEWS
        )
        self.assertEqual(
            LoreSortingFields.get_sorting_option(
                LoreSortingFields.SORT_BY_NR_ATTEMPTS[0]
            ),
            LoreSortingFields.SORT_BY_NR_ATTEMPTS
        )
        self.assertEqual(
            LoreSortingFields.get_sorting_option(
                LoreSortingFields.SORT_BY_AVG_GRADE[0]
            ),
            LoreSortingFields.SORT_BY_AVG_GRADE
        )
        self.assertEqual(
            LoreSortingFields.get_sorting_option('foo_field'),
            LoreSortingFields.SORT_BY_NR_VIEWS
        )

    def test_all_sorting_options_but(self):
        """Test all_sorting_options_but method"""
        self.assertEqual(
            LoreSortingFields.all_sorting_options_but(
                LoreSortingFields.SORT_BY_NR_VIEWS[0]
            ),
            [
                LoreSortingFields.SORT_BY_NR_ATTEMPTS,
                LoreSortingFields.SORT_BY_AVG_GRADE,
            ]
        )
        self.assertEqual(
            LoreSortingFields.all_sorting_options_but(
                LoreSortingFields.SORT_BY_NR_ATTEMPTS[0]
            ),
            [
                LoreSortingFields.SORT_BY_NR_VIEWS,
                LoreSortingFields.SORT_BY_AVG_GRADE,
            ]
        )
        self.assertEqual(
            LoreSortingFields.all_sorting_options_but(
                LoreSortingFields.SORT_BY_AVG_GRADE[0]
            ),
            [
                LoreSortingFields.SORT_BY_NR_VIEWS,
                LoreSortingFields.SORT_BY_NR_ATTEMPTS,
            ]
        )
        self.assertEqual(
            LoreSortingFields.all_sorting_options_but('foo_field'),
            [
                LoreSortingFields.SORT_BY_NR_VIEWS,
                LoreSortingFields.SORT_BY_NR_ATTEMPTS,
                LoreSortingFields.SORT_BY_AVG_GRADE,
            ]
        )
