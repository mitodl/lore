"""
Definitions of sorting fields
"""
from __future__ import unicode_literals


class LoreSortingFields(object):
    """
    Definition of possible sorting fields
    """
    SORT_BY_NR_VIEWS = ('nr_views', 'Number of Views (desc)')
    SORT_BY_NR_ATTEMPTS = ('nr_attempts', 'Number of Attempts (desc)')
    SORT_BY_AVG_GRADE = ('avg_grade', 'Average Grade (desc)')

    DEFAULT_SORTING_FIELD = SORT_BY_NR_VIEWS[0]

    @classmethod
    def all_sorting_options(cls):
        """
        Returns all possible sortings
        """
        return [
            cls.SORT_BY_NR_VIEWS,
            cls.SORT_BY_NR_ATTEMPTS,
            cls.SORT_BY_AVG_GRADE,
        ]

    @classmethod
    def all_sorting_fields(cls):
        """
        Returns a list of all the sorting fields
        """
        return [
            sorting_option[0] for sorting_option in cls.all_sorting_options()
        ]

    @classmethod
    def get_sorting_option(cls, field):
        """
        Returns the sorting option tuple given the field
        """
        if field not in cls.all_sorting_fields():
            field = cls.DEFAULT_SORTING_FIELD
        return (field, dict(cls.all_sorting_options()).get(field))

    @classmethod
    def all_sorting_options_but(cls, field):
        """
        Returns all the sorting options but the one with the specified field
        """
        return [
            sorting_option for sorting_option in cls.all_sorting_options()
            if sorting_option[0] != field
        ]
