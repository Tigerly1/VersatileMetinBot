
import pyautogui
import win32gui
from time import sleep
import subprocess
import utils.interception as interception
from window.window import Window
interception.inputs.keyboard = 1
interception.inputs.mouse = 10


class OskWindow(Window):
    def __init__(self, window_name):
        if win32gui.FindWindow(None, window_name) == 0:
            returned_value = subprocess.Popen('osk', shell=True)
            sleep(1)
        super().__init__(window_name)

        self.width, self.height = 576, 173
        self.gw_object.resizeTo(self.width, self.height)

        self.key_pos = {'space': (148, 155), 'Fn': (11, 150), '1': (55, 61), '2': (79, 67),
                        '3': (100, 65), '4': (122, 59), 'z': (67, 132), 'e': (87, 87),
                        'q': (40, 85), 'g': (134, 107), 't': (129, 86), 'Ctrl': (35, 150),
                        'h': (159, 109), 'r': (107, 88), 'f': (114, 109), 'b': (156, 134)
                        }

    def start_hitting(self):
        self.press_key(button='space', mode='down')

    def stop_hitting(self):
        self.press_key(button='space', mode='up')

    def pull_mobs(self):
        self.press_key(button='2', mode='click', count=3)

    def pick_up(self):
        self.press_key(button='z', mode='click', count=1)

    def activate_tp_ring(self):
        self.press_key(button='3', mode='click', count=1)

    def send_mount_away(self):
        self.press_key(button='Ctrl', mode='click')
        sleep(0.2)
        self.press_key(button='b', mode='click')

    def call_mount(self):
        self.press_key(button='Fn', mode='click')
        sleep(0.2)
        self.press_key(button='1', mode='click')

    def recall_mount(self):
        self.send_mount_away()
        self.un_mount()
        self.send_mount_away()
        self.call_mount()
        self.un_mount()

    def start_rotating_up(self):
        self.press_key(button='g', mode='down')

    def stop_rotating_up(self):
        self.press_key(button='g', mode='up')

    def start_rotating_down(self):
        self.press_key(button='t', mode='down')

    def stop_rotating_down(self):
        self.press_key(button='t', mode='up')

    def start_rotating_horizontally(self):
        self.press_key(button='e', mode='down')

    def stop_rotating_horizontally(self):
        self.press_key(button='e', mode='up')

    def ride_through_units(self):
        self.press_key(button='4', mode='click', count=1)

    def un_mount(self):
        self.press_key(button='Ctrl', mode='click')
        sleep(0.4)
        self.press_key(button='h', mode='click')

    def activate_aura(self):
        self.press_key(button='1', mode='click')

    def activate_berserk(self):
        self.press_key(button='2', mode='click')

    def start_zooming_out(self):
        self.press_key(button='f', mode='down')

    def stop_zooming_out(self):
        self.press_key(button='f', mode='up')

    def start_zooming_in(self):
        self.press_key(button='r', mode='down')

    def stop_zooming_in(self):
        self.press_key(button='r', mode='up')

    def press_key(self, button, mode='click', count=1):
        x, y = self.x, self.y
        if button not in self.key_pos.keys():
            raise Exception('Unknown key!')
        else:
            x += self.key_pos[button][0]
            y += self.key_pos[button][1]
            pyautogui.moveTo(x=x, y=y)
        if mode == 'click':
            for i in range(count):
                pyautogui.mouseDown()
                sleep(0.1)
                pyautogui.mouseUp()
        elif mode == 'down':
            pyautogui.mouseDown()
        elif mode == 'up':
            pyautogui.mouseUp()
