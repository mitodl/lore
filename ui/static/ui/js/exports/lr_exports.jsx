define("lr_exports", ["react", "exports_component", "exports_header"],
  function (React, ExportsComponent, ExportsHeader) {
    'use strict';

    return {
      loader: function (repoSlug, loggedInUser, clearExports, container) {
        React.unmountComponentAtNode(container);
        React.render(
          <ExportsComponent repoSlug={repoSlug} loggedInUser={loggedInUser}
                            interval={1000}
                            clearExports={clearExports}
            />,
          container
        );
      },
      loadExportsHeader: function (exportCount, container) {
        React.unmountComponentAtNode(container);
        React.render(
          <ExportsHeader exportCount={exportCount}/>,
          container
        );
      }
    };
  }
);
