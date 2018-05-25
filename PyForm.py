import pygame as pg
import pygame.gfxdraw


def render_text_pos(screen, text, font, pos, color, background=None):
    surface = font.render(text, True, color, background)
    screen.blit(surface, pos)


def render_text_rect(screen, text, font, rect, color, background=None):
    text_size = font.size(text)
    padding_left = (rect.width - text_size[0]) // 2
    padding_top = (rect.height - text_size[1]) // 2
    render_text_pos(screen, text, font, (rect.left + padding_left, rect.top + padding_top),
                    color, background)


def rect_transparent(screen, color, rect):
    s = pg.Surface((rect.width, rect.height), pygame.SRCALPHA)
    s.fill(color)
    screen.blit(s, (rect.left, rect.top))


class Control:
    def __init__(self, form=None, parent=None, left=0, top=0, width=0, height=0):
        self.form = form
        self.parent = parent if parent is not None else form
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.mouse_over = False
        self.focused = False
        self.font_name = None
        self.font_size = None
        self.set_font('Courier', 18)
        self.controls = []

    def focuse(self):
        self.focused = True

    def add_control(self, control):
        self.controls.append(control)
        control.form = self.form
        control.parent = self

    def rect(self):
        if self.parent:
            if self.parent == self.form:
                return pg.Rect(self.left + self.parent.rect().left,
                               self.top + self.parent.rect().top + self.form.title_height, self.width,
                               self.height)
            else:
                return pg.Rect(self.left + self.parent.rect().left, self.top + self.parent.rect().top, self.width,
                               self.height)

        else:
            return pg.Rect(self.left, self.top, self.width, self.height)

    def set_font(self, name=None, size=None):
        if name is not None:
            self.font_name = name
        if size is not None:
            self.font_size = size
        self.font = pg.font.SysFont(self.font_name, self.font_size)

    def mouse_in(self, event):
        self.mouse_over = True

    def mouse_out(self, event):
        self.mouse_over = False

    def mouse_down(self, event):
        if self.rect().collidepoint(event.pos):
            self.focused = True
        else:
            self.focused = False

    def mouse_up(self, event):
        if self.rect().collidepoint(event.pos):
            self.mouse_click(event)

    def mouse_click(self, event):
        pass

    def mouse_move(self, event):
        if self.rect().collidepoint(event.pos):
            if not self.mouse_over:
                self.mouse_in(event)
        else:
            if self.mouse_over:
                self.mouse_out(event)

    def key_down(self, event):
        if not self.focused:
            return

    def key_up(self, event):
        if not self.focused:
            return
        self.key_press(event)

    def key_press(self, event):
        if not self.focused:
            return

    def handle_event(self, event):
        if event.type == pg.MOUSEMOTION:
            self.mouse_move(event)
        elif event.type == pg.MOUSEBUTTONDOWN:
            self.mouse_down(event)
        elif event.type == pg.MOUSEBUTTONUP:
            self.mouse_up(event)
        elif event.type == pg.KEYDOWN:
            self.key_down(event)
        elif event.type == pg.KEYUP:
            self.key_up(event)
        for control in self.controls:
            if event.type in [pg.MOUSEMOTION, pg.MOUSEBUTTONDOWN]:
                if control.focused or control.mouse_over or control.rect().collidepoint(event.pos):
                    control.handle_event(event)
            elif event.type in [pg.KEYDOWN, pg.KEYUP, pg.MOUSEBUTTONUP] and control.focused:
                control.handle_event(event)


class Draggable(Control):
    def __init__(self, **args):
        super().__init__(**args)
        self.dragging = False
        self.last_pos = None
        self.covered_surf = None
        self.color=pg.Color('gray')

    def perimeter_rect(self):
        rect = self.parent.rect()
        if self.form == self.parent:
            rect.top += self.form.title_height
            rect.height -= self.form.title_height
        return rect

    def mouse_down(self, event):
        super().mouse_down(event)
        if self.rect().collidepoint(event.pos):
            self.dragging = True
            self.last_pos = event.pos

    def mouse_move(self, event):
        super().mouse_move(event)
        if self.dragging and self.perimeter_rect().collidepoint(event.pos):
            offset_x, offset_y = event.pos[0] - self.last_pos[0], event.pos[1] - self.last_pos[1]
            if self.perimeter_rect().left > self.rect().left + offset_x or \
                    self.rect().right + offset_x > self.perimeter_rect().right:
                offset_x=0
            if self.perimeter_rect().top > self.rect().top + offset_y or \
                    self.rect().bottom + offset_y > self.perimeter_rect().bottom:
                offset_y=0
            self.last_pos = event.pos
            self.dragged(offset_x, offset_y)

    def mouse_up(self, event):
        super().mouse_up(event)
        self.dragging = False

    def render(self):
        if not self.covered_surf:
            self.covered_surf = self.form.screen.subsurface(self.rect()).copy()
        pg.draw.rect(self.form.screen, self.color, self.rect())

    def dragged(self, offset_x, offset_y):
        self.form.screen.blit(self.covered_surf, (self.rect().left, self.rect().top))
        self.left += offset_x
        self.top += offset_y
        self.covered_surf = self.form.screen.subsurface(self.rect()).copy()
        self.render()


class Label(Control):
    def __init__(self, form=None, left=0, top=0, width=0, height=0, text=""):
        super().__init__(form=form, left=left, top=top, width=width, height=height)
        self.text = text.replace("\r\n", "\n")
        self.color = pg.Color('black')
        self.background = pg.Color('white')
        self.surface = None

    def render(self):
        if self.form is not None:
            self.form.screen.set_clip(self.rect())
            render_text_pos(screen=self.form.screen, font=self.font, text=self.text, color=self.color,
                            pos=(self.rect().left, self.rect().top))
            self.form.screen.set_clip(None)


class Button(Label):
    def __init__(self, form=None, left=0, top=0, width=0, height=0, text=""):
        super().__init__(form=form, left=left, top=top, width=width, height=height, text=text)
        self.background = pg.Color('gray')

    def render(self, down=False):
        if self.form is not None:
            rect = self.rect()
            if not down:
                pg.draw.rect(self.form.screen, self.background, rect)
            else:
                pg.draw.rect(self.form.screen, pg.Color('white'), rect)
            render_text_rect(screen=self.form.screen, font=self.font, text=self.text, color=self.color, rect=rect)
            pg.draw.rect(self.form.screen, pg.Color('black'), rect, 1)

    def mouse_down(self, event):
        super().mouse_down(event)
        if self.rect().collidepoint(event.pos):
            self.render(down=True)

    def mouse_up(self, event):
        super().mouse_up(event)
        self.render()

    def mouse_click(self, event):
        print("button clicked")


class ScrollBarHandle(Draggable):
    def __init__(self, form=None, parent=None, left=0, top=0, handle_width=10, handle_size=10, orientation=0, max=100):
        super().__init__(form=form, parent=parent, left=left, top=top)
        self.handle_size=handle_size
        self.handle_width=handle_width
        self.orientation = orientation
        self.max = max

    def dragged(self, offset_x, offset_y):
        super().dragged(offset_x,offset_y)
        if self.orientation == 0:
            self.parent.scrolled(self.left/self.max)
        else:
            self.parent.scrolled(self.top/self.max)

    def render(self):
        if self.orientation == 0:
            self.width=self.handle_size
            self.height=self.handle_width
        else:
            self.width=self.handle_width
            self.height=self.handle_size

        super().render()

    def set_pos(self,pc):
        if self.orientation == 0:
            if pc==0:
                self.left=0
            elif pc==1:
                self.left=self.max
            else:
                self.left=int(self.max*pc)
        else:
            if pc==0:
                self.top=0
            elif pc==1:
                self.top=self.max
            else:
                self.top=int(self.max*pc)

class ScrollBar(Control):
    def __init__(self, form=None, parent=None, left=0, top=0, width=10, length=100, orientation=0, min=0, max=100,
                 current=0, view_port=10):
        self.bar_width = width
        self.min = min
        self.max = max
        self.current = current
        self.view_port = view_port
        self.length = length

        if orientation == 0:  # 0: Horizontal 1: Vertical
            width = length
            height = self.bar_width
        else:
            width = self.bar_width
            height = length
        super().__init__(form=form, parent=parent, left=left, top=top, width=width, height=height)
        self.handle = ScrollBarHandle(form=form, parent=self, left=0, top=0, handle_width=self.bar_width, handle_size=self.handle_size(),
                                      orientation=orientation, max=self.length - self.handle_size())
        self.add_control(self.handle)

    def handle_size(self):
        if self.view_port >= self.max - self.min:
            return 0
        return int(self.view_port / (self.max - self.min) * self.length)

    def render(self):
        rect_transparent(self.form.screen, (200, 200, 200, 100), self.rect())
        self.handle.handle_size=self.handle_size()
        self.handle.max=self.length-self.handle.handle_size
        self.handle.render()

    def scrolled(self,pc):
        self.parent.scrolled(self,pc)

    def set_pos(self,pc):
        self.handle.set_pos(pc)
        self.render()

class TextBox(Label):
    def __init__(self, form=None, left=0, top=0, width=0, height=0, text="", multilines=False):
        super().__init__(form=form, left=left, top=top, width=width, height=height, text=text)
        self.padding_left = 2
        self.padding_right = 2
        self.padding_top = 1
        self.padding_bottom = 2
        self.caret_row = 0
        self.caret_col = 0
        self.first_visible_col = 0
        self.first_visible_row = 0
        self.multilines = multilines
        self.scrollbar_width = 10
        if self.multilines:
            self.hscrollbar = ScrollBar(form=form, parent=self, left=1, top=self.height - self.scrollbar_width -1,
                                        width=self.scrollbar_width, length=self.width - self.scrollbar_width -2,
                                        orientation=0)
            self.vscrollbar = ScrollBar(form=form, parent=self, left=self.width - self.scrollbar_width -1, top=1,
                                        width=self.scrollbar_width, length=self.height - self.scrollbar_width -2,
                                        orientation=1)
            self.add_control(self.hscrollbar)
            self.add_control(self.vscrollbar)
        else:
            self.hscrollbar = self.vscrollbar = None

    def text_rect(self):
        return pg.Rect(self.rect().left + self.padding_left, self.rect().top + self.padding_top,
                       self.rect().width - self.padding_left - self.padding_right,
                       self.rect().height - self.padding_top - self.padding_bottom)

    def get_lines(self):
        return self.text.split("\n")

    def visible_rows(self):
        return (self.height - self.padding_top - self.padding_bottom) // self.font.get_linesize()

    def caret_x(self):
        text = self.text[self.first_visible_col:self.caret_col]
        x = self.padding_left
        for (minx, maxx, miny, maxy, advance) in self.font.metrics(text):
            x += advance
        return x

    def get_caret_pos(self):
        lines = self.get_lines()
        pos = 0
        for i in range(self.caret_row):
            pos += len(lines[i]) + 1
        pos += self.caret_col
        return pos

    def draw_caret(self):
        rect = self.form.screen.get_clip()
        self.form.screen.set_clip(self.rect())
        pg.draw.line(self.form.screen, pg.Color('black'), (self.rect().left + self.caret_x(),
                                                           self.rect().top + self.padding_top + self.font.get_linesize() * (
                                                                       self.caret_row - self.first_visible_row)),
                     (self.rect().left + self.caret_x(),
                      self.rect().top + self.padding_top + self.font.get_linesize() * (
                                  self.caret_row - self.first_visible_row + 1)))
        self.form.screen.set_clip(rect)

    def draw_scrollbars(self):
        '''
        rect_transparent(self.form.screen,(200,200,200,100),
                     pg.Rect(self.rect().left+self.width-self.scrollbar_width,self.rect().top,
                             self.scrollbar_width,self.height))
        rect_transparent(self.form.screen, (200,200,200,100),
                     pg.Rect(self.rect().left, self.rect().top+self.height-self.scrollbar_width,
                             self.width , self.scrollbar_width))
        '''
        if self.hscrollbar:
            line_max=0
            for line in self.get_lines():
                if line_max<self.font.size(line)[0]:
                    line_max=self.font.size(line)[0]
            self.hscrollbar.max=line_max
            self.hscrollbar.view_port=self.width
            self.hscrollbar.render()
        if self.vscrollbar:
            self.vscrollbar.view_port=self.visible_rows()
            self.vscrollbar.max=len(self.get_lines())
            self.vscrollbar.render()

    def longest_line(self):
        longest_line = ""
        max_width = 0
        for line in self.get_lines():
            if max_width < self.font.size(line)[0]:
                max_width = self.font.size(line)[0]
                longest_line = line
        return longest_line,max_width

    def scrolled(self,scrollbar,pc):
        if scrollbar==self.vscrollbar:
            if pc==0:
                self.first_visible_row=0
            elif pc==1:
                self.first_visible_row=len(self.get_lines()) - self.visible_rows()
            else:
                self.first_visible_row = int((len(self.get_lines()) - self.visible_rows()) * pc)
        else:
            if pc==0:
                self.first_visible_col=0
            else:
                longest_line,max_width=self.longest_line()
                i=0
                while self.font.size(longest_line[:i])[0]/(max_width-(self.width-self.padding_left-self.padding_right-self.scrollbar_width))<pc:
                    i+=1
                self.first_visible_col=i

        self.render()


    def render(self):
        if self.form is not None:
            pg.draw.rect(self.form.screen, self.background, self.rect())
            self.form.screen.set_clip(self.text_rect())
            lines = self.get_lines()
            for i in range(self.first_visible_row, min(self.first_visible_row + self.visible_rows() + 1, len(lines))):
                pos = (
                    self.rect().left + self.padding_left,
                    self.rect().top + self.padding_top + (i - self.first_visible_row) * self.font.get_linesize())
                render_text_pos(screen=self.form.screen, font=self.font, text=lines[i][self.first_visible_col:],
                                color=self.color, pos=pos)
            self.form.screen.set_clip(None)
            if self.focused:
                self.draw_caret()
            if self.multilines and self.mouse_over:
                self.draw_scrollbars()
            pg.draw.rect(self.form.screen, pg.Color("black"), self.rect(), 1)

    def move_caret(self, pos):
        caret_col = self.first_visible_col
        left = self.rect().left + self.padding_left
        for (minx, maxx, miny, maxy, advance) in self.font.metrics(self.text[self.first_visible_col:]):
            left += advance
            if left >= pos[0]:
                break
            caret_col += 1
        caret_row = (pos[1] - self.rect().top - self.padding_top) // self.font.get_linesize() + self.first_visible_row

        self.set_caret(caret_row, caret_col)

    def set_caret_pos(self, pos):
        pos = min(max(pos, 0), len(self.text) - 1)
        row, col, idx = 0, 0, 0
        text = ""
        while True:
            if len(text + self.get_lines()[row]) < pos:
                text += self.get_lines()[row]+"\n"
                row += 1
                continue
            else:
                col = pos - len(text)
                break
        self.set_caret(row, col)

    def set_caret(self, caret_row, caret_col):
        self.caret_row = min(max(caret_row, 0), len(self.get_lines()) - 1)
        self.caret_col = min(max(caret_col, 0), len(self.get_lines()[self.caret_row]))
        while self.caret_x() > self.width - self.padding_right:
            self.first_visible_col += 1
        while self.first_visible_col > 0 and self.caret_col - 1 < self.first_visible_col:
            self.first_visible_col -= 1
        while self.first_visible_row > self.caret_row:
            self.first_visible_row -= 1
        while self.first_visible_row + self.visible_rows() - 1 < self.caret_row:
            self.first_visible_row += 1
        if self.multilines:
            self.vscrollbar.set_pos(self.first_visible_row/(len(self.get_lines())-self.visible_rows()))
            longest_line,max_width=self.longest_line()
            self.hscrollbar.set_pos(self.font.size(longest_line[:self.first_visible_col])[0]/(max_width-(self.width-self.padding_left-self.padding_right-self.scrollbar_width)))
        self.render()

    def mouse_down(self, event):
        if self.rect().collidepoint(event.pos):
            if not self.multilines:
                self.move_caret(event.pos)
            elif not self.vscrollbar.rect().collidepoint(event.pos) and not self.hscrollbar.rect().collidepoint(event.pos):
                self.move_caret(event.pos)
        super().mouse_down(event)
        self.render()

    def mouse_in(self, event):
        super().mouse_in(event)
        self.render()

    def mouse_out(self, event):
        super().mouse_out(event)
        self.render()

    def on_key_down(self, event):
        return True

    def key_down(self, event):
        if not self.on_key_down(event):
            return
        if event.key == pg.K_BACKSPACE and self.get_caret_pos() > 0:
            pre_pos=self.get_caret_pos()
            self.text = self.text[0:self.get_caret_pos() - 1] + self.text[self.get_caret_pos():]
            self.set_caret_pos(pre_pos - 1)
        elif event.key == pg.K_DELETE and self.get_caret_pos() < len(self.text):
            self.text = self.text[0:self.get_caret_pos()] + self.text[self.get_caret_pos() + 1:]
        elif event.key == pg.K_LEFT and self.caret_col > 0:
            self.set_caret(self.caret_row, self.caret_col - 1)
        elif event.key == pg.K_RIGHT and self.get_caret_pos() < len(self.text):
            self.set_caret(self.caret_row, self.caret_col + 1)
        elif event.key == pg.K_HOME:
            self.set_caret(self.caret_row, 0)
        elif event.key == pg.K_END:
            self.set_caret(self.caret_row, len(self.get_lines()[self.caret_row]))
        elif event.key == pg.K_UP:
            self.set_caret(self.caret_row - 1, self.caret_col)
        elif event.key == pg.K_DOWN:
            self.set_caret(self.caret_row + 1, self.caret_col)
        elif event.key == pg.K_PAGEUP:
            self.set_caret(self.caret_row - self.visible_rows(), self.caret_col)
        elif event.key == pg.K_PAGEDOWN:
            self.set_caret(self.caret_row + self.visible_rows(), self.caret_col)
        elif event.key == pg.K_RETURN and self.multilines:
            self.text = self.text[0:self.get_caret_pos()] + "\n" + self.text[self.get_caret_pos():]
            self.set_caret(self.caret_row + 1, 0)
        elif event.unicode and 32 <= ord(event.unicode) <= 126:
            self.text = self.text[0:self.get_caret_pos()] + event.unicode + self.text[self.get_caret_pos():]
            self.set_caret(self.caret_row, self.caret_col + 1)
        self.render()


class CheckBox(Control):
    def __init__(self, form=None, left=0, top=0):
        super().__init__(form=form, left=left, top=top)
        self.checked = False
        self.width = 20
        self.height = 20

    def mouse_click(self, event):
        self.checked = not self.checked
        self.render()

    def render(self):
        pg.draw.rect(self.form.screen, pg.Color('white'), self.rect(), 0)
        pg.draw.rect(self.form.screen, pg.Color('black'), self.rect(), 1)
        if self.checked:
            pg.draw.line(self.form.screen, pg.Color('black'), (self.rect().left, self.rect().top),
                         (self.rect().left + self.rect().width - 1, self.rect().top + self.rect().height - 1), 1)
            pg.draw.line(self.form.screen, pg.Color('black'),
                         (self.rect().left, self.rect().top + self.rect().height - 1),
                         (self.rect().left + self.rect().width - 1, self.rect().top), 1)


class RadioButton(Control):
    def __init__(self, form=None, left=0, top=0, group_id='default'):
        super().__init__(form=form, left=left, top=top)
        self.checked = False
        self.width = 20
        self.height = 20
        self.group_id = group_id

    def mouse_click(self, event):
        self.checked = True
        for control in self.form.controls:
            if control != self and isinstance(control,
                                              RadioButton) and control.checked and control.group_id == self.group_id:
                control.checked = False
                control.render()
        self.render()

    def render(self):
        pg.gfxdraw.filled_circle(self.form.screen, self.rect().left + self.width // 2,
                                 self.rect().top + self.height // 2, 10, pg.Color('white'))
        pg.gfxdraw.circle(self.form.screen, self.rect().left + self.width // 2,
                          self.rect().top + self.height // 2, 10, pg.Color('black'))
        if self.checked:
            pg.gfxdraw.circle(self.form.screen, self.rect().left + self.width // 2,
                              self.rect().top + self.height // 2, 5, pg.Color('black'))
            pg.gfxdraw.filled_circle(self.form.screen, self.rect().left + self.width // 2,
                                     self.rect().top + self.height // 2, 5, pg.Color('black'))


class PyForm(Control):
    title_height = 20
    title_color = pg.Color('lightgray')

    def __init__(self, screen, left=0, top=0, width=0, height=0, title=""):
        super().__init__(form=None, left=left, top=top, width=width, height=height)
        self.screen = screen
        self.covered_screen = None
        self.visible = False
        self.dragging = False
        self.dragging_pos = None
        self.title = title
        self.set_font('Courier', 18)

    def add_control(self, control):
        self.controls.append(control)
        control.form = self

    def x_rect(self):
        return pg.Rect(self.left + self.width - self.title_height, self.top, self.title_height, self.title_height)

    def handle_rect(self):
        return pg.Rect(self.left, self.top, self.width - self.title_height, self.title_height)

    def title_rect(self):
        return pg.Rect(self.left, self.top, self.width, self.title_height)

    def draw_x(self, color=pg.Color('black'), bgcolor=None):
        if bgcolor is None:
            bgcolor = self.title_color
        pg.draw.rect(self.screen, bgcolor, self.x_rect())
        pg.draw.line(self.screen, color, (self.x_rect().left + 4, self.x_rect().top + 4),
                     (self.x_rect().left + self.x_rect().width - 4, self.x_rect().top + self.x_rect().height - 4), 1)
        pg.draw.line(self.screen, color, (self.x_rect().left + 4, self.x_rect().top + self.x_rect().height - 4),
                     (self.x_rect().left + self.x_rect().width - 4, self.x_rect().top + 4), 1)

    def draw_title(self):
        pg.draw.rect(self.screen, self.title_color, self.title_rect(), 0)
        render_text_rect(self.screen, self.title, self.font, self.title_rect(), pg.Color('black'))

    def draw_background(self):
        pg.draw.rect(self.screen, pg.Color('white'),
                     pg.Rect(self.left, self.top + self.title_height, self.width, self.height - self.title_height), 0)

    def draw_controls(self):
        for control in self.controls:
            control.render()

    def render(self):
        if self.covered_screen is None:
            self.covered_screen = self.screen.copy()
        else:
            self.screen.blit(self.covered_screen, (0, 0))
        self.draw_title()
        self.draw_x()
        self.draw_background()
        self.draw_controls()
        pg.display.flip()

    def close(self):
        if self.covered_screen is not None:
            self.screen.blit(self.covered_screen, (0, 0))
        pg.display.flip()
        self.visible = False

    def open(self):
        self.render()
        self.visible = True

    def open_modal(self):
        self.open()
        while self.visible:
            if pg.event.peek(pg.QUIT):
                self.close()
                break;
            for event in pg.event.get():
                self.handle_event(event)

    def drag_to(self, pos):
        (x0, y0) = self.dragging_pos
        (x, y) = pos
        self.left += x - x0
        self.top += y - y0
        self.dragging_pos = pos
        self.render()

    def mouse_move(self, event):
        if self.dragging:
            self.drag_to(event.pos)
            return
        (x, y) = event.pos
        if self.x_rect().collidepoint(x, y):
            self.draw_x(pg.Color('white'), pg.Color('red'))
        else:
            self.draw_x()

    def mouse_up(self, event):
        if self.handle_rect().collidepoint(event.pos) and self.dragging:
            self.dragging = False
            return
        (x, y) = event.pos
        if self.x_rect().collidepoint(x, y):
            self.close()
            return

    def mouse_down(self, event):
        if self.handle_rect().collidepoint(event.pos):
            self.dragging = True
            self.dragging_pos = event.pos
            return

    def handle_event(self, event):
        super().handle_event(event)
        pg.display.flip()

class MenuItem(Control):
    def __init__(self,text=""):
        super().__init__()
        self.active=False
        self.text=text
        self.menu=None
        self.padding_left=5
        self.padding_right=5
        self.on_mouse_click=None

    def mouse_click(self, event):
        if self.rect().collidepoint(event.pos):
            for item in self.parent.controls:
                item.active=False
            self.active=True
            if callable(self.on_mouse_click):
                self.on_mouse_click(event)

    def render(self):
        if self.menu:
            font=self.menu.font
            self.left=0
            for i in range(self.menu.controls.index(self)):
                item=self.menu.controls[i]
                self.left+=font.size(item.text)[0]+item.padding_left+item.padding_right
            self.width=font.size(self.text)[0]+self.padding_left+self.padding_right
            self.height=font.get_linesize()
            if self.active and self.parent.mouse_over:
                color = pg.Color('white')
                background = pg.Color('blue')
            elif self.mouse_over or self.active:
                color = pg.Color('black')
                background = pg.Color('lightgray')
            else:
                color=pg.Color('black')
                background=pg.Color('white')
            pg.draw.rect(self.menu.screen,background,self.rect())
            render_text_rect(screen=self.menu.screen,text=self.text,font=self.parent.font,rect=self.rect(),color=color,background=background)

class Menu(Control):
    def __init__(self,form=None,screen=None):
        super().__init__()
        if form is not None:
            self.parent=form
            self.screen=form.screen
            self.width=form.width
        elif screen is not None:
            self.parent=None
            self.screen=screen
            self.width=screen.get_width()

    def add_item(self,text):
        item=MenuItem(text)
        item.menu=self
        self.add_control(item)

    def render(self):
        self.height=self.font.get_linesize()
        pg.draw.rect(self.screen,pg.Color('white'),self.rect())
        for item in self.controls:
            item.render()

    def mouse_click(self, event):
        for item in self.controls:
            item.active=False
        super().mouse_click(event)

    def handle_event(self, event):
        super().handle_event(event)
        self.render()
        pg.display.flip()


if __name__ == "__main__":
    pg.init()
    pg.font.init()
    screen = pg.display.set_mode((400, 400))
    pg.key.set_repeat(500, 100)
    form1 = PyForm(screen, 10, 30, 300, 200, title="Form1")
    form1.add_control(Button(form=form1, width=100, height=20, left=20, top=10, text="ABCgyl"))
    form1.add_control(Label(form=form1, width=100, height=20, top=50, left=20, text="ABCgyl"))
    form1.add_control(
        TextBox(form=form1, width=100, height=53, top=80, left=20, text="ABCgyl\r\n1234\r\nasdfas\r\nasdfsadf",
                multilines=True))
    form1.add_control(CheckBox(form=form1, top=150, left=20))
    form1.add_control(RadioButton(form=form1, top=150, left=50))
    form1.add_control(RadioButton(form=form1, top=150, left=100))
    form1.add_control(Draggable(form=form1, top=150, left=200, width=20, height=20))

    menu=Menu(screen=screen)
    menu.add_item("item1")
    menu.add_item("item2")
    menu.add_item("item3")

    menu.render()

    form1.open_modal()

    running = True
    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            elif form1.visible:
                form1.handle_event(e)
            menu.handle_event(e)
