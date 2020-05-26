from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Line, Rectangle, InstructionGroup
from kivy.core.window import Window

from actions import Actions

import math
import subprocess
import os

COLOR_RED = (1, 0, 0)
COLOR_GREEN = (0, 1, 0)
COLOR_BLUE = (0, 0, 1)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (1, 1, 1)


class QuickSketchWidget(Widget):
    
    def __init__(self, **kwargs):
        super(QuickSketchWidget, self).__init__(**kwargs)
        self.config_keyboard()
        Window.bind(mouse_pos=self.on_mouse_pos)
        
        self.text_input = TextInput(pos=(0, 0), size=(750, 50))
        self.text_input.multiline = False
        self.add_widget(self.text_input)
        self.text_input.bind(on_text_validate=self.on_text)
        self.text_input.bind(focus=self.on_text_focus)
        
        self.color = COLOR_BLACK
        self.action = Actions.SELECT
        
        self.last_mouse_pos = ()
        self.action_start_pos = ()
        
        self.shapes = []
        self.undo_buffer = []
        self.is_adding_shape = False
        
        self.stroke_width = 1
        self.object_fill = True
        self.draw_uniformly = False
        
        self.line_points = []
        
        self.text = ""
        self.labels = []
        self.is_placing_text = False
        self.font_size = 30

    # def reposition_text_input(self, root, *args):
    #     self.b1.x = root.x
    #     self.b1.center_y = root.center_y
    
    def config_keyboard(self):
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)
    
    def on_text(self, instance):
        self.text = instance.text
        instance.text = ""
        self.escape()
        self.config_keyboard()
        self.action = Actions.PLACE_TEXT

    def on_text_focus(self, instance, value):
        if not value:
            # user defocused
            self.escape()
            self.config_keyboard()
    
    def on_mouse_pos(self, window, position):
        self.last_mouse_pos = position
        # print(position)
        if self.action == Actions.SELECT:
            pass
        else:
            if self.action == Actions.PLACE_TEXT:
                if self.is_placing_text:
                    item = self.labels.pop(-1)
                    self.remove_widget(item)
                else:
                    self.is_placing_text = True
    
                label = Label(pos=(position[0]-40, position[1]-40), text=self.text, color=list(self.color)+[1], font_size=self.font_size)
                self.labels.append(label)
                self.add_widget(label)
            else:
                instr = InstructionGroup()
                instr.add(Color(*self.color))
    
                if self.is_adding_shape:
                    item = self.shapes.pop(-1)
                    self.canvas.remove(item)
                else:
                    self.is_adding_shape = True
                
                if self.action == Actions.LINE:
                    instr.add(Line(points=[self.action_start_pos, position], width=self.stroke_width / 2))
                
                elif self.action == Actions.FREEHAND:
                    self.line_points.append(position)
                    instr.add(Line(points=self.line_points, width=self.stroke_width / 2))
                    
                elif self.action == Actions.TEXT:
                    pass
                
                else:  # BOX or ELLIPSE
                    w = position[0] - self.action_start_pos[0]
                    h = position[1] - self.action_start_pos[1]
                    
                    sw = math.copysign(1, w)
                    sh = math.copysign(1, h)
                    
                    if self.draw_uniformly:
                        x = min(abs(w), abs(h))
                        w = sw * x
                        h = sh * x
                    
                    start_x = self.action_start_pos[0]
                    start_y = self.action_start_pos[1]
                    
                    if self.action == Actions.BOX:
                        instr.add(Rectangle(pos=(start_x, start_y), size=(w, h)))
                    else:
                        instr.add(Ellipse(pos=(start_x, start_y), size=(w, h)))
                    
                    if not self.object_fill:
                        w += -sw * 2 * self.stroke_width
                        start_x += sw * self.stroke_width
                        
                        h += -sh * 2 * self.stroke_width
                        start_y += sh * self.stroke_width
                        
                        instr.add(Color(*COLOR_WHITE))
                        if self.action == Actions.BOX:
                            instr.add(Rectangle(pos=(start_x, start_y), size=(w, h)))
                        else:
                            instr.add(Ellipse(pos=(start_x, start_y), size=(w, h)))
                
                self.shapes.append(instr)
                self.canvas.add(instr)
    
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        key = keycode[1]
        
        if 'shift' in modifiers:
            self.draw_uniformly = True
            # changing color
            if key == 'r':
                self.color = COLOR_RED
            elif key == 'g':
                self.color = COLOR_GREEN
            elif key == 'b':
                self.color = COLOR_BLUE
            elif key == 'z':
                self.color = COLOR_BLACK
            elif key == 'w':
                self.color = COLOR_WHITE
            elif key in Actions.keymap and Actions.keymap[key] == Actions.SELECT:
                self.select()
            elif key == 'escape':
                self.escape()
        
        elif 'alt' in modifiers:
            if key == 'x':
                self.canvas.clear()
                self.shapes = []
                self.undo_buffer = []
                self.line_points = []
                self.is_adding_shape = False
                self.is_placing_text = False
                self.add_widget(self.text_input)
        
        elif 'ctrl' in modifiers:
            print("saving image")
            
            name = "screenshot.jpg"
            
            self.remove_widget(self.text_input)
            
            Window.screenshot(name=name)
            subprocess.run(
                ["osascript", "-e", 'set the clipboard to (read (POSIX file "screenshot0001.jpg") as JPEG picture)'])
            os.remove("screenshot0001.jpg")
            
            self.add_widget(self.text_input)
        
        else:
            # action
            self.draw_uniformly = False
            
            if key in Actions.keymap:
                self.action = Actions.keymap[key]
                self.action_start_pos = self.last_mouse_pos
                
                if Actions.keymap[key] == Actions.SELECT:
                    self.select()
                elif Actions.keymap[key] == Actions.TEXT:
                    self.text_input.focus = True
            
            else:
                if key == 'escape':
                    self.escape()
                elif key == 'q':
                    self.stroke_width += 2
                elif key == 'a':
                    if self.stroke_width > 2:
                        self.stroke_width -= 2
                elif key == '2':
                    self.font_size += 5
                elif key == '1':
                    if self.font_size > 5:
                        self.font_size -= 5
                elif key == 'f':
                    self.object_fill = not self.object_fill
                elif key == 'u':
                    if len(self.shapes) > 0:
                        item = self.shapes.pop(-1)
                        self.undo_buffer.append(item)
                        self.canvas.remove(item)
                elif key == 'r':
                    if len(self.undo_buffer) > 0:
                        item = self.undo_buffer.pop(-1)
                        self.shapes.append(item)
                        self.canvas.add(item)
        return True
    
    def _on_keyboard_up(self, keyboard, keycode):
        if keycode[1] == 'shift':
            self.draw_uniformly = False
        elif keycode[1] == 'c':
            self.select()
    
    def select(self):
        self.action_start_pos = None
        self.is_adding_shape = False
        self.is_placing_text = False
        self.line_points = []
        self.action = Actions.SELECT
    
    def escape(self):
        # remove last object
        if self.is_adding_shape:
            item = self.shapes.pop(-1)
            self.canvas.remove(item)
        
        if self.is_placing_text:
            item = self.labels.pop(-1)
            self.remove_widget(item)
        
        self.select()
        self.action = Actions.SELECT


class QuickSketchApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)
        return QuickSketchWidget()


if __name__ == '__main__':
    QuickSketchApp().run()
