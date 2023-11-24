import datetime
import os
from threading import Thread, Lock

import torch
import time
import numpy as np
import cv2 as cv
import tensorflow as tf
from openvino.runtime import Core
from utils.helpers.paths import get_second_area_dangeon30
from ultralytics import YOLO
from utils.helpers.vision import Vision

class CaptureAndDetect:

    DEBUG = False

    def __init__(self, metin_window, model_path, hsv_filter):
        self.metin_window = metin_window
        self.vision = Vision()
        #self.snowman_hsv_filter = hsv_filter
        #self.classifier = cv.CascadeClassifier(model_path)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # print(device)
        # self.model = torch.hub.load(r'C:\Users\Filip\Desktop\tob2tm\Metin2-Bot-main\yolov5', 'custom', path=r'C:\Users\Filip\Desktop\tob2tm\versatileMetinBot\detectors\yolo\data\upgraded.pt', source='local',force_reload=True )
        self.model = YOLO(r'C:\Users\Filip\Desktop\tob2tm\versatileMetinBot\detectors\yolo\data\v8.pt').to(device)
        self.screenshot = None
        self.screenshot_time = None

        self.processed_image = None

        self.detection = None
        self.detection_time = None
        self.detection_image = None

        self.detection_tries = 5 

        self.hwnd_of_captured_screenshot = None
        self.temporar_hwnd = None

        self.stopped = False
        self.lock = Lock()

        self.is_object_detector_enabled = False

        self.screen_capture_thread = Thread(target=self.continuous_screen_capture)
        self.screen_capture_thread.daemon = True  # Set as a daemon so it will be killed once the main thread is done
        self.screen_capture_thread.start()
        # self.vision.init_control_gui() # Uncomment do debug HSV filter

    def continuous_screen_capture(self):
        while not self.stopped:
            try:
                #print(str(datetime.datetime.now().strftime("%H:%M:%S:%f")[:-3]) + " TIME CAPTURE STARTED")
                temporar_hwnd = self.metin_window.hwnd
                screenshot = self.metin_window.capture()

                #print(str(datetime.datetime.now().strftime("%H:%M:%S:%f")[:-3]) + " TIME CAPTURE ENDED")
                self.lock.acquire()
                self.screenshot = screenshot
                self.screenshot_time = time.time()
                self.temporar_hwnd = temporar_hwnd
                self.lock.release()
            except:
                # Handle exceptions if needed
                pass
            time.sleep(0.006)  # Small sleep to prevent hogging the CPU

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def run(self):
        while not self.stopped:
            # Take screenshot
            #print(str(datetime.datetime.now().strftime("%H:%M:%S:%f")[:-3]) + " TIME STARTED")
            self.lock.acquire()
            screenshot = self.screenshot
            temporar_hwnd = self.temporar_hwnd
            screenshot_time = self.screenshot_time
            self.lock.release()
            if screenshot is not None:
                start_x = (1024 - 70) // 2
                end_x = start_x + 70
                start_y = (768 - 70) // 2
                end_y = start_y + 70
                # Make the middle region black (set pixel values to [0, 0, 0])
                screenshot[start_y:end_y, start_x:end_x, :] = [0, 0, 0]           
                detection = None
                detection_time = None
                detection_image = screenshot.copy()
                # Convert your image to the appropriate format if necessary

                if self.is_object_detector_enabled:
                    detection_time = time.time()
                    #print(str(datetime.datetime.now().strftime("%H:%M:%S:%f")[:-3]) + " TIME STARTED DETECTION")
                    # screenshot_gpu = torch.from_numpy(screenshot).to(self.device) #to gpu
                    results = self.model(screenshot, verbose=False)
                    #results.print()
                    #results_pandas_df = results.pandas().xyxy[0]
                    #print(str(datetime.datetime.now().strftime("%H:%M:%S:%f")[:-3]) +" TIME DETECTION CALCULATED")
                    class_names = self.model.names
                    boxes = []
                    output_scores = []
                    labels = []
                    # Assuming results is a list of tensors, where each tensor is detections for an image
                    for x in results:
                        x = x.boxes.cpu()
                        boxes.append(x.xyxy.numpy())
                        output_scores.append(x.conf.numpy())
                        labels.append(x.cls.numpy())
                        
                
                # Flatten the lists of boxes, scores, and labels
                    flat_boxes = np.concatenate(boxes)
                    flat_scores = np.concatenate(output_scores)
                    flat_labels = np.concatenate(labels)

                    mask = flat_scores >= 0.57
                    filtered_boxes = flat_boxes[mask]
                    filtered_scores = flat_scores[mask]
                    filtered_labels = flat_labels[mask]

                    # Convert filtered labels to their corresponding names
                    filtered_label_names = [class_names[int(label)] for label in filtered_labels]

                    # Get sorted indices based on filtered scores
                    sorted_indices = np.argsort(filtered_scores)[::-1]

                    # Apply the sorted indices to the filtered arrays
                    sorted_rectangles = filtered_boxes[sorted_indices]
                    sorted_scores = filtered_scores[sorted_indices]
                    sorted_labels = [filtered_label_names[i] for i in sorted_indices]
                    #print(str(datetime.datetime.now().strftime("%H:%M:%S:%f")[:-3]) +" TIME DETECTION PROCESSED")
                    if len(sorted_rectangles):
                        # detection = {
                        #     'rectangles': boxes,
                        #     'scores': output_scores,
                        #     'labels': labels
                        # }
                        detection = {
                            'rectangles': sorted_rectangles,
                            'scores': sorted_scores,
                            'labels': sorted_labels
                        }
                        #print(detection)
                        #print(detection)
                        sorted_indices = np.argsort(detection['scores'])[::-1]
                        sorted_rectangles = detection['rectangles'][sorted_indices]
                        detection['rectangles'] = sorted_rectangles
                        sorted_scores = detection['scores'][sorted_indices]
                        detection['scores'] = sorted_scores
                        # Use to display the best box (the one with the highest score)
                        best_box = detection['rectangles'][0]
                        best_score = detection['scores'][0]
                        best_label = detection['labels'][0]

                        for box, score, label in zip(detection['rectangles'][:6], detection['scores'][:6], detection['labels'][:6]):
                            if score > 0.02:
                                self.vision.draw_rectangle_xmin_ymin_xmax_ymax(detection_image,box, (255,0,0))
                                top_left = (int(box[0]), int(box[1]))
                                bottom_right = (int(box[2]), int(box[3]))
                                # Put the probability on the image
                                #label = f"{score:.2f}"
                                detection_image = cv.putText(detection_image, label + " " + str(score), (top_left[0], top_left[1] - 10),
                                                            cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv.LINE_AA)
                        
                        # Highlighting the best box in a different color (optional)
                        top_left = (int(best_box[0]), int(best_box[1]))
                        bottom_right = (int(best_box[2]), int(best_box[3]))
                        color = (0, 0, 255)  # BGR color for best bounding box
                        detection_image = cv.rectangle(detection_image, top_left, bottom_right, color, 2)

                        # Put the highest probability on the image for the best box
                        #label = f"{best_score:.2f}"
                        detection_image = cv.putText(detection_image, best_label + " " + str(best_score), (top_left[0], top_left[1] - 10),
                                                    cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv.LINE_AA)
                        
                        detection['click_pos'] = int((best_box[0] + best_box[2]) / 2), int((best_box[1] + best_box[3])/2)
                        self.vision.draw_marker(detection_image, detection['click_pos'])
                        #print(str(datetime.datetime.now().strftime("%H:%M:%S:%f")[:-3]) +" TIME DETECTION DRAWED")

                    

                # Acquire lock and set new images
                self.lock.acquire()
                self.detection = detection
                self.detection_time = detection_time
                self.detection_image = detection_image
                # print(self.metin_window.hwnd)
                # print("and temporar" + str(temporar_hwnd))
                if temporar_hwnd == self.metin_window.hwnd:
                    self.hwnd_of_captured_screenshot = self.metin_window.hwnd
                self.lock.release()
                #print(str(datetime.datetime.now().strftime("%H:%M:%S:%f")[:-3]) +" TIME DETECTION END")
                #time_to_go_to_sleep = 0.04 if not detection else  0.20 * len(detection['scores']) + 0.2
                #time.sleep(time_to_go_to_sleep)
                #print("TIME END: " + str(time.time()))

            if self.DEBUG:
                time.sleep(1)
    def try_x_matches_before_screenshot(self):
        self.lock.acquire()
        screenshot = None if self.screenshot is None else self.screenshot.copy()
        screenshot_time = self.screenshot_time
        detection = None if self.detection is None else self.detection.copy()
        detection_time = self.detection_time
        detection_image = None if self.detection_image is None \
            else self.detection_image.copy()
        self.lock.release()
        return screenshot, screenshot_time, detection, detection_time, detection_image

    def set_object_detector_state(self,state):
        self.lock.acquire()
        self.is_object_detector_enabled = state
        self.lock.release()

    def stop(self):
        self.stopped = True

    def change_window_of_detection(self, window):

        self.lock.acquire()
        self.metin_window = window
        self.lock.release()

    def get_info(self):
        self.lock.acquire()
        screenshot = None if self.screenshot is None else self.screenshot.copy()
        screenshot_time = self.screenshot_time
        detection = None if self.detection is None else self.detection.copy()
        detection_time = self.detection_time
        detection_image = None if self.detection_image is None \
            else self.detection_image.copy()
        hwnd_of_detection = self.hwnd_of_captured_screenshot
        self.lock.release()
        return screenshot, screenshot_time, detection, detection_time, detection_image, hwnd_of_detection

    def find_best_match(self, rectangles):
        ideal_width = 80
        diff = []
        for rectangle in rectangles:
            diff.append(abs(rectangle[2] - ideal_width))
        return rectangles[np.argmin(diff)]
        # best = rectangles[np.argmax(rectangles['scores'])]
        # return best

    def get_image_paths(self, directory):
        # List of common image extensions
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tif', '.tiff', '.webp']

        # Collect the paths of all image files in the directory
        image_paths = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    full_path = os.path.join(root, file)
                    image_paths.append(full_path)

        return image_paths