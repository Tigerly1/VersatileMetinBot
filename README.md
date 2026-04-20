## VersatileMetinBot

Metin2 dangeon private server bot using computer vision and gpu with custom model

## How to run

- install interceptor (python package for intercepting mouse driver on pc to be able to input to the game with code.
- install requirements
- edit configuration
  - set the game window name
  - set the model (there is a code for yolov8)
  - <img width="1150" height="458" alt="image" src="https://github.com/user-attachments/assets/8eca7ca5-9640-4097-a064-4b6eddbcc2bf" />
- set number of windows
- RUN :D

Yolov8 fine-tuned, multi-threaded, low level programming with a lot of computer vision game bot

![S1JE7.gif](https://github.com/Tigerly1/VersatileMetinBot/blob/multiwindow_tests/Animation999666.gif)

<img width="551" height="460" alt="image" src="https://github.com/user-attachments/assets/50e44a5c-71a8-4087-8578-6ff33ef2d8c3" />


### Models that were used to detect the game object (4-8 objects depending on the games) + notebooks

#### Yolo v8s Gtx1660 (30ms inference time)

[Notebook](https://colab.research.google.com/drive/1SNpYffK41NiODefSK7SXl8fQ_ggWxOPM)

#### Yolo v5 Gtx1660 (50 ms inference)

[Notebook](https://colab.research.google.com/drive/1BkhNTW1-MEIkyPMl9dbWS3NoHn-h38LR?usp=sharing)

Telegram notifications for detecting the issues and logging how many dungeons were made without restarting the program:

![telegram notifications](https://i.ibb.co/6JJ731X/image.png)
