##############
LORE Test Plan
##############

LORE is known to render differently in Firefox and Chrome, with Chrome
producing less satisfactory results. So testing on Chrome is
recommended.


************
Repositories
************


===================
Create a repository
===================

.. note::

  You may only create a repository if you have the ``staff`` role
  in Django.

.. list-table::
   :widths: 20 35 25
   :header-rows: 1

   * - Action
     - Result
     - Notes
   * - On home page, click ``Create Repository`` link.
     - The repository listing page appears.
     -
   * - On ``Create Repository`` page, enter repository title and
       description. Both are required. Click ``Add Repo``.
     - The repository listing
     -

*******
Courses
*******

===============
Import a course
===============

.. note::

  Since many LORE issues are related to large size and "creative" content,
  import large and potentially problematic courses such as 8.01x ().

  A large course import can be slow, anywhere from several minutes to
  several hours.

.. list-table::
   :widths: 20 35 25
   :header-rows: 1

   * - Action
     - Result
     - Notes
   * - From the listing page, click ``Import Course``.
     -
     -
   * - Click ``Browse`` to select a course bundled in ``tar.gz`` format.
       Once selected, click ``Upload Course``.
     - Course title appears in 'Course' facet list with the total number
       of LRs following the title.
     -

**********
Taxonomies
**********

Include occasional non-alphanumeric characters in vocabulary and term names.

===========================================
Create vocabulary for a range of term types
===========================================

.. list-table::
   :widths: 20 35 25
   :header-rows: 1

   * - Action
     - Result
     - Notes
   * - Open ``Manage Taxonomy`` pane and click the ``Add Vocabulary`` tab.
     - Enter ``Name`` and ``Description`` fields, both are required.
     - Consider using unicode and punctuation in the names.
   * - Select item types and click ``Managed`` and leave other
       choices unchecked. Click ``Save``.
     - The Vocabularies tab appears with the created vocabulary at the
       bottom of the list. In addition, the vocabulary will appear in
       the facet panel with the psuedo term ``not tagged``.
     -
   * - Repeat the initial step, this time select item types and
       click ``Tag Style (on the fly)``.  Click ``Save``.
     -
     -
   * - Repeat the steps to create ``Managed`` and ``Tag Style``
       vocabularies, but this time click ``Allow multiple terms...``
       and save as before.
     -
     -

=========
Add terms
=========

.. list-table::
   :widths: 20 35 25
   :header-rows: 1

   * - Action
     - Result
     - Notes
   * -
     -
     -
   * -
     -
     -
   * -
     -
     -

===================
Assign terms to LRs
===================

.. list-table::
   :widths: 20 35 25
   :header-rows: 1

   * - Action
     - Result
     - Notes
   * - Click a LR to open it's detail pane and navigate to the
       ``Metadata`` tab.
     - You will see ``Vocabularies`` and ``Terms`` dropdown controls.
     - You must have created a vocabulary containing at least one term
       to assign terms to LRs.
   * -
     -
     -

=====================
Edit unassigned terms
=====================

.. list-table::
   :widths: 20 35 25
   :header-rows: 1

   * - Action
     - Result
     - Notes
   * -
     -
     -

===================
Edit assigned terms
===================

.. list-table::
   :widths: 20 35 25
   :header-rows: 1

   * - Action
     - Result
     - Notes
   * -
     -
     -

=======================
Delete unassigned terms
=======================

.. list-table::
   :widths: 20 35 25
   :header-rows: 1

   * - Action
     - Result
     - Notes
   * -
     -
     -

=====================
Delete assigned terms
=====================

.. list-table::
   :widths: 20 35 25
   :header-rows: 1

   * - Action
     - Result
     - Notes
   * -
     -
     -

************
Vocabularies
************

.. list-table::
   :widths: 20 35 25
   :header-rows: 1

   * - Action
     - Result
     - Notes
   * -
     -
     -

******
Facets
******

.. list-table::
   :widths: 20 35 25
   :header-rows: 1

   * - Action
     - Result
     - Notes
   * - Click on twisty to collapse Course facet
     - Twisty changes direction and course facets are hidden.
     -

******
Search
******

.. list-table::
   :widths: 20 35 25
   :header-rows: 1

   * - Action
     - Result
     - Notes
   * - Enter "momentum" in the search control and click the magnifying glass icon.
     -
     -

***********************
Learning Resources (LR)
***********************

.. list-table::
   :widths: 20 35 25
   :header-rows: 1

   * - Action
     - Result
     - Notes
   * - Open the LR pane.
     - A three-tabbed pane will slide out from the right side of the page.
     -

******
Export
******

.. list-table::
   :widths: 20 35 25
   :header-rows: 1

   * - Action
     - Result
     - Notes
   * - Click multiple LR 'export' links
     - The arrow on the link becomes a check and a blue button labeled
       "Export" appears in the upper right corner of the page.
     - Include one or more of each LR type and include some that have
       static assets.
   * - Click the big blue 'Export' button
     - A dialog will appear to download the export file.
     -
   * - Click "OK" to download the CSV file
     - What happens when the file is downloaded depends on how your computer
       configuration. You may see a CSV file, a directory of the file's
       contents, or the file opened by a spreadsheet app
     -
   * - Verify that the contents of the file match the LRs and static assets
       selected for download.
     - The directory structure of the file contents should have directories
       for each LR type containing static assets in a subdirectory.
     -

****
Sort
****

To fully test the sort feature, the repository must contain analytics data.
A script can be run to load fake analytics data if the analytics service is
still unavailable.

.. list-table::
   :widths: 20 35 25
   :header-rows: 1

   * - Action
     - Result
     - Notes
   * - Sort by 'Number of Views (desc)'
     -
     -
   * - Sort by 'Number of Attempts (desc)'
     -
     -
   * - Sort by 'Average Grade (desc)'
     -
     -
   * - Sort by 'Title (asc)'
     -
     -

****************************
Authentication/Authorization
****************************

.. list-table::
   :widths: 20 35 25
   :header-rows: 1

   * - Action
     - Result
     - Notes
   * -
     -
     -

*******
Members
*******

==========
Add member
==========

.. note::

  - Members must be known to the site before you can add them. They become
    known to the site by navigating to the site and authenticating.
  - While it appears that LORE validates the email, it does not. Validation
    is an artifact of the authentication process.

.. list-table::
   :widths: 20 35 25
   :header-rows: 1

   * - Action
     - Result
     - Notes
   * - Add a member as Administrator
     -
     -
   * - Add a member as Curator
     -
     -
   * - Add a member as Author
     -
     -
   * - Delete an Administrator
     -
     -
   * - Delete the last Administrator for the repository
     -
     -
   * - Delete a Curator
     -
     -
   * - Delete an Author
     -
     -
