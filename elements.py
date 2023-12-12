import pygame
from pygame import Vector2
from pygame import Surface
from string import printable
from pygame.font import Font
from pygame.draw import rect
from pygame.rect import Rect
from pygame.event import Event
from storage import local_storage
from typing import Callable


class BaseElement:
    def __init__(self, pos: Vector2, size: Vector2) -> None:
        self.pos = pos
        self.size = size

    def handle_mouseclick(self, event: Event) -> None:
        print(f"Element {id(self)} was clicked")

    def handle_keyboard(self, event: Event) -> None:
        print(id(self), event.unicode)

    def draw(self, screen: Surface, is_active: bool = False):
        raise NotImplementedError()


class TextInput(BaseElement):
    def __init__(self, pos: Vector2, size: Vector2, label: str, storage_key: str) -> None:
        super().__init__(pos, size)
        self.storage_key = storage_key
        local_storage[self.storage_key] = ""
        self.label = label

        label_font = Font("Quicksand-Regular.ttf", 14)
        self.label_surface = label_font.render(self.label, True, (150, 150, 150), (255, 255, 255))

        self.txt_font = Font("Quicksand-Regular.ttf", 25)

    def handle_mouseclick(self, event: Event) -> None:
        print(f"input {id(self)} was clicked")

    def handle_keyboard(self, event: Event) -> None:
        if event.key == pygame.K_BACKSPACE:
            local_storage[self.storage_key] = local_storage[self.storage_key][0:-1]
            return
        if event.key == pygame.K_RETURN:
            local_storage.send_message()
            return
        if event.unicode in printable:
            local_storage[self.storage_key] += event.unicode

    def draw(self, screen: Surface, is_active: bool = False) -> None:
        outline = Rect(self.pos, self.size)
        rect(screen, (150, 150, 150), outline, 1, 5)
        screen.blit(self.label_surface, self.pos + Vector2(10, -self.label_surface.get_height()/2))

        input_value = local_storage[self.storage_key]
        if is_active:
            input_value += "|"
        txt_surface = self.txt_font.render(input_value, True, (50, 50, 50))
        screen.blit(txt_surface, self.pos + Vector2(10, self.size.y/2 - txt_surface.get_height()/2))


class Button(BaseElement):
    def __init__(self, pos: Vector2, size: Vector2, txt: str, click_callback: Callable) -> None:
        super().__init__(pos, size)
        font = Font("Quicksand-Regular.ttf", 25)
        self.txt_image = font.render(txt, True, (0, 0, 0))
        self.clicked = click_callback

    def handle_mouseclick(self, event: Event) -> None:
        self.clicked()

    def draw(self, screen: Surface, is_active: bool = False):
        outline = Rect(self.pos, self.size)
        rect(screen, (150, 150, 150), outline, 1, 5)
        txt_x, txt_y = self.txt_image.get_size()
        screen.blit(
            self.txt_image,
            self.pos + Vector2(
                self.size.x/2 - txt_x/2,
                self.size.y/2 - txt_y/2
            )
        )


class ScreenTitle(BaseElement):
    def __init__(self, pos: Vector2, txt: str) -> None:
        self.txt = txt
        font = Font("Quicksand-Regular.ttf", 48)
        self.txt_surface = font.render(self.txt, True, (0, 0, 0))
        self.delta = Vector2(self.txt_surface.get_width()/2, 0)

        super().__init__(pos, Vector2(self.txt_surface.get_size()))

    def handle_mouseclick(self, event: Event) -> None:
        return

    def draw(self, screen: Surface, is_active: bool = False):
        screen.blit(self.txt_surface, self.pos - self.delta)


class MessagesList(BaseElement):
    def __init__(self, pos: Vector2, size: Vector2) -> None:
        super().__init__(pos, size)
        self.author_font = Font("Quicksand-Regular.ttf", 12)
        self.msg_font = Font("Quicksand-Regular.ttf", 11)
        self.dt_font = Font("Quicksand-Regular.ttf", 10)

    def draw(self, screen: Surface, is_active: bool = False):
        lowest_y = self.pos.y + self.size.y
        messages = local_storage["messages"]
        if len(messages) == 0:
            return

        for author, txt, dt in reversed(messages):
            author_img = self.author_font.render(author, True, (227, 0, 102))
            txt_img = self.msg_font.render(txt, True, (0, 0, 0))
            dt_img = self.dt_font.render(dt, True, (80, 80, 80))

            msg_hight = author_img.get_height() + txt_img.get_height() + 10

            msg_surface = Surface((self.size.x, msg_hight))
            msg_surface.fill((255, 255, 255))
            msg_surface.blit(author_img, (0, 0))
            msg_surface.blit(txt_img, (0, author_img.get_height() + 10))
            msg_surface.blit(dt_img, (self.size.x - dt_img.get_width(), 0))

            screen.blit(msg_surface, (self.pos.x, lowest_y - msg_surface.get_height()))

            lowest_y -= msg_surface.get_height() + 10


class Contacts(BaseElement):
    def __init__(self, pos: Vector2, hidden_size: Vector2, shown_size: Vector2) -> None:
        super().__init__(pos, hidden_size)
        self.hidden_size = hidden_size
        self.shown_size = shown_size
        self.hidden = True
        self.title_font = Font("Quicksand-Regular.ttf", 20)
        self.title_img = self.title_font.render("Contacts", True, (0, 0, 0))

    def handle_mouseclick(self, event: Event) -> None:
        if self.hidden:
            self.size = self.shown_size
            self.hidden = False
            return

        self.hidden = True
        self.size = self.hidden_size

    def draw(self, screen: Surface, is_active: bool = False):
        outline = Rect(self.pos, self.size)
        width = 1 if self.hidden else 0
        rect(screen, (150, 150, 150), outline, width, 5)
        title_pos = Vector2(10, 2) if self.hidden else Vector2(10, 60)
        screen.blit(self.title_img, self.pos + title_pos)
