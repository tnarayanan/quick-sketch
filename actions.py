class Actions:
    SELECT = 0
    ELLIPSE = 1
    BOX = 2
    LINE = 3
    ARROW = 4
    FREEHAND = 5
    TEXT = 6
    PLACE_TEXT = 7
    
    keymap = {
        'spacebar': SELECT,
        'e': ELLIPSE,
        'b': BOX,
        's': LINE,
        'v': ARROW,
        'c': FREEHAND,
        't': TEXT
    }
