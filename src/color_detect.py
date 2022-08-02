# TechVidvan Object detection of similar color

import cv2
import numpy as np
# Import packages
import cv2
import numpy as np

def cropper():
    img = cv2.imread('pre_color_detect.jpg')
    print(img.shape) # Print image shape
    cv2.imshow("original", img)

    cropped_image = img[80:280, 150:330]

    cv2.imshow("cropped", cropped_image)
    cv2.imwrite("pre_color_detect.jpg", cropped_image)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
# Reading the image
def color_detection_function(filename):
    img = cv2.imread(filename)

    #define kernel size  
    kernel = np.ones((7,7),np.uint8)


    # convert to hsv colorspace 
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # lower bound and upper bound for Green color 
    lower_bound = np.array([50,40,50])
    upper_bound = np.array([70,255,255])

    # lower bound and upper bound for Yellow color 
    # lower_bound = np.array([20, 80, 80])     
    # upper_bound = np.array([30, 255, 255])


    # find the colors within the boundaries
    mask = cv2.inRange(hsv, lower_bound, upper_bound)


    # Remove unnecessary noise from mask

    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)



    # Segment only the detected region

    segmented_img = cv2.bitwise_and(img, img, mask=mask)

    # Find contours from the mask

    contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw contour on segmented image
    # output = cv2.drawContours(segmented_img, contours, -1, (0, 0, 255), 3)
    # Draw contour on original image

    output = cv2.drawContours(img, contours, -1, (0, 0, 255), 3)

    cv2.imwrite("/home/pi/Project/images/color_outlined_pic.jpg",segmented_img)