# React addons

1. Basic helpers for CoffeeScript (https://github.com/atom/reactionary).
2. Stuff from `react-with-addons.js` of react.js

## Usage

The functions reside in `React.addons`.

To use coffeescript tags:

```coffeescript
{div} = React.addons

Cursor = React.createClass
  render: ->
    {pixelRect, defaultCharWidth} = @props
    {top, left, height, width} = pixelRect
    width = defaultCharWidth if width is 0
    WebkitTransform = "translate(#{left}px, #{top}px)"

    div className: 'cursor', style: {height, width, WebkitTransform}
```
