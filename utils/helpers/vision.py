# Mostly copied from https://github.com/learncodebygaming/opencv_tutorials/blob/master/006_hsv_thresholding/vision.py
import cv2 as cv
import numpy as np
import os
from pathlib import Path
import time
import matplotlib.pyplot as plt
from IPython import display
from sklearn.cluster import DBSCAN
from PIL import ImageGrab

from utils.helpers.paths import get_metin_needle_path


class HsvFilter:
    def __init__(self, hMin=None, sMin=None, vMin=None, hMax=None, sMax=None, vMax=None,
                    sAdd=None, sSub=None, vAdd=None, vSub=None):
        self.hMin = hMin
        self.sMin = sMin
        self.vMin = vMin
        self.hMax = hMax
        self.sMax = sMax
        self.vMax = vMax
        self.sAdd = sAdd
        self.sSub = sSub
        self.vAdd = vAdd
        self.vSub = vSub


class SnowManFilter(HsvFilter):
    def __init__(self):
        self.hMin = 106
        self.sMin = 0
        self.vMin = 0
        self.hMax = 116
        self.sMax = 90
        self.vMax = 255
        self.sAdd = 0
        self.sSub = 0
        self.vAdd = 255
        self.vSub = 0

class Dang25metin(HsvFilter):
    def __init__(self):
        self.hMin = 16
        self.sMin = 181
        self.vMin = 17
        self.hMax = 66
        self.sMax = 196
        self.vMax = 255
        self.sAdd = 0
        self.sSub = 0
        self.vAdd = 0
        self.vSub = 0

class Metin_45(HsvFilter):
    def __init__(self):
        self.hMin = 6
        self.sMin = 0
        self.vMin = 0
        self.hMax = 188
        self.sMax = 180
        self.vMax = 255
        self.sAdd = 0
        self.sSub = 0
        self.vAdd = 0
        self.vSub = 0

class SnowManFilterRedForest(HsvFilter):
    # Night mode acitve
    def __init__(self):
        self.hMin = 130
        self.sMin = 0
        self.vMin = 0
        self.hMax = 138
        self.sMax = 255
        self.vMax = 255
        self.sAdd = 0
        self.sSub = 0
        self.vAdd = 255
        self.vSub = 0


class MobInfoFilter(HsvFilter):
    def __init__(self):
        self.hMin = 0
        self.sMin = 0
        self.vMin = 140
        self.hMax = 179
        self.sMax = 255
        self.vMax = 255
        self.sAdd = 0
        self.sSub = 0
        self.vAdd = 0
        self.vSub = 0


class Vision:
    TRACKBAR_WINDOW = "Trackbars"

    def __init__(self, needle_img_path=get_metin_needle_path(), method=cv.TM_CCOEFF_NORMED):
        # # # load the image we're trying to match
        # # https://docs.opencv.org/4.2.0/d4/da8/group__imgcodecs.html
        # self.needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)
        
        # # Save the dimensions of the needle image
        # self.needle_w = self.needle_img.shape[1]
        # self.needle_h = self.needle_img.shape[0]
        
        # # There are 6 methods to choose from:
        # # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        # self.method = method
        self.is_diagram_opened = False
        pass

    # create gui window with controls for adjusting arguments in real-time
    def init_control_gui(self):
        cv.namedWindow(self.TRACKBAR_WINDOW, cv.WINDOW_NORMAL)
        cv.resizeWindow(self.TRACKBAR_WINDOW, 350, 700)

        # required callback. we'll be using getTrackbarPos() to do lookups
        # instead of using the callback.
        def nothing(position):
            pass

        # create trackbars for bracketing.
        # OpenCV scale for HSV is H: 0-179, S: 0-255, V: 0-255
        cv.createTrackbar('HMin', self.TRACKBAR_WINDOW, 0, 179, nothing)
        cv.createTrackbar('SMin', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('VMin', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('HMax', self.TRACKBAR_WINDOW, 0, 179, nothing)
        cv.createTrackbar('SMax', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('VMax', self.TRACKBAR_WINDOW, 0, 255, nothing)
        # Set default value for Max HSV trackbars
        cv.setTrackbarPos('HMax', self.TRACKBAR_WINDOW, 179)
        cv.setTrackbarPos('SMax', self.TRACKBAR_WINDOW, 255)
        cv.setTrackbarPos('VMax', self.TRACKBAR_WINDOW, 255)

        # trackbars for increasing/decreasing saturation and value
        cv.createTrackbar('SAdd', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('SSub', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('VAdd', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('VSub', self.TRACKBAR_WINDOW, 0, 255, nothing)

    # returns an HSV filter object based on the control GUI values
    def get_hsv_filter_from_controls(self):
        # Get current positions of all trackbars
        hsv_filter = HsvFilter()
        hsv_filter.hMin = cv.getTrackbarPos('HMin', self.TRACKBAR_WINDOW)
        hsv_filter.sMin = cv.getTrackbarPos('SMin', self.TRACKBAR_WINDOW)
        hsv_filter.vMin = cv.getTrackbarPos('VMin', self.TRACKBAR_WINDOW)
        hsv_filter.hMax = cv.getTrackbarPos('HMax', self.TRACKBAR_WINDOW)
        hsv_filter.sMax = cv.getTrackbarPos('SMax', self.TRACKBAR_WINDOW)
        hsv_filter.vMax = cv.getTrackbarPos('VMax', self.TRACKBAR_WINDOW)
        hsv_filter.sAdd = cv.getTrackbarPos('SAdd', self.TRACKBAR_WINDOW)
        hsv_filter.sSub = cv.getTrackbarPos('SSub', self.TRACKBAR_WINDOW)
        hsv_filter.vAdd = cv.getTrackbarPos('VAdd', self.TRACKBAR_WINDOW)
        hsv_filter.vSub = cv.getTrackbarPos('VSub', self.TRACKBAR_WINDOW)
        return hsv_filter

    # given an image and an HSV filter, apply the filter and return the resulting image.
    # if a filter is not supplied, the control GUI trackbars will be used
    def apply_hsv_filter(self, original_image, hsv_filter=None):
        # convert image to HSV
        hsv = cv.cvtColor(original_image, cv.COLOR_BGR2HSV)

        # if we haven't been given a defined filter, use the filter values from the GUI
        if not hsv_filter:
            hsv_filter = self.get_hsv_filter_from_controls()

        # add/subtract saturation and value
        h, s, v = cv.split(hsv)
        s = self.shift_channel(s, hsv_filter.sAdd)
        s = self.shift_channel(s, -hsv_filter.sSub)
        v = self.shift_channel(v, hsv_filter.vAdd)
        v = self.shift_channel(v, -hsv_filter.vSub)
        hsv = cv.merge([h, s, v])

        # Set minimum and maximum HSV values to display
        lower = np.array([hsv_filter.hMin, hsv_filter.sMin, hsv_filter.vMin])
        upper = np.array([hsv_filter.hMax, hsv_filter.sMax, hsv_filter.vMax])
        # Apply the thresholds
        mask = cv.inRange(hsv, lower, upper)
        result = cv.bitwise_and(hsv, hsv, mask=mask)

        # convert back to BGR for imshow() to display it properly
        img = cv.cvtColor(result, cv.COLOR_HSV2BGR)

        return img

    # apply adjustments to an HSV channel
    # https://stackoverflow.com/questions/49697363/shifting-hsv-pixel-values-in-python-using-numpy
    def shift_channel(self, c, amount):
        if amount > 0:
            lim = 255 - amount
            c[c >= lim] = 255
            c[c < lim] += amount
        elif amount < 0:
            amount = -amount
            lim = amount
            c[c <= lim] = 0
            c[c > lim] -= amount
        return c


    def put_text_on_box(self,img, label, box):
        cv.putText(img, label, (box[0], box[1] - 10),
                                                    cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv.LINE_AA)

    def draw_marker(self, img, position, bgr_color=(0, 255, 0)):
        cv.drawMarker(img, position, color=bgr_color, markerType=cv.MARKER_CROSS, thickness=2)

    def draw_rectangles(self, haystack_img, rectangles, bgr_color=(0, 255, 0)):
        for (x, y, w, h) in rectangles:
            top_left = (x, y)
            bottom_right = (x + w, y + h)
            cv.rectangle(haystack_img, top_left, bottom_right, bgr_color, lineType=cv.LINE_4)

    def draw_rectangle_xmin_ymin_xmax_ymax(self,img, rectangle, color):
        top_left = (int(rectangle[0]), int(rectangle[1]))
        bottom_right = (int(rectangle[2]), int(rectangle[3]))
        color = (255, 0, 0)  # BGR color for bounding box
        cv.rectangle(img, top_left, bottom_right, color, 2)


    def add_rectangles_to_image(self, image, rectangles):
        if len(rectangles > 0):
            image_with_matches = self.draw_rectangles(image, [rectangles[0]], bgr_color=(0, 0, 255))
            if len(rectangles > 1):
                image_with_matches = self.draw_rectangles(image, rectangles[1:])
        return image

    def black_out_area(self, image, top_left, bottom_right):
        cv.rectangle(image, top_left, bottom_right, (0, 0, 0), cv.FILLED)
        # cv.rectangle(image, top_left, bottom_right, (255, 0, 0), cv.LINE_4)

    def extract_section(self, image, top_left, bottom_right):
        
        return image[top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]]

    def template_match(self, screenshot, template):
        needle = cv.imread(template, cv.IMREAD_UNCHANGED)
        result = cv.matchTemplate(screenshot, needle[:, :, :3], cv.TM_CCOEFF_NORMED)
        match_val, _, match_loc, _ = cv.minMaxLoc(result)
        threshold = 0.85
        loc = np.where(result >= threshold)
        
        return loc
        
        

    def template_match_alpha(self, haystack_img, needle_path, max_match_val=100_0000, TM = cv.TM_SQDIFF):
        try:
            needle = cv.imread(needle_path, cv.IMREAD_UNCHANGED)
            result = cv.matchTemplate(haystack_img, needle[:, :, :3], TM, mask=needle[:, :, 3])
            match_val, _, match_loc, _ = cv.minMaxLoc(result)
            if TM == cv.TM_CCOEFF_NORMED:
            
                threshold = 0.5
                loc = np.where(result >= threshold)
                return loc
            if match_val > max_match_val:
                return None, match_val
            else:
                return match_loc, match_val
        except:
            print("image was smaller then needle")

    def find_image(self, live_image, template_path, conf_thresh=0.2, max_centers=1):
        # Load the template
        template = cv.imread(template_path)
        ch, template_w, template_h = template.shape[::-1]

        # Match the template using cv2.matchTemplate
        result = cv.matchTemplate(live_image, template, cv.TM_CCOEFF_NORMED)

        # Threshold the result
        locations = np.where(result >= conf_thresh)
        locations = list(zip(*locations[::-1])) # Swap and pair x, y coordinates

        # Sort locations by their corresponding confidence level
        matches = sorted([(result[y, x], (x, y)) for x, y in locations], key=lambda x: x[0], reverse=True)
        
        # Take up to the top max_centers matches
        top_matches = matches[:max_centers]

        centers = []
        for _, (x, y) in top_matches:
            # Get the coordinates of the center point of the found image
            center_x = x + template_w // 2
            center_y = y + template_h // 2
            self.draw_marker(live_image, (center_x, center_y))
            centers.append((center_x, center_y))

        # Return results based on max_centers
        if max_centers == 1:
            return centers[0] if centers else (None, None)
        else:
            return centers
    
    def is_point_in_rectangle(self, point, rect_top_left, rect_bottom_right):
        """
        Check if the point (x, y) is inside the specified rectangle.

        :param point: Tuple (x, y) representing the point.
        :param rect_top_left: Tuple (x, y) representing the top-left corner of the rectangle.
        :param rect_bottom_right: Tuple (x, y) representing the bottom-right corner of the rectangle.
        :return: True if the point is inside the rectangle, False otherwise.
        """
        x, y = point
        rect_x1, rect_y1 = rect_top_left
        rect_x2, rect_y2 = rect_bottom_right

        return rect_x1 <= x <= rect_x2 and rect_y1 <= y <= rect_y2

    def index_of_centers_that_hasnt_been_clicked_yet(self, centers, clicked_centers, current_inv_tab):
        sorted_centers = sorted(centers, key=lambda center: center[1])
        for index, (center_x, center_y) in enumerate(sorted_centers):
        # Check if this center has been clicked in the current inventory tab
            already_clicked = False
            for clicked_x, clicked_y, inventory in clicked_centers:
                if self.is_point_in_rectangle((center_x, center_y), (clicked_x-12, clicked_y-12), (clicked_x+12, clicked_y+12)) and inventory == current_inv_tab:
                    already_clicked = True
                    break

            if not already_clicked:
                return index  # Return the index of the first unclicked center

        return None  # Return None if all centers have been clicked

            
    
    def in_range(self, left, right, x):
        return left <= x <= right

    def save_results(self,detection_result_rectangle, detection_image, output_image_path, output_txt_path, label_to_index=0):
        # 1. Save the image
        cv.imwrite(output_image_path, detection_image)

        # 2. Create YOLO annotation file
        height, width, _ = detection_image.shape
        with open(output_txt_path, 'w') as f:
            x_center = (detection_result_rectangle[0] + detection_result_rectangle[2] / 2) / width
            y_center = (detection_result_rectangle[1] + detection_result_rectangle[3] / 2) / height
            w = detection_result_rectangle[2] / width
            h = detection_result_rectangle[3] / height
            class_idx = label_to_index
            f.write(f"{class_idx} {x_center} {y_center} {w} {h}\n")
    
    # Function to load image and detect SIFT features
    def detect_features(self, image_path):
        # Read the image
        image = cv.imread(image_path, cv.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError(f"Image at {image_path} could not be loaded.")
        # Detect keypoints and compute the descriptors with SIFT
        keypoints, descriptors = self.sift.detectAndCompute(image, None)
        if descriptors is None:
            raise ValueError(f"No keypoints detected in image at {image_path}.")
        return keypoints, descriptors, image

    # Function to match descriptors between two images
    def match_descriptors(self, descriptors1, descriptors2):
        # Ensure descriptors are valid
        if descriptors1 is None or descriptors2 is None:
            raise ValueError("One or both sets of descriptors are None and cannot be matched.")
        # Create BFMatcher object with default params
        bf = cv.BFMatcher(cv.NORM_L2, crossCheck=True)
        # Match descriptors
        matches = bf.match(descriptors1, descriptors2)
        # Sort them in the order of their distance
        matches = sorted(matches, key=lambda x: x.distance)
        return matches

    def SIFT_FEATURES_DETECTION(self, screenshot):

        self.sift = cv.SIFT_create()
        # Load images and detect features
        keypoints1, descriptors1, image1 = self.detect_features(r'C:\Users\Filip\Downloads\test.png')
        keypoints2, descriptors2 = self.sift.detectAndCompute(cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY), None)
        # Choose a location
        chosen_location = (152, 144) # Replace with your coordinates

        # Compute distances from the chosen location to each keypoint
        distances = [(kp, np.linalg.norm(np.array(kp.pt) - np.array(chosen_location))) for kp in keypoints1]

        # Sort keypoints by distance
        distances.sort(key=lambda x: x[1])

        # Get the indices of the top 100 keypoints
        top_100_indices = [keypoints1.index(kp) for kp, _ in distances[:100]]

        # Extract descriptors for the top 100 keypoints
        top_100_descriptors = descriptors1[top_100_indices, :]

        # Match descriptors if there are keypoints detected
        if top_100_indices:
            matches = self.match_descriptors(top_100_descriptors, descriptors2)
                # Extract locations of matched keypoints in both images
            points2 = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1, 2)

            # Apply DBSCAN clustering
            db = DBSCAN(eps=30, min_samples=5).fit(points2)
            labels = db.labels_
            clustered_matches = []
            # Check if any clusters were found
            if np.any(labels != -1):
                # Calculate the number of occurrences of each label (excluding noise)
                label_counts = np.bincount(labels[labels != -1])
                
                # Find the index of the largest cluster
                largest_cluster_idx = np.argmax(label_counts)

                # Filter the matches based on the largest cluster
                clustered_matches = [m for i, m in enumerate(matches) if labels[i] == largest_cluster_idx]

            # Draw matches if any have been found
            if len(matches) > 0:
                # Draw only the top 100 keypoints
                matched_keypoints = [keypoints2[m.trainIdx].pt for m in clustered_matches]
    
                # Convert keypoints into a form that can be used with drawKeypoints
                matched_keypoints = [cv.KeyPoint(x=pt[0], y=pt[1], size=8) for pt in matched_keypoints]

                imgs = cv.drawKeypoints(screenshot, matched_keypoints, None, flags=cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
                cv.imshow('Top 100 Nearest Feature Matches', imgs)
                # cv.waitKey(0)
                # cv.destroyAllWindows()
            else:
                print("No matches found.")
        else:
            print("No keypoints found near the chosen location.")

    def compare_screenshots(self, img1, img2):
        # Calculate the absolute difference between images
        diff = np.abs(img1.astype('int16') - img2.astype('int16'))
        
        # Calculate the average difference per pixel
        avg_diff = np.mean(diff)
        return avg_diff
