Release Notes
-------------

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
