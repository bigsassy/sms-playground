import os
import urllib
import uuid
from urlparse import urlparse

import cv2  # OpenCV Library

#-----------------------------------------------------------------------------
#       Load and configure Haar Cascade Classifiers
#-----------------------------------------------------------------------------
 
# location of OpenCV Haar Cascade Classifiers:
baseCascadePath = "/usr/local/share/OpenCV/haarcascades/"
 
# xml files describing our haar cascade classifiers
faceCascadeFilePath = baseCascadePath + "haarcascade_frontalface_default.xml"
noseCascadeFilePath = baseCascadePath + "haarcascade_mcs_nose.xml"
eyeCascadeFilePath = baseCascadePath + "haarcascade_eye.xml"

# build our cv2 Cascade Classifiers
faceCascade = cv2.CascadeClassifier(faceCascadeFilePath)
noseCascade = cv2.CascadeClassifier(noseCascadeFilePath)
eyeCascade = cv2.CascadeClassifier(eyeCascadeFilePath)

#-----------------------------------------------------------------------------
#       Load and configure mustache (.png with alpha transparency)
#-----------------------------------------------------------------------------

# Load our overlay image: mustache.png
imgMustache = cv2.imread('images/mustaches/handlebar_mustache.png',-1)
 
# Create the mask for the mustache
orig_mask = imgMustache[:,:,3]
 
# Create the inverted mask for the mustache
orig_mask_inv = cv2.bitwise_not(orig_mask)
 
# Convert mustache image to BGR
# and save the original image size (used later when re-sizing the image)
imgMustache = imgMustache[:,:,0:3]
origMustacheHeight, origMustacheWidth = imgMustache.shape[:2]

#-----------------------------------------------------------------------------
#       Load and configure sunglasses (.png with alpha transparency)
#-----------------------------------------------------------------------------

# Load our overlay image: sunglasses.png
imgSunglasses = cv2.imread('images/sunglasses/sunglasses1.png',-1)

# Create the mask for the sunglasses
orig_mask_sg = imgSunglasses[:,:,3]

# Create the inverted mask for the sunglasses
orig_mask_inv_sg = cv2.bitwise_not(orig_mask_sg)

# Convert mustache image to BGR
# and save the original image size (used later when re-sizing the image)
imgSunglasses = imgSunglasses[:,:,0:3]
origSunglassesHeight, origSunglassesWidth = imgSunglasses.shape[:2]

#-----------------------------------------------------------------------------
#       Main program
#-----------------------------------------------------------------------------

url = "https://s3.amazonaws.com/threerides_misc/selfie.jpg"
file_extension = os.path.splitext(urlparse(url).path)[1]
image_path = "images/{}.{}".format(str(uuid.uuid4()).replace("-", ""), file_extension)
urllib.urlretrieve(url, image_path)
frame = cv2.imread(image_path)

original_height, original_width = frame.shape[:2]
if max(original_height, original_width) > 640:
    if original_height > original_width:
        frame = cv2.resize(frame, (int(original_width * (640.0 / original_height)), 640))
    else:
        frame = cv2.resize(frame, (640, int(original_height * (640.0 / original_width))))

# Create greyscale image from the video feed
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# Detect faces in input video stream
faces = faceCascade.detectMultiScale(
    gray,
    scaleFactor=1.1,
    minNeighbors=5,
    minSize=(30, 30),
    flags=cv2.CASCADE_SCALE_IMAGE
)

# Iterate over each face found
for (x, y, w, h) in faces:
    # Un-comment the next line for debug (draw box around all faces)
    #face = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)

    roi_gray = gray[y:y+h, x:x+w]
    roi_color = frame[y:y+h, x:x+w]

    # Detect a nose within the region bounded by each face (the ROI)
    nose = noseCascade.detectMultiScale(roi_gray)

    for (nx,ny,nw,nh) in nose:
        # Un-comment the next line for debug (draw box around the nose)
        #cv2.rectangle(roi_color,(nx,ny),(nx+nw,ny+nh),(255,0,0),2)

        # The mustache should be three times the width of the nose
        mustacheWidth =  3 * nw
        mustacheHeight = mustacheWidth * origMustacheHeight / origMustacheWidth

        # Center the mustache on the bottom of the nose
        x1 = nx - (mustacheWidth/4)
        x2 = nx + nw + (mustacheWidth/4)
        y1 = ny + nh - (mustacheHeight/2)
        y2 = ny + nh + (mustacheHeight/2)

        # Check for clipping
        if x1 < 0:
            x1 = 0
        if y1 < 0:
            y1 = 0
        if x2 > w:
            x2 = w
        if y2 > h:
            y2 = h

        # Re-calculate the width and height of the mustache image
        mustacheWidth = x2 - x1
        mustacheHeight = y2 - y1

        # Re-size the original image and the masks to the mustache sizes
        # calcualted above
        mustache = cv2.resize(imgMustache, (mustacheWidth,mustacheHeight), interpolation = cv2.INTER_AREA)
        mask = cv2.resize(orig_mask, (mustacheWidth,mustacheHeight), interpolation = cv2.INTER_AREA)
        mask_inv = cv2.resize(orig_mask_inv, (mustacheWidth,mustacheHeight), interpolation = cv2.INTER_AREA)

        # take ROI for mustache from background equal to size of mustache image
        roi = roi_color[y1:y2, x1:x2]

        # roi_bg contains the original image only where the mustache is not
        # in the region that is the size of the mustache.
        roi_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)

        # roi_fg contains the image of the mustache only where the mustache is
        roi_fg = cv2.bitwise_and(mustache,mustache,mask = mask)

        # join the roi_bg and roi_fg
        dst = cv2.add(roi_bg,roi_fg)

        # place the joined image, saved to dst back over the original image
        roi_color[y1:y2, x1:x2] = dst

        break

    # Detect the eyes within the region bounded by each face (the ROI)
    eyes = eyeCascade.detectMultiScale(roi_gray)
    if len(eyes) == 2:
        left_eye = eyes[0] if eyes[0][0] < eyes[1][0] else eyes[1]
        right_eye = eyes[0] if eyes[0][0] >= eyes[1][0] else eyes[1]

        ex = left_eye[0]
        ey = min(eyes[0][1], eyes[1][1])
        ew = right_eye[0] + right_eye[2] - ex
        eh = max(left_eye[1] + left_eye[3], right_eye[1] + right_eye[3]) - ey
        #cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)

        # The sunglasses should overlap the eyes a little bit
        sunglassesWidth =  int(ew * 1.3)
        sunglassesHeight = int(origSunglassesHeight * (float(sunglassesWidth) / origSunglassesWidth))

        # Center the sunglasses over the eyes
        x1 = (ex + (ew / 2)) - (sunglassesWidth / 2)
        x2 = x1 + sunglassesWidth
        y1 = ey
        y2 = ey + sunglassesHeight

        # Check for clipping
        if x1 < 0:
            x1 = 0
        if y1 < 0:
            y1 = 0
        if x2 > w:
            x2 = w
        if y2 > h:
            y2 = h

        # Re-calculate the width and height of the mustache image
        sunglassesWidth = x2 - x1
        sunglassesHeight = y2 - y1

        # Re-size the original image and the masks to the mustache sizes
        # calcualted above
        sunglasses = cv2.resize(imgSunglasses, (sunglassesWidth,sunglassesHeight), interpolation = cv2.INTER_AREA)
        mask = cv2.resize(orig_mask_sg, (sunglassesWidth,sunglassesHeight), interpolation = cv2.INTER_AREA)
        mask_inv = cv2.resize(orig_mask_inv_sg, (sunglassesWidth,sunglassesHeight), interpolation = cv2.INTER_AREA)

        # take ROI for mustache from background equal to size of mustache image
        roi = roi_color[y1:y2, x1:x2]

        # roi_bg contains the original image only where the mustache is not
        # in the region that is the size of the mustache.
        roi_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)

        # roi_fg contains the image of the mustache only where the mustache is
        roi_fg = cv2.bitwise_and(sunglasses,sunglasses,mask = mask)

        # join the roi_bg and roi_fg
        dst = cv2.add(roi_bg,roi_fg)

        # place the joined image, saved to dst back over the original image
        roi_color[y1:y2, x1:x2] = dst

# Display the resulting frame
cv2.imwrite('images/hipstafied.jpg', frame)
