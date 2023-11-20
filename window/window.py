
import pyautogui
import win32gui, win32ui, win32con, win32com.client, win32process
from time import sleep
import subprocess
import pygetwindow as gw
import numpy as np
import pythoncom
import utils.interception as interception
interception.inputs.keyboard = 0
interception.inputs.mouse = 10
import psutil
import pygetwindow as gw


def windows_swap_fix():
    interception.move_to(1440,1059)
    # sleep(0.03)
    # interception.left_click(1)
    # sleep(0.03)

class Window:
    def __init__(self, window_name, hwnd=None):
        self.name = window_name

        if hwnd == 0 or hwnd == None:
            self.hwnd = win32gui.FindWindow(None, window_name)
            #raise Exception(f'Window "{self.name}" not found!')
        else:
            self.hwnd = hwnd
        _, self.pid = win32process.GetWindowThreadProcessId(self.hwnd)

        # if self.pid in Window.managed_windows:
        #     raise Exception(f'Window "{self.name}" with PID "{self.pid}" is already being managed.')


        self.gw_object = gw.getWindowsWithTitle(self.name)[0]

        rect = win32gui.GetWindowRect(self.hwnd)
        border = 8
        title_bar = 31
        self.x = rect[0] + border
        self.y = rect[1] + title_bar
        self.width = rect[2] - self.x - border
        self.height = rect[3] - self.y - border

        self.cropped_x = border
        self.cropped_y = title_bar

        self.open_window_await_time = 6
        self.window_open_click_time = None

        interception.move_to(1440,1059)
        sleep(0.03)
        interception.left_click(1)
        sleep(0.03)

        pythoncom.CoInitialize()
        win32gui.ShowWindow(self.hwnd, 5)
        self.shell = win32com.client.Dispatch("WScript.Shell")
        self.shell.SendKeys('%')
        win32gui.SetForegroundWindow(self.hwnd)

    def _get_hwnd_by_name(self):
        def window_enum_callback(hwnd, output):
            if win32gui.GetWindowText(hwnd) == self.name:
                output.append(hwnd)
            return True
        
        hwnds = []
        win32gui.EnumWindows(window_enum_callback, hwnds)
        return hwnds[0] if hwnds else None

    def _get_hwnd_from_pid(self):
        """
        Get HWND from PID. Since a PID can be associated with multiple windows,
        this function returns the HWND whose window title matches the name.
        """
        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if pid == self.pid:
                    hwnds.append(hwnd)
            return True
        
        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        for hwnd in hwnds:
            if win32gui.GetWindowText(hwnd) == self.name:
                return hwnd
        return None
    def _check_if_hwnd_exits(self, hwnd):
        def window_enum_callback(hwnd, output):
            if win32gui.GetWindowText(hwnd) == self.name:
                output.append(hwnd)
            return True
        
        hwnds = []

        win32gui.EnumWindows(window_enum_callback, hwnds)
        #print(hwnds)
        if hwnd in hwnds:
            return True
        else: return False
   

    def set_window_foreground(self,  second_try = True):
        if self._check_if_hwnd_exits(self.hwnd):
                win32gui.ShowWindow(self.hwnd, 5)
                self.shell = win32com.client.Dispatch("WScript.Shell")
                self.shell.SendKeys('%')
                win32gui.SetForegroundWindow(self.hwnd)
                #print('hwnd of {} is on'.format(self.hwnd))
           
            
    def close_window(self):
        if self._check_if_hwnd_exits(self.hwnd):
            
            win32gui.PostMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)
            #print(f"The window '{self.name}' with PID {self.pid} is now closed")

    def move_window(self, x, y):
        if self._check_if_hwnd_exits(self.hwnd):
            rect = win32gui.GetWindowRect(self.hwnd)
            win32gui.MoveWindow(self.hwnd, x, y, rect[2]-rect[0], rect[3]-rect[1], True)

    def find_process_and_kill_window(self):
    # Find the window by title
        window = gw.getWindowsWithTitle(self.name)

        if window:
            window = window[0]
            pid = None

            for proc in psutil.process_iter(attrs=['pid', 'name']):
                try:
                    if "metin2client" in proc.info['name']:
                        pid = proc.info['pid']
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass

            if pid:
                try:
                    process = psutil.Process(pid)  # Get the process by PID
                    process.terminate()  # Terminate the process
                    print(f"Terminated process with PID {pid}")
                except psutil.NoSuchProcess:
                    print(f"Process with PID {pid} not found")
                except psutil.AccessDenied:
                    print(f"Access denied when terminating process with PID {pid}")
            else:
                print(f"No process ID found for window '{self.name}'")
        else:
            print(f"Window with title '{self.name}' not found")

    def get_relative_mouse_pos(self):
        curr_x, curr_y = pyautogui.position()
        return curr_x - self.x, curr_y - self.y

    def print_relative_mouse_pos(self, loop=False):
        repeat = True
        while repeat:
            repeat = loop
            #print(self.get_relative_mouse_pos)
            if loop:
                sleep(1)

    def mouse_move(self, x, y):
        #pyautogui.moveTo(self.x + x, self.y + y, duration=0.1)
        interception.move_to(self.x + x, self.y + y)

    def mouse_click(self, x=None, y=None):
        sleep(0.2)
        if x is None and y is None:
            x, y = self.get_relative_mouse_pos()
        interception.click(self.x + x, self.y + y)
        #pyautogui.click(self.x + x, self.y + y, duration=0.1)

    def mouse_right_click(self, x=None, y=None):
        sleep(0.03)
        if x is None and y is None:
            x, y = self.get_relative_mouse_pos()
        interception.right_click(1)

    def limit_coordinate(self, pos):
        pos = list(pos)
        if pos[0] < 0: pos[0] = 0
        elif pos[0] > self.width: pos[0] = self.width
        if pos[1] < 0: pos[1] = 0
        elif pos[1] > self.height: pos[1] = self.height
        return tuple(pos)

    def capture(self):
        # https://stackoverflow.com/questions/6312627/windows-7-how-to-bring-a-window-to-the-front-no-matter-what-other-window-has-fo\
        try:
            wDC = win32gui.GetWindowDC(self.hwnd)
            dcObj = win32ui.CreateDCFromHandle(wDC)
            cDC = dcObj.CreateCompatibleDC()
            dataBitMap = win32ui.CreateBitmap()
            dataBitMap.CreateCompatibleBitmap(dcObj, self.width, self.height)
            cDC.SelectObject(dataBitMap)
            cDC.BitBlt((0, 0), (self.width, self.height), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)
            # dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')

            # https://stackoverflow.com/questions/41785831/how-to-optimize-conversion-from-pycbitmap-to-opencv-image
            signedIntsArray = dataBitMap.GetBitmapBits(True)
            img = np.fromstring(signedIntsArray, dtype='uint8')
            img.shape = (self.height, self.width, 4)

            # Free Resources
            dcObj.DeleteDC()
            cDC.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, wDC)
            win32gui.DeleteObject(dataBitMap.GetHandle())

            # Drop the alpha channel
            img = img[..., :3]

            # make image C_CONTIGUOUS
            img = np.ascontiguousarray(img)

            return img
        except:
            print("Failed to capture window, will open a new window")

            file_path = r"C:\Users\Filip\Downloads\MasnoMT2\patcher.exe"
            subprocess.run(["runas", "/user:Administrator", file_path])