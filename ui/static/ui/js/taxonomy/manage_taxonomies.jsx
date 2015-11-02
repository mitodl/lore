define('manage_taxonomies', ['react', 'taxonomy_component'],
  function (React, TaxonomyComponent) {
  'use strict';

  return {
    'loader': function (repoSlug, container, showConfirmationDialog,
                        showTab, setTabName, refreshFromAPI
    ) {
      // Unmount and remount the component to ensure that its state
      // is always up to date with the rest of the app.
      React.unmountComponentAtNode(container);

      React.render(
        <TaxonomyComponent
          repoSlug={repoSlug}
          refreshFromAPI={refreshFromAPI}
          renderConfirmationDialog={showConfirmationDialog}
          showTab={showTab}
          setTabName={setTabName}
          />,
        container
      );
    }
  };
});
