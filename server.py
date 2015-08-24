import os
import json
import random
from datetime import datetime

from twilio.rest import TwilioRestClient
from flask import Flask, request
import dateutil.parser


ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
twilio = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
app = Flask(__name__)

# Keeps track of which text messages we've already handled
# and shouldn't get processed again
handled_messages = set()

# Maps a conversation code to a user's cell phone number
conversation_to_phone_number = {}


@app.route("/conversation/start", methods=['POST'])
def start_a_conversation():
    response = None

    request_data = request.get_json()
    keyword = request_data['keyword']
    oldest_message_time = dateutil.parser.parse(request_data['messages_must_be_older_than'])

    # Check if any users have sent a text to the server with the keyword used to start the conversation,
    # making sure the message wasn't already handled earlier and isn't from a long time ago
    for message in twilio.messages.list(date_sent=datetime.utcnow().date()):
        if message.sid not in handled_messages and message.date_created >= oldest_message_time:

            # If this message doesn't match our keyword, try the next message
            if message.body.strip().lower() != keyword.strip().lower():
                continue

            # Remember this message so we won't process it a second time later
            handled_messages.add(message.sid)

            # Create a new special code for the conversation
            conversation_code = "%032x" % random.getrandbits(128)

            # Link the new special code to this phone number so any future messages
            # from this phone number will be associated with this conversation.
            conversation_to_phone_number[conversation_code] = message.from_

            # Tell the program to use the special conversation code when it wants
            # to send this user any text messages and get replies
            response = {'conversation_code': conversation_code}

            break

    # if we didn't find any messages that are starting a conversation,
    # tell the program to wait a little bit and check again
    if response is None:
        response = {'wait_for_seconds': 1}

    return json.dumps(response), 200, {'Content-Type': 'application/json'}


@app.route("/conversation/<conversation_code>/message/send", methods=['POST'])
def send_message(conversation_code):
    request_data = request.get_json()
    message = request_data['message']
    picture_url = request_data.get('picture_url', None)

    # Send a new message to the user in the conversation
    if conversation_code in conversation_to_phone_number:
        _send_message(conversation_code, message, picture_url)
        return ""
    else:
        return "No conversation found with specified code", 400


@app.route("/conversation/<conversation_code>/message/response/<expected_response_type>", methods=['POST'])
def get_response_message(conversation_code, expected_response_type):
    response = None

    request_data = request.get_json()
    oldest_message_time = dateutil.parser.parse(request_data['messages_must_be_older_than'])

    # Get a message sent to the sms playground that's for this conversation
    # and hasn't already been handled earlier
    if conversation_code in conversation_to_phone_number:
        users_phone_number = conversation_to_phone_number[conversation_code]
        for message in twilio.messages.list(from_=users_phone_number):
            if message.sid not in handled_messages and message.date_created >= oldest_message_time:

                # Remember this message so we won't process it a second time later
                handled_messages.add(message.sid)

                # Make sure the message sent from the user matches what the program
                # was expecting (e.g. a number or a picture). If it's not, ask the
                # user to send another message that's the correct type

                if expected_response_type == "string":
                    response = {
                        'message': message.body
                    }

                elif expected_response_type == "int":
                    try:
                        response = {
                            'message': int(message.body)
                        }
                    except ValueError:
                        _send_message(conversation_code, "Whole numbers only, please. Try again.")

                elif expected_response_type == "float":
                    try:
                        response = {
                            'message': float(message.body)
                        }
                    except ValueError:
                        _send_message(conversation_code, "Numbers only, please. Try again.")

                elif expected_response_type == "picture":
                    if int(message.num_media) > 0:
                        response = {
                            'url': message.media_list.list()[0].uri
                        }
                    else:
                        _send_message(conversation_code, "Please reply with a picture.")

                break

    # If the user didn't reply to our last message yet,
    # tell the program to wait a little bit and check again
    if response is None:
        response = {'wait_for_seconds': 1}

    return json.dumps(response), 200, {'Content-Type': 'application/json'}


# ----------------------------------------------------------------------------
# Support functions
# ----------------------------------------------------------------------------
def _send_message(conversation_code, message, picture_url=None):
    args = {
        'body': message,
        'to': conversation_to_phone_number[conversation_code],
        'from_': "+12407536527",
    }
    if picture_url:
        args['media_url'] = picture_url
    twilio.messages.create(**args)


if __name__ == '__main__':
    app.run(debug=True)
