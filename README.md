# Quick Sketch
A light app to draw basic diagrams for notes, relying heavily on keyboard shortcuts.

Created by Tejas Narayanan

## Instructions
The shortucts are designed such that a user's left hand is on
the home row, while their right hand is on the trackpad or mouse.

### Primary actions
Key | Action
---|---
`v` or `space` | Normal, confirm an object
`e` | Ellipse
`b` | Box
`s` | Line
`c` (hold) | Freehand
`t` | Text
`escape` | Exit object addition
`control` | Copy the image to clipboard (macOS only)

### Secondary actions
Key | Action
---|---
`shift` (hold) | Make uniform shapes (circles and squares)
`q` | Increase stroke width
`a` | Decrease stroke width
`f` | Toggle object fill
`u` | Undo
`r` | Redo
`alt+x` | Clear screen

### Colors
Key | Color
---|---
`shift+z` | Black
`shift+w` | White
`shift+r` | Red
`shift+g` | Green
`shift+b` | Blue

## Dependencies
Quick Sketch was developed on `Python 3.7.7`, and requires `kivy 1.11.1`. It has not been tested with other
versions of `python` or `kivy`.

## Compatibility
Currently, Quick Sketch only works on macOS because of the use of an Applescript to copy an image to the clipboard.
However, I plan on making it compatible for Windows and Linux as well.