import os
import urllib
import uuid
from urlparse import urlparse

from server import *

# key codes
q_key = 113
up_arrow = 63232
down_arrow = 63233
left_arrow = 63234
right_arrow = 63235

# Get paths to all the bad images
bad_images = [os.path.join("bad_images", i) for i in os.listdir('bad_images') if i != ".DS_Store"]

# Keep track of which image and cascade we're displaying
indexes = [[0, bad_images], [0, moustache_options.keys()], [0, glasses_options.keys()]]
edit_index = 0
edit_index_names = ['image', 'moustache', 'glasses']

def refresh_image(bad_image, moustache_name, glasses_name):
    frame = resize_image(cv2.imread(bad_image))
    face_features = DetectedFace(facepp.File(bad_image), frame)

    add_moustache(frame, face_features, moustache_name)
    add_glasses(frame, face_features, glasses_name)
    add_detected_features(frame, face_features)

    cv2.imshow("Window", frame)

key = None
while key != q_key:
    print "{}: {}, {}".format(
        indexes[0][1][indexes[0][0]],
        indexes[1][1][indexes[1][0]],
        indexes[2][1][indexes[2][0]],
    )
    refresh_image(
        indexes[0][1][indexes[0][0]],
        indexes[1][1][indexes[1][0]],
        indexes[2][1][indexes[2][0]],
    )
    key = cv2.waitKey(0)
    if key == up_arrow:
        edit_index = edit_index - 1 if edit_index > 0 else len(indexes) - 1
        print "Now editing {}".format(edit_index_names[edit_index])
    elif key == down_arrow:
        edit_index = edit_index + 1 if edit_index < len(indexes) - 1 else 0
        print "Now editing {}".format(edit_index_names[edit_index])
    elif key == left_arrow:
        indexes[edit_index][0] = indexes[edit_index][0] - 1 if indexes[edit_index][0] > 0 else len(indexes[edit_index][1]) - 1
    elif key == right_arrow:
        indexes[edit_index][0] = indexes[edit_index][0] + 1 if indexes[edit_index][0] < len(indexes[edit_index][1]) - 1 else 0
