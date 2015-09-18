"""
Tests for search endpoint.
"""

from __future__ import unicode_literals

from six.moves import urllib_parse

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_405_METHOD_NOT_ALLOWED,
)

from learningresources.api import create_repo
from learningresources.models import LearningResource, get_preview_url
from rest.tests.base import (
    RESTTestCase,
    REPO_BASE,
    as_json,
)
from search.sorting import LoreSortingFields
from taxonomy.models import Term, Vocabulary


class TestSearch(RESTTestCase):
    """
    Tests for search endpoint.
    """

    def get_results(self, query="", selected_facets=None, sortby=""):
        """Helper method to get search results."""
        if selected_facets is None:
            selected_facets = []

        selected_facets_arg = ""
        for facet in selected_facets:
            selected_facets_arg += "&selected_facets={facet}".format(
                facet=urllib_parse.quote_plus(facet)
            )
        resp = self.client.get(
            "{repo_base}{repo_slug}/search/?q={query}{facets}"
            "&sortby={sortby}".format(
                repo_base=REPO_BASE,
                repo_slug=self.repo.slug,
                query=urllib_parse.quote_plus(query),
                facets=selected_facets_arg,
                sortby=sortby
            )
        )
        self.assertEqual(HTTP_200_OK, resp.status_code)
        return as_json(resp)

    def assert_result_equal(self, result, resource):
        """Helper method to assert result == resource."""

        self.assertEqual(
            {
                'course': resource.course.course_number,
                'description': resource.description,
                'description_path': resource.description_path,
                'id': resource.id,
                'preview_url': get_preview_url(resource),
                'resource_type': resource.learning_resource_type.name,
                'run': resource.course.run,
                'title': resource.title,
                'xa_avg_grade': resource.xa_avg_grade,
                'xa_nr_attempts': resource.xa_nr_attempts,
                'xa_nr_views': resource.xa_nr_views,
            },
            result
        )

    def test_methods(self):
        """
        Verify that write methods won't work
        """
        url = "{repo_base}{repo_slug}/search/?q={query}".format(
            repo_base=REPO_BASE,
            repo_slug=self.repo.slug,
            query=""
        )

        self.assertEqual(
            HTTP_405_METHOD_NOT_ALLOWED, self.client.post(url).status_code)
        self.assertEqual(
            HTTP_405_METHOD_NOT_ALLOWED, self.client.patch(url).status_code)
        self.assertEqual(
            HTTP_405_METHOD_NOT_ALLOWED, self.client.put(url).status_code)

    def test_blank(self):
        """
        Verify that a blank search will retrieve all results.
        """
        self.import_course_tarball(self.repo)
        no_q_url = "{repo_base}{repo_slug}/search/".format(
            repo_base=REPO_BASE,
            repo_slug=self.repo.slug,
        )

        count = self.get_results()['count']
        self.assertEqual(LearningResource.objects.count(), count)

        resp = self.client.get(no_q_url)
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertEqual(count, as_json(resp)['count'])

    def test_empty(self):
        """
        Verify a case with zero results.
        """
        self.assertEqual(0, self.get_results("zebra")['count'])
        LearningResource.objects.all().delete()

        results = self.get_results()
        self.assertEqual(0, results['count'])
        facet_counts = results['facet_counts']
        self.assertEqual(
            facet_counts['run'],
            {
                'facet': {'key': 'run', 'label': 'Run', 'missing_count': 0},
                'values': []
            })
        self.assertEqual(
            facet_counts['course'],
            {
                'facet': {
                    'key': 'course', 'label': 'Course', 'missing_count': 0},
                'values': []
            })
        self.assertEqual(
            facet_counts['resource_type'],
            {
                'facet': {
                    'key': 'resource_type', 'label': 'Item Type',
                    'missing_count': 0
                },
                'values': []
            })

    def test_spaces(self):
        """
        Verify handling of spaces.
        """
        self.assertEqual(1, self.get_results("silly example")['count'])

    def test_repository_facet(self):
        """
        Verify that searches stay within repository.
        """
        repo2 = create_repo("repo2", "repo2", self.user.id)
        self.import_course_tarball(repo2)
        self.assertEqual(1, self.get_results()['count'])

        self.import_course_tarball(self.repo)
        self.assertEqual(19, self.get_results()['count'])

    def test_results(self):
        """
        Verify that the results are formatted correctly.
        """
        result = self.get_results()['results'][0]
        resource_id = result['id']
        resource = LearningResource.objects.get(id=resource_id)
        self.assert_result_equal(result, resource)

    def test_num_queries(self):
        """
        Make sure we're not hitting the database for the search
        more than necessary.
        """
        with self.assertNumQueries(7):
            self.get_results()

    def test_sortby(self):
        """
        Test that sortby works as expected.
        """
        self.import_course_tarball(self.repo)

        # Pick some resources in the middle to set xa_ values.
        all_resources = LearningResource.objects.order_by("id").all()
        resource1 = all_resources[0]
        resource2 = all_resources[1]
        resource3 = all_resources[2]
        # remove all the learning resources we do not need to
        # avoid interferences
        for resource in all_resources[3:]:
            resource.delete()

        resource1.xa_avg_grade = 2.0
        resource1.xa_nr_attempts = 4
        resource1.xa_nr_views = 1000
        resource1.title = '22222'
        resource1.save()

        resource2.xa_avg_grade = 4.0
        resource2.xa_nr_attempts = 1
        resource2.xa_nr_views = 100
        resource2.title = '11111'
        resource2.save()

        resource3.xa_avg_grade = 2.0
        resource3.xa_nr_attempts = 4
        resource3.xa_nr_views = 1000
        resource3.title = '00000'
        resource3.save()

        # Default sorting should be by nr_views, descending, then id ascending.
        default_results = self.get_results()['results']
        self.assertEqual(default_results[0]['id'], resource1.id)
        self.assertEqual(default_results[1]['id'], resource3.id)
        self.assertEqual(default_results[2]['id'], resource2.id)

        nr_views_results = self.get_results(
            sortby=LoreSortingFields.SORT_BY_NR_VIEWS[0])['results']
        self.assertEqual(default_results, nr_views_results)

        avg_grade_results = self.get_results(
            sortby=LoreSortingFields.SORT_BY_AVG_GRADE[0])['results']
        self.assertEqual(avg_grade_results[0]['id'], resource2.id)
        self.assertEqual(avg_grade_results[1]['id'], resource1.id)
        self.assertEqual(avg_grade_results[2]['id'], resource3.id)

        avg_grade_results = self.get_results(
            sortby=LoreSortingFields.SORT_BY_NR_ATTEMPTS[0])['results']
        self.assertEqual(avg_grade_results[0]['id'], resource1.id)
        self.assertEqual(avg_grade_results[1]['id'], resource3.id)
        self.assertEqual(avg_grade_results[2]['id'], resource2.id)

        title_results = self.get_results(
            sortby=LoreSortingFields.SORT_BY_TITLE[0])['results']
        self.assertEqual(title_results[0]['id'], resource3.id)
        self.assertEqual(title_results[1]['id'], resource2.id)
        self.assertEqual(title_results[2]['id'], resource1.id)

        # special case for sorting by title
        resource1.title = ' uuuu'  # space at the beginning
        resource1.save()
        resource2.title = ''  # empty title
        resource2.save()
        resource3.title = '    aaa '  # many spaces around
        resource3.save()
        title_results = self.get_results(
            sortby=LoreSortingFields.SORT_BY_TITLE[0])['results']
        self.assertEqual(title_results[0]['id'], resource3.id)
        self.assertEqual(title_results[1]['id'], resource1.id)
        self.assertEqual(title_results[2]['id'], resource2.id)

    def test_facets(self):
        """
        Test run, course, resource_type and term facets.
        """
        self.import_course_tarball(self.repo)

        vocab = Vocabulary.objects.create(
            repository=self.repo,
            required=False,
            weight=1,
            name='almond',
        )
        term1 = Term.objects.create(vocabulary=vocab, label='term1', weight=1)
        term2 = Term.objects.create(vocabulary=vocab, label='term2', weight=1)

        # getting two specific type of learning resources
        resources = LearningResource.objects.filter(
            course__repository__id=self.repo.id,
            learning_resource_type__name='html'
        ).all()

        resource1, resource2 = resources[:2]
        resource1.terms.add(term1)
        resource2.terms.add(term2)

        # Run
        self.assertEqual(
            1, self.get_results(
                selected_facets=["run_exact:Febtober"])['count'])
        self.assertEqual(
            18, self.get_results(
                selected_facets=["run_exact:TT_2012_Fall"])['count'])
        self.assertEqual(
            0, self.get_results(
                selected_facets=["run_exact:zebra"])['count'])
        # Inexact facet.
        self.assertEqual(
            18, self.get_results(
                selected_facets=["run:TT_2012_Fall"])['count'])

        # Course
        self.assertEqual(
            1, self.get_results(
                selected_facets=["course_exact:infinity"])['count'])
        self.assertEqual(
            18, self.get_results(
                selected_facets=["course_exact:toy"])['count'])
        self.assertEqual(
            0, self.get_results(
                selected_facets=["course_exact:zebra"])['count'])

        # Resource type
        self.assertEqual(
            9, self.get_results(
                selected_facets=["resource_type_exact:vertical"])['count'])
        self.assertEqual(
            2, self.get_results(
                selected_facets=["resource_type_exact:chapter"])['count'])
        self.assertEqual(
            0, self.get_results(
                selected_facets=["resource_type_exact:zebra"])['count'])

        # Term
        term1_results = self.get_results(
            selected_facets=["{v}_exact:{t}".format(
                v=vocab.name,
                t=term1.label
            )]
        )
        self.assertEqual(1, term1_results['count'])
        self.assert_result_equal(term1_results['results'][0], resource1)
        term2_results = self.get_results(
            selected_facets=["{v}_exact:{t}".format(
                v=vocab.name,
                t=term2.label
            )]
        )
        self.assertEqual(1, term2_results['count'])
        self.assert_result_equal(term2_results['results'][0], resource2)
        self.assertEqual(
            0, self.get_results(
                selected_facets=["{v}_exact:{t}".format(
                    v=vocab.name,
                    t="-1"
                )]
            )['count']
        )

        # Facets with missing counts for vocabularies
        results = self.get_results()
        facet_counts = results['facet_counts']
        # No missing count for facets that are not vocabularies
        self.assertEqual(
            facet_counts['run']['facet'],
            {'key': 'run', 'label': 'Run', 'missing_count': 0}
        )
        self.assertEqual(
            facet_counts['course']['facet'],
            {'key': 'course', 'label': 'Course', 'missing_count': 0}
        )
        self.assertEqual(
            facet_counts['resource_type']['facet'],
            {'key': 'resource_type', 'label': 'Item Type', 'missing_count': 0}
        )
        # And missing count for vocabulary
        # Note there are two learning resources tagged with
        # terms at the beginning of this test
        self.assertEqual(
            facet_counts[vocab.name]['facet'],
            {
                'key': vocab.name,
                'label': vocab.name,
                'missing_count': results['count'] - 2
            }
        )
        # the missing count reflects the filtering
        # both html LR have a term
        results = self.get_results(
            selected_facets=['resource_type_exact:html'])
        facet_counts = results['facet_counts']
        self.assertEqual(results['count'], 2)
        self.assertEqual(
            facet_counts[vocab.name]['facet'],
            {
                'key': vocab.name,
                'label': vocab.name,
                'missing_count': 0
            }
        )
        # no chapter LR has a term
        results = self.get_results(
            selected_facets=['resource_type_exact:chapter'])
        facet_counts = results['facet_counts']
        self.assertEqual(results['count'], 2)
        self.assertEqual(
            facet_counts[vocab.name]['facet'],
            {
                'key': vocab.name,
                'label': vocab.name,
                'missing_count': 2
            }
        )
        # filtering by missing vocabulary
        results = self.get_results(
            selected_facets=['_missing_:{0}_exact'.format(vocab.name)])
        facet_counts = results['facet_counts']
        self.assertEqual(results['count'], 17)
        self.assertEqual(
            facet_counts[vocab.name],
            {
                'facet': {
                    'key': vocab.name,
                    'label': vocab.name,
                    'missing_count': 17
                },
                'values': []
            }
        )

        # Facet count
        facet_counts = self.get_results(
            selected_facets=["{v}_exact:{t}".format(
                v=vocab.name, t=term1.label
            )]
        )['facet_counts']
        self.assertEqual(
            facet_counts['run'],
            {
                'facet': {'key': 'run', 'label': 'Run', 'missing_count': 0},
                'values': [
                    {
                        'count': 1,
                        'key': resource1.course.run,
                        'label': resource1.course.run
                    }
                ]
            })
        self.assertEqual(
            facet_counts['course'],
            {
                'facet': {
                    'key': 'course', 'label': 'Course',
                    'missing_count': 0
                },
                'values': [{
                    'count': 1,
                    'key': resource1.course.course_number,
                    'label': resource1.course.course_number
                }]
            })
        self.assertEqual(
            facet_counts['resource_type'],
            {
                'facet': {
                    'key': 'resource_type',
                    'label': 'Item Type',
                    'missing_count': 0,
                },
                'values': [
                    {
                        'count': 1,
                        'key': resource1.learning_resource_type.name,
                        'label': resource1.learning_resource_type.name
                    }
                ]
            })
        self.assertEqual(
            facet_counts[vocab.name],
            {
                'facet': {
                    'key': vocab.name,
                    'label': vocab.name,
                    'missing_count': 0
                },
                'values': [{
                    'count': 1,
                    'key': term1.label,
                    'label': term1.label
                }]
            }
        )

    def test_selected_facets(self):
        """Test selected_facets in REST results."""
        self.import_course_tarball(self.repo)

        vocab = Vocabulary.objects.create(
            repository=self.repo,
            required=False,
            weight=1,
            name='turtle',
        )
        term1 = Term.objects.create(vocabulary=vocab, label='term1', weight=1)

        resources = LearningResource.objects.filter(
            course__repository__id=self.repo.id,
            learning_resource_type__name='html'
        ).all()

        resource1 = resources[0]
        resource1.terms.add(term1)

        selected_facets = self.get_results(
            selected_facets=["{v}_exact:{t}".format(
                v=vocab.name, t=term1.label
            )]
        )['selected_facets']
        self.assertEqual(
            selected_facets,
            {
                '{v}'.format(v=vocab.name): {'{t}'.format(
                    t=term1.label): True},
                'course': {},
                'resource_type': {},
                'run': {}
            }
        )

        # Because we're faceting on something that doesn't exist
        # we should have no checkboxes that show up.
        selected_facets = self.get_results(
            selected_facets=["{v}_exact:{t}".format(
                v=vocab.name, t=term1.label
            ), "run_exact:doesnt_exist"]
        )['selected_facets']
        self.assertEqual(
            selected_facets,
            {
                '{v}'.format(v=vocab.name): {},
                'course': {},
                'resource_type': {},
                'run': {}
            }
        )

        selected_missing_facets = self.get_results(
            selected_facets=["_missing_:{v}_exact".format(v=vocab.name)]
        )['selected_missing_facets']
        self.assertEqual(
            selected_missing_facets,
            {
                "{v}".format(v=vocab.name): True
            }
        )

        selected_missing_facets = self.get_results()['selected_missing_facets']
        self.assertEqual(selected_missing_facets, {})
