define('learning_resources',
  ['react', 'learning_resource_panel'],
  function (React, LearningResourcePanel) {
    'use strict';

    return {
      loader: function (repoSlug, learningResourceId, refreshFromAPI,
                        closeLearningResourcePanel, container) {
        // Unmount and remount the component to ensure that its state
        // is always up to date with the rest of the app.
        React.unmountComponentAtNode(container);
        React.render(<LearningResourcePanel
          repoSlug={repoSlug}
          learningResourceId={learningResourceId}
          refreshFromAPI={refreshFromAPI}
          closeLearningResourcePanel={closeLearningResourcePanel}
          />, container);
      }
    };
  });
