import os
import urllib2
import uuid
import cgi
from urlparse import urlparse

import cv2


#-----------------------------------------------------------------------------
# Configure Haar Cascade Classifiers
#-----------------------------------------------------------------------------

# location of OpenCV Haar Cascade Classifiers:
baseCascadePath = "./cascades/"

# xml files describing our haar cascade classifiers
faceCascadeFilePath = baseCascadePath + "haarcascade_frontalface_default.xml"
noseCascadeFilePath = baseCascadePath + "haarcascade_mcs_nose.xml"
eyeCascadeFilePath = baseCascadePath + "haarcascade_eye.xml"

# build our cv2 Cascade Classifiers
faceCascade = cv2.CascadeClassifier(faceCascadeFilePath)
noseCascade = cv2.CascadeClassifier(noseCascadeFilePath)
eyeCascade = cv2.CascadeClassifier(eyeCascadeFilePath)


#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

def get_image(url):
    image_path = None
    try:
        # Download the image to the server's hard drive and load it so we can manipulate it
        request = urllib2.Request(url, headers={ 'User-Agent': 'Mozilla/5.0' })
        response = urllib2.urlopen(request)
        if 'content-disposition' in response.headers and 'filename=' in response.headers['content-disposition']:
            file_name = cgi.parse_header(response.headers['content-disposition'])[1]['filename']
            file_extension = os.path.splitext(file_name)[1]
        elif 'content-type' in response.headers:
            file_extension = response.headers['content-type'].split("/")[1]
        else:
            file_extension = os.path.splitext(urlparse(url).path)[1]
        image_path = "images/{}{}".format(str(uuid.uuid4()).replace("-", ""), file_extension)
        with open(image_path, "w") as saved_image:
            print url
            saved_image.write(response.read())
        image = cv2.imread(image_path)

        # Make sure the image is a small enough size for the detection algoritms
        # to work with an acceptable accuracy
        original_height, original_width = image.shape[:2]
        if max(original_height, original_width) > 640:
            if original_height > original_width:
                image = cv2.resize(image, (int(original_width * (640.0 / original_height)), 640))
            else:
                image = cv2.resize(image, (640, int(original_height * (640.0 / original_width))))
    finally:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)

    return image


def transform_image(image, transform_info):
    # Get a greyscale version of the image to help with calculations
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect the position of a face in the image
    faces_found = faceCascade.detectMultiScale(
        grayscale_image,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # Detect the eyes and nose if we found a face in the image
    if len(faces_found) > 0:
        face_xywh = x, y, w, h = faces_found[0]
        face_gray = grayscale_image[y:y+h, x:x+w]
        face_color = image[y:y+h, x:x+w]

        nose_xywh = None
        noses_found = noseCascade.detectMultiScale(face_gray)
        if len(noses_found) > 0:
            nose_xywh = noses_found[0]

        eyes_xywh = None
        eyes = eyeCascade.detectMultiScale(face_gray)
        if len(eyes) == 2:
            # Bounding boxes for each eye
            left_eye_xywh = eyes[0] if eyes[0][0] < eyes[1][0] else eyes[1]
            right_eye_xywh = eyes[0] if eyes[0][0] >= eyes[1][0] else eyes[1]

            # Bounding box for both eyes
            eyes_xywh = (
                left_eye_xywh[0],
                min(eyes[0][1], eyes[1][1]),
                right_eye_xywh[0] + right_eye_xywh[2] - left_eye_xywh[0],
                max(left_eye_xywh[1] + left_eye_xywh[3], right_eye_xywh[1] + right_eye_xywh[3]) - min(left_eye_xywh[1], right_eye_xywh[1])
            )

        # Apply transforms for the face
        if transform_info['mustache'] and nose_xywh is not None:
            add_mustache(face_color, face_xywh, nose_xywh, transform_info['mustache'])

        if transform_info['sunglasses'] and eyes_xywh is not None:
            add_sunglasses(face_color, face_xywh, eyes_xywh, transform_info['sunglasses'])


def add_mustache(image, face_xywh, nose_xywh, mustache_name):
    x, y, w, h = face_xywh
    nx, ny, nw, nh = nose_xywh

    # Load the mustache image we're adding to the image
    imgMustache = cv2.imread('images/mustaches/{}.png'.format(mustache_name), -1)

    # Create the mask for the mustache
    orig_mask = imgMustache[:,:,3]

    # Create the inverted mask for the mustache
    orig_mask_inv = cv2.bitwise_not(orig_mask)

    # Convert mustache image to BGR
    # and save the original image size (used later when re-sizing the image)
    imgMustache = imgMustache[:,:,0:3]
    origMustacheHeight, origMustacheWidth = imgMustache.shape[:2]

    # The mustache should be three times the width of the nose
    mustacheWidth =  int(2 * nw)
    mustacheHeight = int(origMustacheHeight * (float(mustacheWidth) / origMustacheWidth))

    # Center the mustache on the bottom of the nose
    x1 = (nx + (nw / 2)) - (mustacheWidth / 2)
    x2 = x1 + mustacheWidth
    y1 = ny + (nh / 2)
    y2 = y1 + mustacheHeight

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
    roi = image[y1:y2, x1:x2]

    # roi_bg contains the original image only where the mustache is not
    # in the region that is the size of the mustache.
    roi_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)

    # roi_fg contains the image of the mustache only where the mustache is
    roi_fg = cv2.bitwise_and(mustache,mustache,mask = mask)

    # join the roi_bg and roi_fg
    dst = cv2.add(roi_bg,roi_fg)

    # place the joined image, saved to dst back over the original image
    image[y1:y2, x1:x2] = dst


def add_sunglasses(image, face_xywh, eyes_xywh, sunglasses_name):
    x, y, w, h = face_xywh
    ex, ey, ew, eh = eyes_xywh

    # Load our overlay image: sunglasses.png
    imgSunglasses = cv2.imread('images/sunglasses/{}.png'.format(sunglasses_name), -1)

    # Create the mask for the sunglasses
    orig_mask_sg = imgSunglasses[:,:,3]

    # Create the inverted mask for the sunglasses
    orig_mask_inv_sg = cv2.bitwise_not(orig_mask_sg)

    # Convert mustache image to BGR
    # and save the original image size (used later when re-sizing the image)
    imgSunglasses = imgSunglasses[:,:,0:3]
    origSunglassesHeight, origSunglassesWidth = imgSunglasses.shape[:2]

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

    # Re-calculate the width and height of the sunglasses image
    sunglassesWidth = x2 - x1
    sunglassesHeight = y2 - y1

    # Re-size the original image and the masks to the sunglasses sizes
    # calcualted above
    sunglasses = cv2.resize(imgSunglasses, (sunglassesWidth,sunglassesHeight), interpolation = cv2.INTER_AREA)
    mask = cv2.resize(orig_mask_sg, (sunglassesWidth,sunglassesHeight), interpolation = cv2.INTER_AREA)
    mask_inv = cv2.resize(orig_mask_inv_sg, (sunglassesWidth,sunglassesHeight), interpolation = cv2.INTER_AREA)

    # take ROI for mustache from background equal to size of sunglasses image
    roi = image[y1:y2, x1:x2]

    # roi_bg contains the original image only where the sunglasses is not
    # in the region that is the size of the mustache.
    roi_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)

    # roi_fg contains the image of the mustache only where the sunglasses is
    roi_fg = cv2.bitwise_and(sunglasses,sunglasses,mask = mask)

    # join the roi_bg and roi_fg
    dst = cv2.add(roi_bg,roi_fg)

    # place the joined image, saved to dst back over the original image
    image[y1:y2, x1:x2] = dst
