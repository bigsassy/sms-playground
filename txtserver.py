import os
import json
import random
import sqlite3
from datetime import date, datetime

from twilio.rest import TwilioRestClient
from flask import Flask, request, g, app
import dateutil.parser

ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
twilio = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
app = Flask(__name__)

# Keeps track of which text messages we've already handled
# and shouldn't get processed again
handled_messages = set()

# Maps a conversation code to a user's cell phone number
# and the start time of the conversation
conversation_to_phone_number = {}


@app.route("/conversation/start/")
def start_a_conversation():
    response = {'conversation_code': None}

    request_data = request.get_json()
    keyword = request_data['keyword'].strip().lower()
    oldest_message_time = dateutil.parser.parse(request_data['oldest_message_time'])

    # Check if any users have sent a text to the server with the keyword used to start the conversation,
    # making sure the message wasn't already handled earlier and isn't from a long time ago
    for message in twilio.messages.list(date_sent=date.today()):
        if message.sid not in handled_messages and message.date_created >= oldest_message_time:

            # Remember this message so we won't process it a second time later
            handled_messages.add(message.sid)

            # Create a new special code for the conversation
            conversation_code = "%032x" % random.getrandbits(128)

            # Link the new special code to this phone number so any future messages
            # from this phone number will be associated with this conversation.
            # Also store the time this conversation started so we can later ignore any messages that
            # were sent to the server before we started this conversation.
            conversation_to_phone_number[conversation_code] = (message._from, datetime.now())

            # Tell the program to use the special conversation code when it wants
            # to send this user any text messages and get replies
            response['conversation_code'] = conversation_code

            break

    return json.dumps(response), 200, {'Content-Type': 'application/json'}


@app.route("/conversation/<int:conversation_code>/message/send")
def send_message(self, conversation_code):
    request_data = request.get_json()
    message = request_data['message']
    picture_url = request_data.get('picture_url', None)

    # Send a new message to the user in the conversation
    if conversation_code in conversation_to_phone_number:
        args = {
            'body': message,
            'to': conversation_to_phone_number[conversation_code][0],
            'from_': "+12407536527",
        }
        if picture_url:
            args['media_url'] = picture_url
        twilio.messages.create(**args)
        return ""
    else:
        return "No conversation found with specified code", 400


@app.route("/conversation/<int:conversation_code>/message/response/<expected_response_type>")
def get_response_message(self, conversation_code, expected_response_type):
    # If a valid message hasn't been sent yet, tell the program to check
    response = {"wait_for_seconds": 1}

    # Get a message sent to the sms playground that's for this conversation
    # and hasn't already been handled earlier
    if conversation_code in conversation_to_phone_number:
        conversation_start_time = conversation_to_phone_number[conversation_code][1]
        for message in twilio.messages.list(from_=self.users_phone_number):
            if message.sid not in self.handled_messages and message.date_created >= conversation_start_time:

                # Remember this message so we won't process it a second time later
                handled_messages.add(message.sid)

                # Make sure the message sent from the user matches what the program
                # was expecting (e.g. a number or a picture). If it's not, ask the
                # user to send another message that's the correct type

                if expected_response_type == "str":
                    response = {
                        'message': message.body
                    }

                elif expected_response_type == "int":
                    try:
                        response = {
                            'message': int(message.body)
                        }
                    except ValueError:
                        send_message("Whoops! I need a whole number here, like 2 or 47.")

                elif expected_response_type == "float":
                    try:
                        response = {
                            'message': int(message.body)
                        }
                    except ValueError:
                        send_message("Whoops! I need a number here, like 5 or 21.5.")

                elif expected_response_type == "picture":
                    if message.num_media > 0:
                        response = {
                            'url': message.media_list.list()[0].uri
                        }
                    else:
                        send_message("Whoops! I need a picture. Can you snap one with camera and reply with that?")

                break

    return json.dumps(response), 200, {'Content-Type': 'application/json'}
