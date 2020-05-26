from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
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
    
    def __init__(self, text_input, **kwargs):
        super(QuickSketchWidget, self).__init__(**kwargs)
        self.config_keyboard()
        Window.bind(mouse_pos=self.on_mouse_pos)
        
        self.background_color = list(COLOR_WHITE) + [1]
        
        self.text_input = text_input
        self.text_input.multiline = False
        self.text_input.bind(on_text_validate=self.on_text)
        self.text_input.bind(focus=self.on_text_focus)
        
        self.color = COLOR_BLACK
        self.action = Actions.SELECT
        
        self.last_mouse_pos = ()
        self.action_start_pos = ()
        self.prev_pos = ()
        
        self.object_stack = []
        self.undo_buffer = []
        
        self.curr_shape = None
        self.is_adding_shape = False
        
        self.stroke_width = 1
        self.object_fill = True
        self.draw_uniformly = False
        
        self.line_points = []
        
        self.double_arrow = False
        
        self.text = ""
        self.curr_label = None
        self.is_placing_text = False
        self.font_size = 30
        
        self.number_str = ""
    
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
        self.draw_object()
    
    def draw_object(self):
        pos = self.last_mouse_pos
        if self.action == Actions.SELECT:
            pass
        else:
            if self.action == Actions.PLACE_COPY:
                if self.is_adding_shape:
                    self.canvas.remove(self.curr_shape)
                else:
                    self.is_adding_shape = True
                
                instr = InstructionGroup()
                
                for child in self.curr_shape.children:
                    instr.add(Color(*self.color))
                    if type(child) is Line:
                        pts = []
                        for i in range(len(child.points)):
                            if i % 2 == 0:
                                # x
                                pts.append(child.points[i] - self.prev_pos[0] + pos[0])
                            else:
                                # y
                                pts.append(child.points[i] - self.prev_pos[1] + pos[1])
                        
                        if len(pts) <= 8:
                            pts += [pts[0]]
                            pts += [pts[1]]
                        
                        instr.add(Line(points=pts, width=self.stroke_width / 2))
                    elif type(child) is Ellipse:
                        instr.add(Ellipse(pos=pos, size=child.size))
                    elif type(child) is Rectangle:
                        instr.add(Rectangle(pos=pos, size=child.size))
                
                self.prev_pos = pos
                
                self.curr_shape = instr
                self.canvas.add(instr)
            
            elif self.action == Actions.PLACE_TEXT:
                if self.is_placing_text:
                    self.remove_widget(self.curr_label)
                else:
                    self.is_placing_text = True
                
                label = Label(pos=(pos[0] - 40, pos[1] - 40), text=self.text, color=list(self.color) + [1],
                              font_size=self.font_size)
                self.curr_label = label
                self.add_widget(label)
            else:
                instr = InstructionGroup()
                instr.add(Color(*self.color))
                
                if self.is_adding_shape:
                    self.canvas.remove(self.curr_shape)
                else:
                    self.is_adding_shape = True
                
                if self.action == Actions.LINE:
                    instr.add(Line(points=[self.action_start_pos, pos], width=self.stroke_width / 2))
                
                elif self.action == Actions.ARROW:
                    instr.add(Line(points=[self.action_start_pos, pos], width=self.stroke_width / 2))
                    
                    dy = self.action_start_pos[1] - pos[1]
                    dx = self.action_start_pos[0] - pos[0]
                    angle = math.degrees(math.atan2(dy, dx))
                    length = math.sqrt(dy ** 2 + dx ** 2)
                    
                    max_arrow_length = 40
                    
                    # Transformation of the sigmoid function
                    arrow_length = 2 * max_arrow_length * (math.e ** (length / 100)) / (
                            math.e ** (length / 100) + 1) - max_arrow_length
                    
                    pos_angle_pt = (pos[0] + arrow_length * math.cos(math.radians(angle + 30)),
                                    pos[1] + arrow_length * math.sin(math.radians(angle + 30)))
                    neg_angle_pt = (pos[0] + arrow_length * math.cos(math.radians(angle - 30)),
                                    pos[1] + arrow_length * math.sin(math.radians(angle - 30)))
                    
                    instr.add(Line(points=[pos, pos_angle_pt], width=self.stroke_width / 2))
                    instr.add(Line(points=[pos, neg_angle_pt], width=self.stroke_width / 2))
                    
                    if self.double_arrow:
                        angle += 180
                        pos_angle_pt = (self.action_start_pos[0] + arrow_length * math.cos(math.radians(angle + 30)),
                                        self.action_start_pos[1] + arrow_length * math.sin(math.radians(angle + 30)))
                        neg_angle_pt = (self.action_start_pos[0] + arrow_length * math.cos(math.radians(angle - 30)),
                                        self.action_start_pos[1] + arrow_length * math.sin(math.radians(angle - 30)))
                        
                        instr.add(Line(points=[self.action_start_pos, pos_angle_pt], width=self.stroke_width / 2))
                        instr.add(Line(points=[self.action_start_pos, neg_angle_pt], width=self.stroke_width / 2))
                
                elif self.action == Actions.FREEHAND:
                    self.line_points.append(pos)
                    instr.add(Line(points=self.line_points, width=self.stroke_width / 2))
                
                elif self.action == Actions.TEXT:
                    pass
                
                else:  # BOX or ELLIPSE
                    w = pos[0] - self.action_start_pos[0]
                    h = pos[1] - self.action_start_pos[1]
                    
                    sw = math.copysign(1, w)
                    sh = math.copysign(1, h)
                    
                    if self.draw_uniformly:
                        x = min(abs(w), abs(h))
                        w = sw * x
                        h = sh * x
                    
                    start_x = self.action_start_pos[0]
                    start_y = self.action_start_pos[1]
                    
                    if self.object_fill:
                        if self.action == Actions.BOX:
                            instr.add(Rectangle(pos=(start_x, start_y), size=(w, h)))
                        else:
                            instr.add(Ellipse(pos=(start_x, start_y), size=(w, h)))
                    
                    else:
                        if self.action == Actions.BOX:
                            instr.add(Line(rectangle=(start_x, start_y, w, h), width=self.stroke_width / 2))
                        else:
                            instr.add(Line(ellipse=(start_x, start_y, w, h), width=self.stroke_width / 2))
                
                self.curr_shape = instr
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
            
            self.draw_object()
        
        elif 'alt' in modifiers:
            if key == 'x':
                self.reset()
            elif key.isdigit() or (len(self.number_str) == 0 and key == '-'):
                self.number_str += key
        
        elif 'ctrl' in modifiers:
            print("saving image")
            
            name = "screenshot.jpg"
            self.export_as_image().save(name)
            
            subprocess.run(
                ["osascript", "-e", 'set the clipboard to (read (POSIX file "screenshot.jpg") as JPEG picture)'])
            os.remove("screenshot.jpg")
            
            print("saved")
        
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
                elif key == 'c':
                    self.select()
                    if len(self.object_stack) > 0:
                        if type(self.object_stack[-1]) is Label:
                            self.text = self.object_stack[-1].text
                            self.action = Actions.PLACE_TEXT
                        else:
                            self.curr_shape = self.object_stack[-1]
                            self.action = Actions.PLACE_COPY
                            self.prev_pos = self.action_start_pos
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
                elif key == 'g':
                    self.double_arrow = not self.double_arrow
                elif key == 'u':
                    if len(self.object_stack) > 0:
                        item = self.object_stack.pop(-1)
                        self.undo_buffer.append(item)
                        
                        if type(item) is Label:
                            self.remove_widget(item)
                        else:
                            self.canvas.remove(item)
                elif key == 'r':
                    if len(self.undo_buffer) > 0:
                        item = self.undo_buffer.pop(-1)
                        self.object_stack.append(item)
                        if type(item) is Label:
                            self.add_widget(item)
                        else:
                            self.canvas.add(item)
                
                self.draw_object()
        return True
    
    def _on_keyboard_up(self, keyboard, keycode):
        if keycode[1] == 'shift':
            self.draw_uniformly = False
        elif keycode[1] == '`':
            self.select()
        elif keycode[1] == 'alt':
            if len(self.number_str) > 0:
                self.text = self.number_str
                self.number_str = ""
                self.action = Actions.PLACE_TEXT
    
    def select(self, clear_undo_buffer=True):
        # self.action_start_pos = None
        self.is_adding_shape = False
        self.is_placing_text = False
        self.line_points = []
        
        if clear_undo_buffer:
            self.undo_buffer = []
        
        self.action = Actions.SELECT
        
        if self.curr_shape is not None:
            self.object_stack.append(self.curr_shape)
            print("Appending shape")
            self.action_start_pos = self.last_mouse_pos
        elif self.curr_label is not None:
            self.object_stack.append(self.curr_label)
            print("Appending label")
        
        self.curr_shape = None
        self.curr_label = None
    
    def escape(self):
        # remove last object
        if self.is_adding_shape:
            self.canvas.remove(self.curr_shape)
            self.curr_shape = None
        
        if self.is_placing_text:
            self.remove_widget(self.curr_label)
            self.curr_label = None
        
        self.select(clear_undo_buffer=False)
        self.action = Actions.SELECT
    
    def reset(self):
        self.canvas.clear()
        self.curr_shape = None
        self.curr_label = None
        self.undo_buffer = []
        self.line_points = []
        self.is_adding_shape = False
        self.is_placing_text = False
        
        with self.canvas:
            Color(COLOR_WHITE)
            Rectangle(size=self.size, pos=self.pos)
            Color(*self.color)
        
        self.select()


class QuickSketchApp(App):
    def build(self):
        box = BoxLayout(orientation='vertical')
        text_input = TextInput(size_hint=(1, None))
        text_input.height = 50
        sketch = QuickSketchWidget(text_input)
        sketch.bind(size=self._update_rect, pos=self._update_rect)
        
        with sketch.canvas.before:
            Color(COLOR_WHITE)
            self.rect = Rectangle(size=sketch.size, pos=sketch.pos)
        
        box.add_widget(sketch)
        box.add_widget(text_input)
        return box
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


if __name__ == '__main__':
    QuickSketchApp().run()
