from redis import Redis
from threading import Thread
import pygame
from pygame import Vector2
from time import sleep
from typing import List, Optional

from screen import Screen
from elements import ScreenTitle, TextInput, Button, MessagesList
from storage import local_storage


pygame.init()

SCREEN_WIDTH = 600
SCREEN_HEIGH = 800

signup_screen = Screen()
signup_screen.add_element(
    ScreenTitle(Vector2(SCREEN_WIDTH/2, 100), "Sign Up")
)
signup_screen.add_element(
    TextInput(Vector2(SCREEN_WIDTH/2 - 200, 200), Vector2(400, 50), "Login", "login")
)
signup_screen.add_element(
    TextInput(Vector2(SCREEN_WIDTH/2 - 200, 280), Vector2(400, 50), "Password", "password")
)
signup_screen.add_element(
    Button(Vector2(SCREEN_WIDTH/2 - 50, 350), Vector2(100, 50), "Submit", local_storage.signup)
)

main_screen = Screen()
main_screen.add_element(
    ScreenTitle(Vector2(SCREEN_WIDTH/2, 100), "Messenger")
)
main_screen.add_element(
    TextInput(Vector2(20, SCREEN_HEIGH - 70), Vector2(SCREEN_WIDTH - 40, 50), "Type your message...", "current_message")
)
main_screen.add_element(
    Button(Vector2(SCREEN_WIDTH - 125, SCREEN_HEIGH - 65), Vector2(100, 40), "Send", local_storage.send_message)
)
main_screen.add_element(
    MessagesList(Vector2(20, 180), Vector2(SCREEN_WIDTH - 40, 500))
)


class Messenger:
    def __init__(self):
        self._exit = False
        self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGH))
        self.clock = pygame.time.Clock()
        self.redis = Redis(host="178.62.216.119", port=4567, decode_responses=True)
        self.screens: List[Screen] = []
        self.active_screen: Optional[int] = None

    def add_screen(self, screen: Screen, is_active=False):
        self.screens.append(screen)
        if is_active:
            self.active_screen = len(self.screens) - 1

    def launch(self) -> None:
        self.receiver = Thread(target=local_storage.receive_messages, args=(self, ))
        self.receiver.start()

        self.sender = Thread(target=local_storage.message_sender, args=(self, ))
        self.sender.start()

        if self.active_screen is None:
            raise Exception("At least one screen must be active")

        while True:
            if local_storage["is_authorized"]:
                self.active_screen = 1
            active_screen: Screen = self.screens[self.active_screen]
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self._exit = True
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    active_screen.handle_mouseclick(event)

                if event.type == pygame.KEYDOWN:
                    active_screen.handle_keyboard(event)

            self.window.fill((255, 255, 255))
            s = self.screens[self.active_screen]
            s.draw(self.window)
            pygame.display.update()
            self.clock.tick(60)


m = Messenger()
m.add_screen(signup_screen, is_active=True)
m.add_screen(main_screen)
m.launch()
