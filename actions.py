class Actions:
    SELECT = 0
    ELLIPSE = 1
    BOX = 2
    LINE = 3
    ARROW = 4
    BEZIER = 5
    FREEHAND = 6
    TEXT = 7
    PLACE_TEXT = 8
    PLACE_COPY = 9
    
    keymap = {
        'spacebar': SELECT,
        'e': ELLIPSE,
        'b': BOX,
        's': LINE,
        'w': BEZIER,
        'v': ARROW,
        '`': FREEHAND,
        't': TEXT
    }
