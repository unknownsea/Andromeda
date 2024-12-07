import ctypes
from ctypes import wintypes
import threading
import time

import dearpygui.dearpygui as dpg

class MENU:
    def init_ui(title=str):
        dpg.create_context()

        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)

        window_width = 380
        window_height = 400
        x_pos = int((screen_width - window_width) / 2)
        y_pos = int((screen_height - window_height) / 2)

        with dpg.window(label="", no_title_bar=True, no_move=True, no_resize=True, no_close=True, width=window_width, height=window_height):
            with dpg.tab_bar():
                with dpg.tab(label="Console"):
                    with dpg.child_window(horizontal_scrollbar=True, width=350, height=325, tag="console_window"):
                        pass

        dpg.create_viewport(title=title, width=window_width, height=window_height, x_pos=x_pos, y_pos=y_pos, resizable=False, always_on_top=False)

        def enable_dark_mode(hwnd):
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
            set_window_attribute.argtypes = [wintypes.HWND, wintypes.DWORD, wintypes.LPCVOID, wintypes.DWORD]
            set_window_attribute.restype = ctypes.c_long
            value = ctypes.c_int(2)
            set_window_attribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value))

        dpg.setup_dearpygui()
        dpg.show_viewport()

        hwnd = ctypes.windll.user32.FindWindowW(None, title)
        enable_dark_mode(hwnd)

        
        dpg.start_dearpygui()
        return dpg

    def close_program():
        dpg.stop_dearpygui()

    def log(message, color):
        dpg.add_text(message, parent="console_window", color=color)
        dpg.set_y_scroll("console_window", dpg.get_y_scroll_max("console_window"))

ui_thread = threading.Thread(target=MENU.init_ui, args=("Andromeda",)).start()
