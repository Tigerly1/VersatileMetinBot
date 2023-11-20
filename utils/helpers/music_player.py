from playsound import playsound

from utils.helpers.paths import gm_detection_music

def play_music(mp3_file = gm_detection_music()):
    playsound(mp3_file)

# Replace 'your-music-file.mp3' with the path to your MP3 file
