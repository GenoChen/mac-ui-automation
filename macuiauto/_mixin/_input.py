from pynput.mouse import Button
from pynput.keyboard import Key
from pynput import mouse
from pynput import keyboard


class Mouse(object):
    mouse = mouse.Controller()
    keyboard = keyboard.Controller()


    def drag_mouse_button_left(self, coord: tuple, dest_coord: tuple):
        """Drag the left mouse button without modifiers pressed.

        Parameters: coordinates to click on screen (tuple (x, y))
                    dest coordinates to drag to (tuple (x, y))
                    interval to send event of btn down, drag and up
        Returns: None
        """
        self.mouse.position = coord
        self.mouse.press(Button.left)
        self.mouse.position = dest_coord
        self.mouse.release(Button.left)

    def double_click_drag_mouse_button_left(self, coord: tuple, dest_coord: tuple):
        """Double-click and drag the left mouse button without modifiers
        pressed.

        Parameters: coordinates to double-click on screen (tuple (x, y))
                    dest coordinates to drag to (tuple (x, y))
                    interval to send event of btn down, drag and up
        Returns: None
        """
        self.mouse.position = coord
        self.mouse.press(Button.left)
        self.mouse.release(Button.left)
        self.mouse.press(Button.left)
        self.mouse.position = dest_coord

    def click_mouse_button_left(self, coord=None, count=1):
        """Click the left mouse button without modifiers pressed.

        Parameters: coordinates to click on screen (tuple (x, y))
        Returns: None
        """
        if coord is not None:
            self.mouse.position = coord
        self.mouse.click(Button.left, count)

    def click_mouse_button_right(self, coord=None, count=1):
        """Click the right mouse button without modifiers pressed.

        Parameters: coordinates to click on scren (tuple (x, y))
        Returns: None
        """
        if coord is not None:
            self.mouse.position = coord
        self.mouse.click(Button.right, count)

    def click_mouse_button_left_with_modifiers(self, coord: tuple, modifiers: list[Key], count=1):
        """Click the left mouse button with modifiers pressed.

        Parameters: coordinates to click; modifiers (list) (e.g. ["shift"] or
                    ["command", "shift"])
        Returns: None
        """
        with self.keyboard.pressed(**modifiers):
            self.click_mouse_button_left(coord, count)

    def click_mouse_button_right_with_modifiers(self, coord: tuple, modifiers: list[Key], count=1):
        """Click the right mouse button with modifiers pressed.

        Parameters: coordinates to click; modifiers (list)
        Returns: None
        """
        with self.keyboard.pressed(**modifiers):
            self.click_mouse_button_right(coord, count)

    def double_click_mouse_left(self, coord: tuple):
        """Double-click primary mouse button.

        Parameters: coordinates to click (assume primary is left button)
        Returns: None
        """
        self.mouse.position = coord
        self.mouse.click(Button.left, 2)

    def double_mouse_button_left_with_modifiers(self, coord: tuple, modifiers: list[Key]):
        """Click the left mouse button with modifiers pressed.

        Parameters: coordinates to click; modifiers (list)
        Returns: None
        """
        self.mouse.position = coord
        with self.keyboard.pressed(**modifiers):
            self.mouse.click(Button.left, 2)

    def triple_click_mouse_left(self, coord: tuple):
        """Triple-click primary mouse button.

        Parameters: coordinates to click (assume primary is left button)
        Returns: None
        """
        self.mouse.position = coord
        self.mouse.click(Button.left, 3)


class Keyboard(object):
    keyboard = keyboard.Controller()

    def send_key(self, keychr: str | Key):
        """Send one character with no modifiers."""
        self.keyboard.press(keychr)
        self.keyboard.release(keychr)

    def send_key_with_modifiers(self, keychr: str, modifiers: list[Key]):
        """Send one character with modifiers pressed

        Parameters: key character, modifiers (list) (e.g. ["shift"] or
                    ["command", "shift"]
        """
        with self.keyboard.pressed(*modifiers):
            self.keyboard.press(keychr)
            self.keyboard.release(keychr)

    def type(self, keystr: str):
        """Send a series of characters with no modifiers."""
        self.keyboard.type(keystr)


class KeyboardMouseMixin(Mouse, Keyboard):
    pass
