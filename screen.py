from pygame import Surface
from elements import BaseElement
from typing import List, Optional
from pygame.event import Event
from pygame.rect import Rect


class Screen:
    def __init__(self) -> None:
        self.elements: List[BaseElement] = []
        self.active_element: Optional[BaseElement] = None

    def add_element(self, el: BaseElement):
        self.elements.append(el)

    def handle_mouseclick(self, event: Event):
        # 1. Find the element which overlaps with the coords of the event
        for el in self.elements:
            # TODO: !! Add size property to the base element
            el_rect = Rect(el.pos, el.size)
            if el_rect.collidepoint(event.pos):
                # 2. Make the element active
                self.active_element = el
                # 3. Call the click handler of the element
                el.handle_mouseclick(event)

    def handle_keyboard(self, event: Event):
        # 1. Find the active element if it is present
        # 2. Call the keyboard handler of the element
        if self.active_element is not None:
            self.active_element.handle_keyboard(event)

    def draw(self, screen: Surface) -> None:
        for element in self.elements:
            is_active = element is self.active_element
            element.draw(screen, is_active)
