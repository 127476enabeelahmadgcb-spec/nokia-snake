from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.core.window import Window
from kivy.uix.label import Label
import random

CELL = 20
COLS = 20
ROWS = 30

class SnakeGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reset_game()
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        Clock.schedule_interval(self.update, 1.0 / 10)

    def reset_game(self):
        cx, cy = COLS // 2, ROWS // 2
        self.snake = [(cx, cy), (cx-1, cy), (cx-2, cy)]
        self.direction = (1, 0)
        self.next_dir = (1, 0)
        self.score = 0
        self.level = 1
        self.eaten = 0
        self.alive = True
        self.food = self.spawn_food()
        self.touch_start = None

    def spawn_food(self):
        while True:
            pos = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
            if pos not in self.snake:
                return pos

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == "up"    and self.direction != (0,-1): self.next_dir = (0, 1)
        if keycode[1] == "down"  and self.direction != (0, 1): self.next_dir = (0,-1)
        if keycode[1] == "left"  and self.direction != (1, 0): self.next_dir = (-1,0)
        if keycode[1] == "right" and self.direction != (-1,0): self.next_dir = (1, 0)
        if keycode[1] == "enter" and not self.alive: self.reset_game()

    def on_touch_down(self, touch):
        self.touch_start = (touch.x, touch.y)

    def on_touch_up(self, touch):
        if not self.touch_start:
            return
        dx = touch.x - self.touch_start[0]
        dy = touch.y - self.touch_start[1]
        if abs(dx) > abs(dy):
            if dx > 20 and self.direction != (-1,0): self.next_dir = (1, 0)
            if dx < -20 and self.direction != (1, 0): self.next_dir = (-1,0)
        else:
            if dy > 20 and self.direction != (0,-1): self.next_dir = (0, 1)
            if dy < -20 and self.direction != (0, 1): self.next_dir = (0,-1)
        if not self.alive:
            self.reset_game()
        self.touch_start = None

    def update(self, dt):
        if not self.alive:
            return
        speed = max(4, 10 - (self.level - 1))
        Clock.unschedule(self.update)
        Clock.schedule_interval(self.update, 1.0 / speed)
        self.direction = self.next_dir
        hx, hy = self.snake[0]
        nx, ny = hx + self.direction[0], hy + self.direction[1]
        nx %= COLS
        ny %= ROWS
        if (nx, ny) in self.snake:
            self.alive = False
            self.draw_scene()
            return
        self.snake.insert(0, (nx, ny))
        if (nx, ny) == self.food:
            self.score += self.level * 10
            self.eaten += 1
            if self.eaten >= 5:
                self.level += 1
                self.eaten = 0
            self.food = self.spawn_food()
        else:
            self.snake.pop()
        self.draw_scene()

    def draw_scene(self):
        self.canvas.clear()
        W = self.width
        H = self.height
        ox = (W - COLS * CELL) / 2
        oy = (H - ROWS * CELL) / 2 + 40
        with self.canvas:
            Color(0.08, 0.15, 0.08)
            Rectangle(pos=(0,0), size=(W, H))
            Color(0.09, 0.2, 0.09)
            Rectangle(pos=(ox, oy), size=(COLS*CELL, ROWS*CELL))
            Color(0.12, 0.22, 0.12)
            for i in range(COLS+1):
                Line(points=[ox+i*CELL, oy, ox+i*CELL, oy+ROWS*CELL], width=0.5)
            for i in range(ROWS+1):
                Line(points=[ox, oy+i*CELL, ox+COLS*CELL, oy+i*CELL], width=0.5)
            fx, fy = self.food
            Color(1, 0.3, 0.2)
            Ellipse(pos=(ox+fx*CELL+2, oy+fy*CELL+2), size=(CELL-4, CELL-4))
            Color(1, 0.7, 0.5, 0.4)
            Ellipse(pos=(ox+fx*CELL-1, oy+fy*CELL-1), size=(CELL+2, CELL+2))
            for i, (gx, gy) in enumerate(self.snake):
                if i == 0:
                    Color(0.4, 0.9, 0.4)
                else:
                    t = 1 - (i / len(self.snake)) * 0.4
                    Color(0.2*t, 0.65*t, 0.2*t)
                Rectangle(pos=(ox+gx*CELL+2, oy+gy*CELL+2), size=(CELL-4, CELL-4))
            Color(0.05, 0.1, 0.05)
            Rectangle(pos=(0, H-50), size=(W, 50))
        self.clear_widgets()
        self.add_widget(Label(
            text="SCORE: " + str(self.score),
            font_size=18, bold=True,
            color=(0.5, 1, 0.5, 1),
            pos=(ox, H-45),
            size=(150, 40)
        ))
        self.add_widget(Label(
            text="LEVEL: " + str(self.level),
            font_size=18, bold=True,
            color=(1, 0.9, 0.2, 1),
            pos=(W-150, H-45),
            size=(150, 40)
        ))
        if not self.alive:
            with self.canvas:
                Color(0, 0, 0, 0.6)
                Rectangle(pos=(ox, oy + ROWS*CELL//2 - 40),
                          size=(COLS*CELL, 80))
            self.add_widget(Label(
                text="GAME OVER - Swipe to restart",
                font_size=16, bold=True,
                color=(1, 1, 0.3, 1),
                halign="center",
                pos=(ox, oy + ROWS*CELL//2 - 40),
                size=(COLS*CELL, 80)
            ))

    def on_size(self, *args):
        self.draw_scene()


class NokiaSnakeApp(App):
    def build(self):
        Window.clearcolor = (0.08, 0.15, 0.08, 1)
        return SnakeGame()

if __name__ == "__main__":
    NokiaSnakeApp().run()
