import win32gui

class Window:
    _used_hwnds = set()  # Class variable to keep track of used hwnds

    def __init__(self, name):
        self.name = name
        self.hwnd = None

    def _get_hwnd_by_name(self):
        def window_enum_callback(hwnd, output):
            if win32gui.GetWindowText(hwnd) == self.name and hwnd not in self._used_hwnds:
                output.append(hwnd)
            return True
        
        hwnds = []
        win32gui.EnumWindows(window_enum_callback, hwnds)
        return hwnds[0] if hwnds else None

    def add_window_by_hwnd(self):
        hwnd = self._get_hwnd_by_name()
        if hwnd:
            self._used_hwnds.add(hwnd)  # Adding hwnd to the set of used hwnds
            self.hwnd = hwnd
            print(f"Hwnd {hwnd} has been added.")
        else:
            print("No available hwnd found.")

# Example usage:
window1 = Window("Ervelia")
window1.add_window_by_hwnd()

window2 = Window("Ervelia")
window2.add_window_by_hwnd()
