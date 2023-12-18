import pyautogui

def get_metin_needle_path():
    return r'C:\Users\Filip\Desktop\tob2tm\Metin2-Bot-main\utils/needle_metin.png'

def get_dangeon_25lvl_end_needle_path():
    return r'C:\Users\Filip\Desktop\tob2tm\Metin2-Bot-main\utils/needle_25lvl_dang_end.png'

def get_tesseract_path():
    return r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def get_respawn_needle_path():
    return r'C:\Users\Filip\Desktop\tob2tm\Metin2-Bot-main\utils/needle_respawn.png'

def get_ervelia_metin_needle():
    return r'C:\Users\Filip\Desktop\tob2tm\Metin2-Bot-main\utils/erveliaMetinNeedle.png'

def get_metin_45_path():
    return r'C:\Users\Filip\Desktop\tob2tm\Metin2-Bot-main\utils\metin_45'

def get_second_area_dangeon30():
    return r'C:\Users\Filip\Desktop\tob2tm\versatileMetinBot\utils\images\second_arena.png'

def get_first_area_dangeon30():
    return r'C:\Users\Filip\Desktop\tob2tm\versatileMetinBot\utils\images\first_arena.png'

def get_dangeon_item_dangeon30():
    return r'C:\Users\Filip\Desktop\tob2tm\versatileMetinBot\utils\images\dangeon_item.png'

def get_dangeon_end_image():
    return r'C:\Users\Filip\Desktop\tob2tm\versatileMetinBot\utils\images\dangeon_end.png'

def get_dangeon_enter_the_dangeon_button():
    return r'C:\Users\Filip\Desktop\tob2tm\versatileMetinBot\utils\images\yes_button_dang_entry.png'

def get_dangeon_you_cannot_enter_the_dangeon_button():
    return r'C:\Users\Filip\Desktop\tob2tm\versatileMetinBot\utils\images\ok_button_dangeon_entry.png'

def get_empty_mount_image():
    return r'C:\Users\Filip\Desktop\tob2tm\versatileMetinBot\utils\images\empty_mount.png'

def gm_icon_image():
    return r'C:\Users\Filip\Desktop\tob2tm\versatileMetinBot\utils\images\gmicon.png'

def get_eq_ervelia_stripe():
    return r'C:\Users\Filip\Desktop\tob2tm\versatileMetinBot\utils\images\eq_stripe_ervelia.png'

def countdown():
    pyautogui.countdown(1)

def gm_detection_music():
    return r'C:\Users\Filip\Desktop\tob2tm\versatileMetinBot\utils\music\alarm_gm_detection.mp3'

import os

def get_absolute_path(relative_path):
    # Directory of the image_paths.py file
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(base_dir, relative_path)

# Define paths
ERVELIA_DANG30_IMAGE_PATHS = {
    'brown_belt': get_absolute_path('utils/images/ervelia/dang_30_items/brown_belt.png'),
    'green_belt': get_absolute_path('utils/images/ervelia/dang_30_items/green_belt.png'),
    'red_dragon': get_absolute_path('utils/images/ervelia/dang_30_items/red_dragon.png'),
    # Add more images here
}