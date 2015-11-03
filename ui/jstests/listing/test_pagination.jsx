define(['QUnit', 'jquery', 'pagination', 'react',
  'test_utils'],
  function(QUnit, $, Pagination, React, TestUtils) {
    'use strict';

    var PaginationComponent = Pagination.Pagination;

    QUnit.module('Test pagination', {
      beforeEach: function () {
        TestUtils.setup();
      },
      afterEach: function () {
        TestUtils.cleanup();
      }
    });

    QUnit.test('Assert pagination state changes', function(assert) {
      var done = assert.async();

      var newPage = null;
      var updatePage = function(page) {
        newPage = page;
      };

      var afterMount = function(component) {
        assert.deepEqual(component.state, {
          isEditing: false,
          textPageNum: 3
        });

        // Left click
        var $node = $(React.findDOMNode(component));
        React.addons.TestUtils.Simulate.click($node.find("a")[0]);
        component.forceUpdate(function() {
          assert.equal(newPage, 2);

          // Right click
          React.addons.TestUtils.Simulate.click($node.find("a")[2]);
          component.forceUpdate(function() {
            assert.equal(newPage, 4);

            // Middle click
            React.addons.TestUtils.Simulate.click($node.find("a")[1]);
            component.forceUpdate(function() {
              assert.deepEqual(component.state, {
                isEditing: true,
                textPageNum: 4
              });

              // Change text value
              React.addons.TestUtils.Simulate.change($node.find("input")[0], {
                target: {
                  value: 1
                }
              });
              component.forceUpdate(function() {
                assert.deepEqual(component.state, {
                  isEditing: true,
                  textPageNum: 1
                });

                // Hit enter
                React.addons.TestUtils.Simulate.keyUp($node.find("input")[0], {
                  key: "Enter"
                });
                component.forceUpdate(function() {
                  assert.deepEqual(component.state, {
                    isEditing: false,
                    textPageNum: 1
                  });
                  assert.equal(newPage, 1);

                  // Bring back textbox
                  React.addons.TestUtils.Simulate.click($node.find("a")[1]);
                  component.forceUpdate(function() {
                    newPage = null;

                    // Focus elsewhere
                    $node.find("a").first().focus();
                    component.forceUpdate(function() {
                      // Loss of focus caused page to be set
                      assert.deepEqual(component.state, {
                        isEditing: false,
                        textPageNum: 1
                      });
                      assert.equal(newPage, 1);

                      $("#testingDiv").remove();
                      done();
                    });
                  });
                });
              });
            });
          });
        });
      };

      // Must render on page to test loss of focus
      $("body").append($("<div id='testingDiv' />"));

      React.render(
        <PaginationComponent
          numPages={5}
          pageNum={3}
          updatePage={updatePage}
          ref={afterMount}
          />, $("#testingDiv")[0]
      );
    });

    QUnit.test('Assert that loader works', function(assert) {
      var div = document.createElement("div");
      assert.equal(0, $(div).html().length);
      Pagination.loader(1, 1, function() {}, div);
      assert.ok($(div).html().length > 0);
    });

    QUnit.test('Assert no previous link if at page 1', function(assert) {
      var done = assert.async();
      var afterMount = function(component) {
        var $node = $(React.findDOMNode(component));

        assert.equal($node.find(".fa-angle-right").size(), 1);
        assert.equal($node.find(".fa-angle-left").size(), 0);

        done();
      };

      React.addons.TestUtils.renderIntoDocument(
        <PaginationComponent
          numPages={3}
          pageNum={1}
          updatePage={function() {}}
          ref={afterMount}
          />
      );
    });

    QUnit.test('Assert next link works after pagination change (#651)',
      function(assert) {
        var done1 = assert.async();
        var done2 = assert.async();
        var done3 = assert.async();

        // this test takes place in three callbacks
        // nextMount will point to the next callback in line
        var nextMount;
        var firstMount;
        var afterEnter;
        var afterNextClick;

        firstMount = function (component) {
          nextMount = afterEnter;

          var $node = $(React.findDOMNode(component));

          // Middle click
          React.addons.TestUtils.Simulate.click($node.find("a")[0]);
          component.forceUpdate(function() {
            assert.deepEqual(component.state, {
              isEditing: true,
              textPageNum: 1
            });
            // Change page
            React.addons.TestUtils.Simulate.change($node.find("input")[0], {
              target: {
                value: 2
              }
            });
            component.forceUpdate(function() {
              assert.deepEqual(component.state, {
                isEditing: true,
                textPageNum: 2
              });

              // Hit enter
              React.addons.TestUtils.Simulate.keyUp($node.find("input")[0], {
                key: "Enter"
              });
              done1();
            });

          });

        };

        afterEnter = function(component) {
          nextMount = afterNextClick;
          var $node = $(React.findDOMNode(component));
          component.forceUpdate(function () {
            assert.deepEqual(component.state, {
              isEditing: false,
              textPageNum: 2
            });

            // Right click
            React.addons.TestUtils.Simulate.click($node.find("a")[2]);
            done2();
          });
        };

        afterNextClick = function(component) {
          nextMount = null;
          assert.deepEqual(component.state, {
            isEditing: false,
            textPageNum: 3
          });
          done3();
        };

        var render;
        var updatePage = function(newPageNum) {
          render(newPageNum);
        };

        nextMount = firstMount;

        render = function(pageNum) {
          React.addons.TestUtils.renderIntoDocument(
            <PaginationComponent
              numPages={3}
              pageNum={pageNum}
              updatePage={updatePage}
              ref={nextMount}
              />
          );
        };

        render(1);
      }
    );
    QUnit.test('Assert no next link if at last page', function(assert) {
      var done = assert.async();
      var afterMount = function(component) {
        var $node = $(React.findDOMNode(component));

        assert.equal($node.find(".fa-angle-right").size(), 0);
        assert.equal($node.find(".fa-angle-left").size(), 1);

        done();
      };

      React.addons.TestUtils.renderIntoDocument(
        <PaginationComponent
          numPages={3}
          pageNum={3}
          updatePage={function() {}}
          ref={afterMount}
          />
      );
    });

    QUnit.test('Assert nothing displayed if only one page', function(assert) {
      var done = assert.async();
      var afterMount = function(component) {
        var $node = $(React.findDOMNode(component));

        assert.equal($node.html(), undefined);

        done();
      };

      React.addons.TestUtils.renderIntoDocument(
        <PaginationComponent
          numPages={1}
          pageNum={1}
          updatePage={function() {}}
          ref={afterMount}
          />
      );
    });
  }
);
