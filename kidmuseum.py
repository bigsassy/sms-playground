from datetime import datetime
import time


timeout = 120 # seconds, i.e. 2 minutes


class TimeoutError(Exception):
    """Thrown when the program has waited too long for something to happen."""
    pass


class SmsPlayground(object):

    def __init__(self):
        pass

    def register_conversation(self, timeout=None):
        start = datetime.utcnow()
        while (True):
            for message in client.messages.list():
                if message.sid not in self.handled_messages and message.date_created >= self.session_start_time:
                    self.handled_messages.add(message.sid)
                    return message.body
            time.sleep(1)
            if timeout and datetime.utcnow() - start - timeout:
                raise TimeoutError("Too much time passed while waiting for incoming text.")

    def _get_messages(self, session_start_time):
        messages = []
        for message in client.messages.list():
            if message.sid not in self.handled_messages and message.date_created >= self.session_start_time:
                self.handled_messages.add(message.sid)
                return message.body

    def _wait_for_response(self, timeout=None):
        await_start_time = datetime.utcnow()
        while(True):
            for message in client.messages.list(from_=self.users_phone_number):
                if message.sid not in self.handled_messages and message.date_created >= self.session_start_time:
                    self.handled_messages.add(message.sid)
                    return message.body
            time.sleep(1)
            if timeout and datetime.utcnow() - await_start_time > timeout:
                raise TimeoutError("Too much time passed while waiting for incoming text.")

class TxtConversation(object):
    """
    A TxtConversation manages a text conversation between a person txting you and your program.
    It comes with a bunch of useful functions that help you communicate with the person txting
    your program, in particular sending messages and getting information from the user of your
    program.

    It also handles registering your program with the SMS Playground.  This allows people to
    pick your program to chat with by sending a txt with the name of your program.

    Here's a simple example of what a program could look like:

        from kidmuseum import TxtConversation

        conversation = TxtConversation("I <3 compliments")
        converstaion.send_message("Hi! You love compliments?  Well I got tons of 'em!")

        name = converstaion.get_string("First, what's your name?")

        conversation.send_message("Hey, " + name + " is an awesome name!")
        conversation.send_message("I bet you're super smart too.")
        conversation.send_message("To be honest, you're the coolest person to talk to me all day today :D")
        converstaion.send_message("Gotta go, ttyl!")

    Now, let's pretend the phone number for the SMS Playground was 240-555-0033.  Here's what the
    conversation would look like If someone texted I <3 compliments to that number.

        Person:   I <3 compliments
        Program:  Hi! You love compliments?  Well I got tons of 'em!
        Program:  First, what's your name?
        Person:   Sarah
        Program:  Hey, Sarah is an awesome name!
        Program:  I bet you're super smart too.
        Program:  To be honest, you're the coolest person to talk to me all day today :D
        Program:  Gotta go, ttyl!
    """

    def __init__(self, start_message):
        """
        This is the code that get's called when you create the conversation.  In the example above,
        the code would be: TxtConversation("I <3 compliments").

        :param start_message: What someone would txt to start this conversation.
        :param timeout: How long to wait for someone to text a number until we give up and stop the program
        """
        self.handled_messages = set()
        self.session_start_time = datetime.utcnow()
        self.users_phone_number = users_phone_number
        self.service_phone_number = "+12407536527"

        # Tell the playground any messages sent with out start_message
        # should be reserved for our program.
        self.playground = SmsPlayground()
        self.playground.register_conversation(start_message)

        # Wait for someone to text our start_message before we
        # start our program


    def _wait_for_response(self, timeout=None):
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
        self.playground.send_message(prompt_message)
        return self.playground.wait_for_response_message()

    def get_integer(self, prompt_message):
        self.playground.send_message(prompt_message)
        return self.wait_for_response(int, "Whole numbers only, please. Try again.")

    def get_floating_point(self, prompt_message):
        self.send_message(prompt_message)
        return self.wait_for_response(float, "Numbers only, please. Try again.")

    def _get_type(self, type_cast_function, invalid_type_message):
        user_response = None
        while (user_response is None):
            response = self.playground.wait_for_response()
            try:
                user_response = type_cast_function(response)
            except ValueError:
                self.playground.send_message(invalid_type_message)
        return user_response
