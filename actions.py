class Actions:
    SELECT = 0
    ELLIPSE = 1
    BOX = 2
    LINE = 3
    FREEHAND = 4
    
    keymap = {
        'v': SELECT,
        'spacebar': SELECT,
        'e': ELLIPSE,
        'b': BOX,
        's': LINE,
        'c': FREEHAND
    }