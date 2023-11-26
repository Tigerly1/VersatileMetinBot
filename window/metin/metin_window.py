
import time
import psutil
import win32gui, win32ui, win32con, win32com.client, win32process
from time import sleep
import numpy as np
import utils.interception as interception
from window.window import Window
interception.inputs.keyboard = 0
interception.inputs.mouse = 10
import ctypes
import pythoncom
import threading
# 10,24 i 48:46


class MetinWindow(Window):
    _used_hwnds = set() 

    def __init__(self, window_name):   
        self.name = window_name
        self.open_window_await_time = 15
        self.window_open_click_time = None
        pythoncom.CoInitialize()
    
        if not self._set_hwnd_of_window_by_name():
            self.open_new_window_first_time()
        
        self.pid = self._get_pid_by_hwnd(self.hwnd)
        self.temp_hwnd = 0
        if self.hwnd == 0:
            self.open_new_window_first_time()
            #raise Exception(f'Window "{self.name}" not found!')

        self.set_window_foreground()
        super().__init__(window_name, self.hwnd)
        

        self.capture_lock = threading.Lock()


    def _set_hwnd_of_window_by_name(self):
        hwnd = self._get_hwnd_by_name()
        if hwnd:
            self._used_hwnds.add(hwnd)  # Adding hwnd to the set of used hwnds
            self.hwnd = hwnd
            print(f"Hwnd {hwnd} has been added.")
            return True
        else:
            print("No available hwnd found.")
            return False

    def _get_hwnd_by_name(self):
        def window_enum_callback(hwnd, output):
            if win32gui.GetWindowText(hwnd) == self.name and hwnd not in self._used_hwnds:
                output.append(hwnd)
            return True
        
        hwnds = []
        win32gui.EnumWindows(window_enum_callback, hwnds)
        return hwnds[0] if hwnds else None
    
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

    def _get_pid_by_hwnd(self, hwnd):
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return pid

    def activate(self):
        interception.click(self.x, self.y-25)
        sleep(0.3)
        self.mouse_click()
        sleep(0.05)

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
        
    def check_if_window_is_opened(self):
        window = win32gui.FindWindow(None, self.name)
        if window == 0:
            return False
        else:
            return True
        
    def open_new_window_first_time(self):
        
        #game_path = r"C:\Users\Filip\Desktop\Ervelia_official_011\Ervelia.pl\metin2client.exe"
        game_path = r"C:\Users\Filip\Desktop\Ervelia_official_011\Ervelia.pl\Ervelia Patcher.exe"
        game_dir = r"C:\Users\Filip\Desktop\Ervelia_official_011\Ervelia.pl"
        # Request UAC elevation
        patcher_hwnd = win32gui.FindWindow(None, "Ervelia Patcher")

        if not patcher_hwnd:
            
            ctypes.windll.shell32.ShellExecuteW(None, "runas", game_path, None, game_dir, 1)
            time.sleep(2)
        
        print("XXXXXXXXX")
        interception.move_to(1440,1059)
        sleep(0.03)
        interception.left_click(1)
        sleep(0.03)
        interception.move_to(1100,650)
        patcher = win32gui.FindWindow(None, "Ervelia Patcher")
        win32gui.ShowWindow(patcher, 5)
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(patcher)
        sleep(0.1)
        interception.left_click(1)
        time.sleep(10)

        possible_pids = [p.info['pid'] for p in psutil.process_iter(attrs=['pid', 'name']) if p.info['name'] == "metin2client.exe"]
        possible_pids.sort(key=lambda p: psutil.Process(p).create_time())
        self.pid = possible_pids[0] if possible_pids else None
        self._set_hwnd_of_window_by_name()
        self.window_open_click_time = None

    def open_new_window(self):
        
        #game_path = r"C:\Users\Filip\Desktop\Ervelia_official_011\Ervelia.pl\metin2client.exe"
        game_path = r"C:\Users\Filip\Desktop\Ervelia_official_011\Ervelia.pl\Ervelia Patcher.exe"
        game_dir = r"C:\Users\Filip\Desktop\Ervelia_official_011\Ervelia.pl"
        # Request UAC elevation
        patcher_hwnd = win32gui.FindWindow(None, "Ervelia Patcher")

        if not patcher_hwnd:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", game_path, None, game_dir, 1)
            return
        
        if self.window_open_click_time == None:
            interception.move_to(1440,1059)
            sleep(0.03)
            interception.left_click(1)
            sleep(0.03)
            interception.move_to(1100,650)
            patcher = win32gui.FindWindow(None, "Ervelia Patcher")
            pythoncom.CoInitialize()
            win32gui.ShowWindow(patcher, 5)
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%')
            win32gui.SetForegroundWindow(patcher)
            sleep(0.1)
            interception.left_click(1)
            self.window_open_click_time = time.time()

        if time.time() - self.window_open_click_time > self.open_window_await_time:
            possible_pids = [p.info['pid'] for p in psutil.process_iter(attrs=['pid', 'name']) if p.info['name'] == "metin2client.exe"]
            possible_pids.sort(key=lambda p: psutil.Process(p).create_time())
            self.pid = possible_pids[0] if possible_pids else None
            self.hwnd = self._set_hwnd_of_window_by_name()
            print(self.hwnd)
            self.window_open_click_time = None

        
        
        
        
        
        # Now, we identify the window with the shortest uptime
       
        
    def capture(self):
        # https://stackoverflow.com/questions/6312627/windows-7-how-to-bring-a-window-to-the-front-no-matter-what-other-window-has-fo\
        with self.capture_lock:
            try:
                if self.hwnd == None:
                    raise Exception("None")
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
            except Exception as e:
                    time.sleep(0.1)
                    hwnd_exists = self._check_if_hwnd_exits(self.hwnd)
                    print(hwnd_exists)
                    if hwnd_exists:
                        print("OKAY")
                        #self.open_new_window()
                        self.set_window_foreground()
                        return self.capture()
                    if not hwnd_exists:
                        print("NIE OKAY")
                        self.open_new_window()
                        #self.set_window_foreground()
                        raise Exception("trying to open new window")
                
            
