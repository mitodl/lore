define('learning_resources',
  ['react', 'learning_resource_panel'],
  function (React, LearningResourcePanel) {
    'use strict';

    return {
      /** Current list of options are:
        repoSlug
        learningResourceId
        refreshFromAPI
        markDirty
        closeLearningResourcePanel
      */
      loader: function (options, container) {
        // Unmount and remount the component to ensure that its state
        // is always up to date with the rest of the app.
        React.unmountComponentAtNode(container);
        React.render(<LearningResourcePanel {...options} />, container);
      }
    };
  });
