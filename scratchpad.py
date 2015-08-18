import os
import time
from datetime import datetime, date

from twilio.rest import TwilioRestClient

ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

class Session:

    def __init__(self, users_phone_number):
        self.handled_messages = set()
        self.session_start_time = datetime.utcnow()
        self.users_phone_number = users_phone_number
        self.service_phone_number = "+12407536527"

    def await_response_message(self, timeout=None):
        await_start_time = datetime.utcnow()
        while(True):
            for message in client.messages.list(from_=self.users_phone_number):
                if message.sid not in self.handled_messages and message.date_created >= self.session_start_time:
                    self.handled_messages.add(message.sid)
                    return message.body
            time.sleep(1)
            if timeout and datetime.utcnow() - await_start_time > timeout:
                raise TimeoutError("Too much time passed while waiting for incoming text.")

    def send_message(self, message):
        client.messages.create(
            body=message,
            to=self.users_phone_number,
            from_=self.service_phone_number,
        )

    def get_string(self, prompt_message):
        self.send_message(prompt_message)
        return self.await_response_message()

    def get_integer(self, prompt_message):
        self.send_message(prompt_message)
        return self._get_type(int, "Whole numbers only, please. Try again.")

    def get_floating_point(self, prompt_message):
        self.send_message(prompt_message)
        return self._get_type(float, "Numbers only, please. Try again.")

    def _get_type(self, type_cast_function, invalid_type_message):
        user_response = None
        while (user_response is None):
            response = self.await_response_message()
            try:
                user_response = type_cast_function(response)
            except ValueError:
                self.send_message(invalid_type_message)
        return user_response

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

conversation = TxtConversation('hipster')

# Welcome the user and ask for a selfie image
conversation.send_message("Welcome to Hipster Face!")
selfie = conversation.ask_for_selfie("Reply with a selfie and see what happens :P")

# Get a funny mustache and sunglasses from the kidmuseum image library
curley_mustache = get_image("curley mustache")
hipster_sunglasses = get_image("sunglasses")

# Paste a mustache and hipster shades on the person's face
selfie.add_mustache(curley_mustache)
selfie.add_glasses(hipster_sunglasses)

conversation.send_picture(selfie)
