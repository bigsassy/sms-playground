import cv2
from images import get_image, transform_image

picture = {
    'url': "https://s3.amazonaws.com/threerides_misc/selfie.jpg",
    'mustache': "handlebar_mustache",
    'sunglasses': "sunglasses1",
    'lefteye': None,
    'righteye': None,
    'leftcheek': None,
    'rightcheeck': None,
}

image = get_image(picture['url'])
transform_image(image, picture)

cv2.imwrite('images/hipstafied.jpg', image)
