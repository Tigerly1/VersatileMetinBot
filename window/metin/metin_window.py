
import psutil
import win32gui, win32ui, win32con, win32com.client, win32process
from time import sleep
import numpy as np
import utils.interception as interception
from window.window import Window
interception.inputs.keyboard = 1
interception.inputs.mouse = 10
import ctypes


class MetinWindow(Window):
    def __init__(self, window_name):   
        self.name = window_name
        self.hwnd = self._get_hwnd_by_name()
        self.pid = self._get_pid_by_hwnd(self.hwnd)

        if self.hwnd == 0:
            self.open_new_window()
            #raise Exception(f'Window "{self.name}" not found!')
        
        super().__init__(window_name)
        self.set_window_foreground()

    def _get_hwnd_by_name(self):
        def window_enum_callback(hwnd, output):
            if win32gui.GetWindowText(hwnd) == self.name:
                output.append(hwnd)
            return True
        
        hwnds = []
        win32gui.EnumWindows(window_enum_callback, hwnds)
        return hwnds[0] if hwnds else None

    def _get_pid_by_hwnd(self, hwnd):
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return pid

    def activate(self):
        self.mouse_move(self.x, self.y-10)
        sleep(0.1)
        self.mouse_click()

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
    def open_new_window(self):
        
        #game_path = r"C:\Users\Filip\Desktop\Ervelia_official_011\Ervelia.pl\metin2client.exe"
        game_path = r"C:\Users\Filip\Desktop\Ervelia_official_011\Ervelia.pl\Ervelia Patcher.exe"
        game_dir = r"C:\Users\Filip\Desktop\Ervelia_official_011\Ervelia.pl"
        # Request UAC elevation
        ctypes.windll.shell32.ShellExecuteW(None, "runas", game_path, None, game_dir, 1)
        sleep(60)
        
        interception.move_to(1100,650)
        patcher = win32gui.FindWindow(None, "Ervelia Patcher")
        win32gui.ShowWindow(patcher, 5)
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(patcher)
        sleep(0.5)
        interception.left_click(1)
        sleep(20)
        max_wait_time = 200
        time_passed = 0

        possible_pids = [p.info['pid'] for p in psutil.process_iter(attrs=['pid', 'name']) if p.info['name'] == self.name]
        possible_pids.sort(key=lambda p: psutil.Process(p).create_time())
        self.pid = possible_pids[0] if possible_pids else None
        self.hwnd = self._get_hwnd_by_name()

        while not self.check_if_window_is_opened():
            sleep(1)
            time_passed += 1
            if time_passed > max_wait_time:
                break
        if not self.check_if_window_is_opened():
            self.open_new_window()
        
        
        
        # Now, we identify the window with the shortest uptime
       
        
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
        except Exception as e:
            try:
                print(str(e))
                print("Failed to capture window, will try to open a new window")

                self.hwnd = win32gui.FindWindow(None, self.name)
                if self.hwnd != 0:
                    #self.open_new_window()
                    self.set_window_foreground()
                    return self.capture()
                if self.hwnd == 0:
                    self.open_new_window()
                    self.set_window_foreground()
                    return self.capture()
                return self.capture()
            except:
                return self.capture()
