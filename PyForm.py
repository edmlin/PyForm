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


class Control:
    def __init__(self, form=None, left=0, top=0, width=0, height=0):
        self.form = form
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.mouse_over = False
        self.focused = False
        self.font_name = None
        self.font_size = None
        self.set_font('Courier', 18)

    def rect(self):
        if self.form is not None:
            return pg.Rect(self.left + self.form.left, self.top + self.form.top + self.form.title_height, self.width,
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
        pass

    def key_up(self, event):
        pass

    def key_press(self, event):
        pass


class Label(Control):
    def __init__(self, form=None, left=0, top=0, width=0, height=0, text=""):
        super().__init__(form, left, top, width, height)
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
        super().__init__(form, left, top, width, height, text)
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


class TextBox(Label):
    def __init__(self, form=None, left=0, top=0, width=0, height=0, text="", multilines=False):
        super().__init__(form, left, top, width, height, text)
        self.padding_left = 2
        self.padding_top = 1
        self.caret_row = 0
        self.caret_col = 0
        self.first_visible_col = 0
        self.first_visible_row = 0
        self.multilines = multilines
        self.current_line = 0

    def get_lines(self):
        return self.text.split("\n")

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
                                                           self.rect().top + self.padding_top + self.font.get_linesize() * self.caret_row),
                     (self.rect().left + self.caret_x(),
                      self.rect().top + self.padding_top + self.font.get_linesize() * (self.caret_row + 1)))
        self.form.screen.set_clip(rect)

    def render(self):
        if self.form is not None:
            self.form.screen.set_clip(self.rect())
            pg.draw.rect(self.form.screen, self.background, self.rect())
            lines = self.get_lines()
            for i in range(self.first_visible_row,len(lines)):
                pos = (
                self.rect().left + self.padding_left, self.rect().top + self.padding_top + (i-self.first_visible_row) * self.font.get_linesize())
                render_text_pos(screen=self.form.screen, font=self.font, text=lines[i][self.first_visible_col:],
                                color=self.color, pos=pos)
            pg.draw.rect(self.form.screen, pg.Color("black"), self.rect(), 1)
            if self.focused:
                self.draw_caret()
            self.form.screen.set_clip(None)

    def move_caret(self, pos):
        caret_col = self.first_visible_col
        left = self.rect().left + self.padding_left
        for (minx, maxx, miny, maxy, advance) in self.font.metrics(self.text[self.first_visible_col:]):
            left += advance
            if left >= pos[0]:
                break
            caret_col += 1
        caret_row = (pos[1] - self.rect().top) // self.font.get_linesize()

        self.set_caret(caret_row, caret_col)

    def set_caret(self, caret_row, caret_col):
        if caret_row < 0:
            self.caret_row = 0
        elif caret_row > len(self.get_lines()) - 1:
            self.caret_row = len(self.get_lines()) - 1
        else:
            self.caret_row = caret_row
        if caret_col < 0:
            self.caret_col = 0
        elif caret_col > len(self.get_lines()[self.caret_row]):
            self.caret_col = len(self.get_lines()[self.caret_row])
        else:
            self.caret_col = caret_col
        while self.caret_x() > self.width - 2 and self.first_visible_col < len(self.text) - 1:
            self.first_visible_col += 1
        while self.first_visible_col > 0 and self.caret_col - 1 < self.first_visible_col:
            self.first_visible_col -= 1
        while self.first_visible_row > self.caret_row:
            self.first_visible_row -= 1
        while self.first_visible_row + self.height // self.font.get_linesize() < self.caret_row:
            self.first_visible_row += 1
        self.render()

    def mouse_down(self, event):
        super().mouse_down(event)
        if self.focused:
            self.move_caret(event.pos)
        else:
            self.render()

    def on_key_down(self, event):
        return True

    def key_down(self, event):
        if not self.on_key_down(event):
            return
        if event.key == pg.K_BACKSPACE and self.get_caret_pos() > 0:
            self.text = self.text[0:self.get_caret_pos() - 1] + self.text[self.get_caret_pos():]
            self.set_caret(self.caret_row, self.caret_col - 1)
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
        elif event.key == pg.K_RETURN:
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
        self.screen = screen
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.controls = []
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
        for control in self.controls:
            if control.rect().collidepoint(event.pos) or control.mouse_over:
                control.mouse_move(event)

    def mouse_up(self, event):
        if self.handle_rect().collidepoint(event.pos) and self.dragging:
            self.dragging = False
            return
        (x, y) = event.pos
        if self.x_rect().collidepoint(x, y):
            self.close()
            return
        for control in self.controls:
            if control.rect().collidepoint(x, y) or control.focused:
                control.mouse_up(event)

    def mouse_down(self, event):
        if self.handle_rect().collidepoint(event.pos):
            self.dragging = True
            self.dragging_pos = event.pos
            return
        (x, y) = event.pos
        for control in self.controls:
            if control.rect().collidepoint(x, y) or control.focused:
                control.mouse_down(event)

    def key_down(self, event):
        for control in self.controls:
            if control.focused:
                control.key_down(event)

    def key_up(self, event):
        for control in self.controls:
            if control.focused:
                control.key_up(event)

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
        pg.display.flip()


if __name__ == "__main__":
    pg.init()
    pg.font.init()
    screen = pg.display.set_mode((400, 400))
    pg.key.set_repeat(500, 100)
    form1 = PyForm(screen, 10, 10, 300, 200, title="Form1")
    form1.add_control(Button(width=100, height=20, left=20, top=10, text="ABCgyl"))
    form1.add_control(Label(width=100, height=20, top=50, left=20, text="ABCgyl"))
    form1.add_control(TextBox(width=100, height=60, top=100, left=20, text="ABCgyl\r\n1234", multilines=False))
    form1.add_control(CheckBox(top=150, left=20))
    form1.add_control(RadioButton(top=150, left=50))
    form1.add_control(RadioButton(top=150, left=100))

    form1.open()
    running = True
    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            elif form1.visible:
                form1.handle_event(e)
