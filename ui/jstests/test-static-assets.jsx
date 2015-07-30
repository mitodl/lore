define(['QUnit', 'jquery', 'static_assets', 'reactaddons',
  'test_utils'], function(
  QUnit, $, StaticAssets, React, TestUtils) {
    'use strict';

    var StaticAssetsPanel = StaticAssets.StaticAssetsPanel;
    var waitForAjax = TestUtils.waitForAjax;

    var staticAssetsResponse = {
      "count": 2,
      "next": null,
      "previous": null,
      "results": [
        {
          "id": 1,
          "asset": "http://lore.test.mit/media/assets/edX/toy/" +
            "TT_2012_Fall/subs_CCxmtcICYNc.srt_dZF2PcC.sjson",
          "name": "subs_CCxmtcICYNc.srt_dZF2PcC.sjson"
        },
        {
          "id": 2,
          "asset": "http://lore.test.mit/media/assets/edX/toy/" +
            "TT_2012_Fall/test_YpcBO8Y.txt",
          "name": "test_YpcBO8Y.txt"
        }
      ]
    };

    QUnit.module('Test static assets panel', {
      beforeEach: function() {
        TestUtils.setup();

        TestUtils.initMockjax({
          url: '/api/v1/repositories/repo/learning_resources/1/static_assets/',
          type: 'GET',
          responseText: staticAssetsResponse
        });
      },
      afterEach: function() {
        TestUtils.cleanup();
      }
    });

    QUnit.test(
      'Assert that StaticAssetsPanel loads properly',
      function(assert) {
        var done = assert.async();
        var afterMount = function(component) {
          // wait for calls to populate page
          waitForAjax(1, function () {
            // two static assets
            var $node = $(React.findDOMNode(component));
            var $vocabSelect = $node.find("li");
            assert.equal($vocabSelect.size(), 2);
            $vocabSelect = $node.find("li > a");
            assert.equal($vocabSelect.size(), 2);
            assert.equal(
              $($vocabSelect[0]).text(),
              staticAssetsResponse.results[0].name
            );
            assert.equal(
              $($vocabSelect[1]).text(),
              staticAssetsResponse.results[1].name
            );
            assert.equal(
              $($vocabSelect[0]).attr('href'),
              staticAssetsResponse.results[0].asset
            );
            assert.equal(
              $($vocabSelect[1]).attr('href'),
              staticAssetsResponse.results[1].asset
            );

            done();
          });
        };
        React.addons.TestUtils.renderIntoDocument(<StaticAssetsPanel
          repoSlug="repo"
          learningResourceId="1"
          ref={afterMount} />);
      }
    );

    QUnit.test(
      'Assert that StaticAssetsPanel Error AJAX call has a message',
      function(assert) {
        var done = assert.async();
        TestUtils.replaceMockjax({
          url: '/api/v1/repositories/repo/learning_resources/1/static_assets/',
          type: 'GET',
          status: 400
        });
        var afterMount = function(component) {
          waitForAjax(1, function() {
            assert.deepEqual(
              component.state.message,
              {error: "Unable to read information about static assets."}
            );
            var $node = $(React.findDOMNode(component));
            var $vocabSelect = $node.find("div.alert");
            assert.equal($vocabSelect.size(), 1);
            $vocabSelect = $node.find("li");
            assert.equal($vocabSelect.size(), 0);
            done();
          });
        };
        React.addons.TestUtils.renderIntoDocument(<StaticAssetsPanel
          repoSlug="repo"
          learningResourceId="1"
          ref={afterMount} />);
      }
    );

    QUnit.test(
      'Assert that loader mounts a React component', function(assert) {
        var container = document.createElement("div");
        assert.equal($(container).find("ul").length, 0);
        StaticAssets.loader("repo", 1, container);
        assert.equal($(container).find("ul").length, 1);
      }
    );
  }
);
