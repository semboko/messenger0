import pygame
from pygame import Vector2
from pygame import Surface
from string import printable
from pygame.font import Font
from pygame.draw import rect
from pygame.rect import Rect
from pygame.event import Event
from storage import local_storage
from typing import Callable, List


class BaseElement:
    def __init__(self, pos: Vector2, size: Vector2) -> None:
        self.pos = pos
        self.size = size

    def get_rect(self) -> Rect:
        return Rect(self.pos, self.size)

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
        self.hints_font = Font("Quicksand-Regular.ttf", 15)

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

    def draw_hints(self, screen: Surface, hints: List[str], is_active: bool) -> None:
        if not is_active:
            return
        hints_rect = Rect(
            self.pos + Vector2(10, self.size.y),
            Vector2(self.size.x - 20, 100)
        )
        pygame.draw.rect(screen, (150, 150, 150), hints_rect)


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


class ContactItem(BaseElement):
    def __init__(self, pos: Vector2, txt: str) -> None:
        self.font = Font("Quicksand-Regular.ttf", 18)
        self.contact_img = self.font.render(txt, True, (0, 0, 0))

        super().__init__(pos, Vector2(self.contact_img.get_size()))

    def draw(self, screen: Surface, is_active: bool = False) -> None:
        screen.blit(self.contact_img, self.pos)


class Contacts(BaseElement):
    def __init__(self, pos: Vector2, hidden_size: Vector2, shown_size: Vector2) -> None:
        super().__init__(pos, hidden_size)
        self.hidden_size = hidden_size
        self.shown_size = shown_size
        self.hidden = True
        self.title_font = Font("Quicksand-Regular.ttf", 20)
        self.title_img = self.title_font.render("Contacts", True, (0, 0, 0))
        self.close_btn = Button(self.pos + Vector2(10, 10), Vector2(20, 20), "X", print)
        self.contact_items = self.create_contact_items()

        self.search_input = TextInput(
            self.pos + Vector2(10, 50),
            Vector2(self.shown_size.x - 20, 40),
            "Search",
            "search_input",
        )
        self.search_is_active = False

    def create_contact_items(self):
        result = []
        pos = self.pos + Vector2(10, 100 + self.title_img.get_height() + 20)
        for contact in local_storage["contacts"]:
            item = ContactItem(pos.copy(), contact)
            result.append(item)
            pos += Vector2(0, item.contact_img.get_height() + 5)
        return result

    def handle_mouseclick(self, event: Event) -> None:
        if self.hidden:
            self.size = self.shown_size
            self.hidden = False
            return

        if self.close_btn.get_rect().collidepoint(event.pos):
            self.hidden = True
            self.size = self.hidden_size
            self.search_is_active = False

        if self.search_input.get_rect().collidepoint(event.pos):
            self.search_is_active = True
            return

        self.search_is_active = False

    def handle_keyboard(self, event: Event) -> None:
        self.search_input.handle_keyboard(event)

    def draw(self, screen: Surface, is_active: bool = False):
        outline = Rect(self.pos, self.size)
        width = 1 if self.hidden else 0
        rect(screen, (200, 200, 200), outline, width, 5)
        title_pos = Vector2(10, 2) if self.hidden else Vector2(10, 100)
        screen.blit(self.title_img, self.pos + title_pos)

        if not self.hidden:
            # Draw close button
            self.close_btn.draw(screen)

            # Draw list of contacts
            for item in self.contact_items:
                item.draw(screen)

            # Draw search input
            self.search_input.draw(screen, self.search_is_active)
            self.search_input.draw_hints(screen, local_storage["contact_hints"], self.search_is_active)
