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

session = Session('+12407789795')
session.send_message("Hello! Welcome to the test box")
name = session.get_string("What's your name?")
age = session.get_integer("Hey, {}. How old are you?".format(name))
birth_year = date.today().year - age
session.send_message("You were born in {}. Goodbye.".format(birth_year))
