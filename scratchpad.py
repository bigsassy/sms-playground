import os
import time
from datetime import datetime, date

from twilio.rest import TwilioRestClient

def hello_world():
    session = Session('+12407789795')
    session.send_message("Hello! Welcome to the test box")
    name = session.get_string("What's your name?")
    age = session.get_integer("Hey, {}. How old are you?".format(name))
    birth_year = date.today().year - age
    session.send_message("You were born in {}. Goodbye.".format(birth_year))

def digital_face_painting():
    session = Session('+12407789795')
    selfie = session.get_selfie("Hello! Welcome to hipster face! Reply with a selfie and see what happens :)")

    star = images.get_image("star")
    tribal = image.get_image("tribal")

    selfie.left_cheek.paste(star)
    selfie.right_side_of_face.paste(tribal)

    session.send_picture(selfie)

def hipster_face():
    session = Session('+12407789795')
    selfie = session.get_picture("Hello! Welcome to hipster face! Reply with a selfie and see what happens :)")

    mustache = images.get_image("mustache")
    sunglasses = images.get_image("sunglasses")

    selfie.mustache.paste(mustache)
    selfie.glasses.paste(sunglasses)

    session.send_picture(selfie)


from kidmuseum import TxtConversation
from datetime import date

conversation = TxtConversation('birth year')

# Ask for the person's name and age
conversation.send_message("Hi!")
name = conversation.get_string("What's your name?")
age = conversation.get_integer("Hey, {}. How old are you?".format(name))

# Calculate the person's birth year
birth_year = date.today().year - age

# Tell the person their birth year
conversation.send_message("You were born in {}.".format(birth_year))


from kidmuseum import TxtConversation, get_image
from datetime import date

# * poll the server for someone to text hipster to start the conversation
# * server eventually responds hash used to converse with user (i.e. phone number)
conversation = TxtConversation('hipster')

# Welcome the user and ask for a selfie image
# * tell server to send message for user (via hash)
# * tell server to send a message for user and return url for MMS sent back
# * package url into image object and return it
conversation.send_message("Welcome to Hipster Face!")
selfie = conversation.ask_for_selfie("Reply with a selfie and see what happens :P")

# Get a funny mustache and sunglasses from the kidmuseum image library
# * package url into image object and return it
curley_mustache = get_image("curley mustache")
hipster_sunglasses = get_image("sunglasses")

# Paste a mustache and hipster shades on the person's face
# * tell server to add one image onto other image and return updated url
selfie.add_mustache(curley_mustache)
selfie.add_glasses(hipster_sunglasses)

# * tell server to send back updated image to user
conversation.send_picture(selfie)
