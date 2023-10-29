
import pyautogui
import win32gui, win32ui, win32con, win32com.client
from time import sleep
import subprocess
import pygetwindow as gw
import numpy as np
import pythoncom
import utils.interception as interception
interception.inputs.keyboard = 1
interception.inputs.mouse = 10
import psutil
import pygetwindow as gw

class Window:
    def __init__(self, window_name):
        self.name = window_name
        self.hwnd = win32gui.FindWindow(None, window_name)
        if self.hwnd == 0:
            raise Exception(f'Window "{self.name}" not found!')

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

        pythoncom.CoInitialize()
        win32gui.ShowWindow(self.hwnd, 5)
        self.shell = win32com.client.Dispatch("WScript.Shell")
        self.shell.SendKeys('%')
        win32gui.SetForegroundWindow(self.hwnd)

    def set_window_foreground(self):
        self.hwnd = win32gui.FindWindow(None, self.name)
        win32gui.ShowWindow(self.hwnd, 5)
        self.shell = win32com.client.Dispatch("WScript.Shell")
        self.shell.SendKeys('%')
        win32gui.SetForegroundWindow(self.hwnd)

    def close_window(self):
        self.hwnd = win32gui.FindWindow(None, self.name)
        #win32gui.PostMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)
        #win32gui.CloseWindow(self.hwnd)
        print("The windows is now closed")

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
            print(self.get_relative_mouse_pos)
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

    def move_window(self, x, y):
        win32gui.MoveWindow(self.hwnd, x - 7, y, self.width, self.height, True)
        self.x, self.y = x, y

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