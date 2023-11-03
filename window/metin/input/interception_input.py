
import random
from window.window import Window

from time import sleep
import utils.interception as interception
interception.inputs.keyboard = 1
interception.inputs.mouse = 10


class InterceptionInput(Window):
    def __init__(self, window_name, hwnd=None):
        super().__init__(window_name, hwnd)
        pass

    def start_hitting(self):
        sleep(0.03)
        interception.key_down("space")

    def start_spinning(self):
        sleep(0.03)
        interception.key_down("e")
        sleep(0.03)
        interception.key_down("w")
        sleep(0.03)

    def rotate_forward(self):
        sleep(0.03)
        interception.key_down("w")
        sleep(1.2)
        interception.key_up("w")
        sleep(0.1)

    def press_enter(self):
        interception.press('enter', 2)
        sleep(0.3)
    
    def stop_spinning(self):
        interception.key_up("e")
        sleep(0.03)
        interception.key_up("w")
        sleep(0.03)

    def stop_hitting(self):
        interception.key_up("space")

    def pull_mobs(self):
        interception.press("3", 3, 0.02)

    def pick_up(self):
        interception.key_down("z")
        sleep(6)
        interception.key_up("z")
        
    def move_with_camera_rotation(self):
        interception.key_down("w")
        sleep(0.05)
        interception.key_down("e")
        sleep(0.3)
        interception.key_up("w")
        sleep(0.05)
        interception.key_up("e")

    def activate_flag(self):
        interception.press("3")

    def activate_horse_dodge(self):
        interception.press("4")

    def activate_dodge(self, flag=False):
        if flag: self.activate_flag()
        else: self.activate_horse_dodge()


    def send_mount_away(self):
        # self.press_key(button='Ctrl', mode='click')
        # sleep(0.2)
        # self.press_key(button='b', mode='click')
        pass

    def call_mount(self):
        interception.press("1")
        # self.press_key(button='Fn', mode='click')
        # sleep(0.2)
        # self.press_key(button='1', mode='click')
        

    def recall_mount(self):
        self.call_mount()
        # self.send_mount_away()
        self.un_mount()
        # self.send_mount_away()
        # self.call_mount()
        # self.un_mount()
        pass

    def find_metin(self):
        interception.press("f1")
        sleep(0.1)

    def open_inventory(self):
        interception.press("i")
        sleep(0.1)

    def activate_buffs(self):
        interception.press("f5")

    def start_rotating_up(self):
        interception.key_down("g")

    def stop_rotating_up(self):
        interception.key_up("g")

    def calibrate_with_mouse(self, calibration_type):
        sleep(0.03)
        self.mouse_move(random.randint(280, 400), random.randint(260, 360))
        sleep(0.03)
        interception.mouse_down('right')
        sleep(0.02)
        interception.move_relative(0, random.randint(65, 75))
        sleep(0.02)
        interception.mouse_up('right')
        sleep(0.1)
        self.mouse_move(random.randint(280, 400), random.randint(260, 360))
        sleep(0.2)
        interception.mouse_down('right')
        sleep(0.02)
        if calibration_type=="guard":
            interception.move_relative(0, -random.randint(34, 36))
        elif calibration_type=="first_arena":
            interception.move_relative(0, -random.randint(29, 31))
        elif calibration_type=="second_arena":
            interception.move_relative(0, -random.randint(31, 33))
        sleep(0.1)
        interception.mouse_up('right')
        sleep(0.03)
    def rotate_with_mouse(self):
        
        self.mouse_move(random.randint(300, 400), random.randint(400, 500))
        sleep(0.03)
        # with interception.hold_mouse("right"):
        #     sleep(0.10)
        #     x, y = self.get_relative_mouse_pos()
        #     interception.move_relative(30, 0)
        #     #self.mouse_move(x+random.randint(30, 50), y)

        #sleep(0.1)
        interception.mouse_down('right')
        sleep(0.02)
        interception.move_relative(random.randint(7, 16), 0)
        sleep(0.02)
        interception.mouse_up('right')
        sleep(0.03)
    def start_rotating_down(self):
        interception.key_down("t")

    def stop_rotating_down(self):
        interception.key_up("t")

    def start_rotating_horizontally(self):
        interception.key_down("e")

    def stop_rotating_horizontally(self):
       interception.key_up("e")

    def ride_through_units(self):
        #self.press_key(button='4', mode='click', count=1)
        pass
    def un_mount(self):
        interception.key_down("ctrl")
        sleep(0.05)
        interception.key_down("g")
        sleep(0.05)
        interception.key_up("ctrl")
        sleep(0.05)
        interception.key_up("g")

        # self.press_key(button='Ctrl', mode='click')
        # sleep(0.4)
        # self.press_key(button='h', mode='click')
        
    def activate_aura(self):
        interception.press("2")

    def activate_teleports(self):
        interception.key_down("ctrl")
        sleep(0.04)
        interception.key_down("x")
        sleep(0.04)
        interception.key_up("ctrl")
        sleep(0.04)
        interception.key_up("x")

    def turn_poly_off(self):
        sleep(0.04)
        interception.press("p")
        sleep(0.3)

    def turn_poly_on(self):
        sleep(0.1)
        interception.press("f4")
        sleep(0.2)

    def activate_berserk(self):
        interception.press("2")

    def heal_yourself(self):
        interception.press("1")

    def start_zooming_out(self):
        interception.key_down("f")

    def stop_zooming_out(self):
        interception.key_up("f")

    def start_zooming_in(self):
        interception.key_down("r")

    def stop_zooming_in(self):
        interception.key_up("r")