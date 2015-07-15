Release Notes
-------------

Version 0.4.0
=============

- Added view to serve static assets and modified REST API
- Added fix and test for handling deleted Elasticsearch index.
- Refactored manage_taxonomies.jsx and related tests
- Sped up test discovery by removing node_modules from search
- Added learning resource types to manage taxonomies UI
- Added learning_resource_types API and learning_resource_types field for
  vocabularies
- Fixed bug with file path length in static assets
- Added learning resource UI to edit description and terms
- Upgraded several packages
    - Bootstrap
    - uwsgi
    - static3
    - elasticsearch
    - django-bootstrap
    - django-storages-redux
- Added terms to the readonly list
- Allowed blank descriptions for LearningResource model
- Implemented Enter key to add taxonomy term and added test case to
  fix coverage
- Updated Django to 1.8.3
- Correct LORE production URL in Apiary doc
- Added checkbox styling to vocabulary/term facets
- Fixed error message on unsupported terms in learning resource
- Fixed facet checkboxes not showing in production
- Fixed course/run highlight bug
- Default checked radio button for Manage Taxonomies -> Add Vocabulary
- Fixed vertical alignment of taxonomy tabs
- Fixed error message for duplicate vocabulary
- Added docker container for javascript testing
- Added checkboxes and ability to toggle facets
- Added html coverage report for javascript
- Added shim configuration to karma test runner
- Implemented learning_resources API
- Members REST API docs
- Linked video transcripts to learning resources.
- Parse static assets from LearningResource
- Removed unused patterns to limit memory use
- fix css to make list vertical align
- Installed JSXHint and configured JSCS to work with JSX files
- Included JSX files in coverage results
- Allow only usernames and not emails in the Members add input
- Added test case, tested menulay all scenarios
- Moved coverage CLI script to utils directory
- Fixed buttons alignment problem in members panel.
- Fixed error message behavior for manage taxonomies tab
- Added ability to filter vocabularies by learning resource type

Version 0.3.0
=============

- Added UI to add and remove repository members.
- Added form for adding new vocabularies.
- Added manage taxonomies panel and button
- REST for repo members
- Implemented taxonomy model delete cascading.
- Renamed "Copy to Clipboard" to "Select XML"
- Setup JSX processing requirements.
- Fixed mis-resolutioned learning resource type icons.
- Converted several large HTML blocks into include files.
- Switched from using main.js for everything to multiple modules.
- Installed lodash.
- Added CSRF jQuery initialization code.

Version 0.2.0
=============

- The search bar performs full-text search over the learning resources
  in the repository, the search results replace the contents of the
  listing page.
- Full-text search includes taxonomy facets.
- Learning resources details are displayed in a panel that slides out
  from the right side of the page.
- Glyphs for learning resources types are displayed in the left side
  panel for facets.
- LORE's RESTful web service documentation is available.
  (http://docs.lore.apiary.io)
- Authorizations are in place for taxonomy endpoints in LORE's web
  service.
- Relationships between learning resources and static assets are
  captured.
- Roles app has additional features.

Other Changes
*************

- Switched to using get_perms for cleaner code.
- Added JavaScript infrastructure to run unit tests.

Version 0.1.0
=============

- Added taxonomy app with models
- Add learning resources app
- Basic Import Functionality
- CAS Integration
- Added forms to taxonomy app
- Added welcome page
- Logging support
- Added sphinx documentation project
- Added add and edit forms for vocabularies
- Added listing page
- Added base UI templates
- Styled listing page
- Added footer to listing page
- Added link to repository in repository base template
- Added support for asynchronous course imports
- Added rest app with support for RESTful API
- Added initial authorization support
- Added login requirement for taxonomy app
- Switched to using django storage for course uploads
- Switched to using Haystack/ElasticSearch for listing page
- Protected course imports
- Protected export view
- Added faceted filtering
- Added new manage repo users permission
- Fixed repository listing page to only show results for a single repo.
