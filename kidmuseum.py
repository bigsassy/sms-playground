from datetime import datetime
import time
try:
    from urllib2 import Request, urlopen, HTTPError
except:
    from urllib.request import Request, urlopen, HTTPError
import json


start_conversation_url = "http://sms-playground.com/conversation/start"
send_message_url = "http://sms-playground.com/conversation/{}/message/send"
get_response_message_url = "http://sms-playground.com/conversation/{}/message/response/{}"
add_to_picture_url = "http://sms-playground.com/conversation/{}/picture/{}/{}"
get_transformed_picture_url = "http://sms-playground.com/conversation/{}/picture/{}/"


class TxtConversation(object):
    """
    A TxtConversation manages a text conversation between a person txting you and your program.
    It comes with a bunch of useful methods that help you communicate with the person texting
    your program, in particular sending messages and getting information from the user of your
    program.

    It also handles registering your program with the Texting Playground.  This allows people to
    pick your program to chat with by sending a txt with the name of your program.

    Here's a simple example of what a program could look like:

        from kidmuseum import TxtConversation

        conversation = TxtConversation("I <3 compliments")
        converstaion.send_message("Hi! You love compliments?  Well I got tons of 'em!")

        name = converstaion.get_string("First, what's your name?")

        conversation.send_message("Hey, " + name + " is an awesome name!")
        conversation.send_message("I bet you're super smart too.")
        conversation.send_message("To be honest, you're the coolest person I've talked today BY FAR :D")
        converstaion.send_message("Gotta go, ttyl!")

    Now, let's pretend the phone number for the SMS Playground was 240-555-0033.  Here's what the
    conversation would look like If someone texted I <3 compliments to that number.

        Person:   I <3 compliments
        Program:  Hi! You love compliments?  Well I got tons of 'em!
        Program:  First, what's your name?
        Person:   Sarah
        Program:  Hey, Sarah is an awesome name!
        Program:  I bet you're super smart too.
        Program:  To be honest, you're the coolest person I've talked today BY FAR :D
        Program:  Gotta go, ttyl!
    """

    def __init__(self, keyword):
        """
        This is the code that get's called when you create the conversation.

        Example:

        conversation = TxtConversation("I <3 compliments")

        :param keyword: What someone would text to start this conversation (e.g. "I <3 compliments")
        """
        timeout_seconds = 120
        start_time = datetime.utcnow()

        while (True):
            # Ask the server to start a conversation with someone
            # who texts the keyword to the Texting Playground's phone number
            request = Request(start_conversation_url, json.dumps({
                'keyword': keyword,
                'messages_must_be_older_than': str(start_time),
            }).encode('utf-8'), {'Content-Type': 'application/json'})
            response_data = json.loads(urlopen(request).read().decode('utf8'))

            # If nobody has texted our keyword to the Texting Playgroud yet,
            # wait a bit and check again.  If it's been a really long time,
            # stop waiting and stop the program.
            if 'wait_for_seconds' in response_data:
                time.sleep(response_data['wait_for_seconds'])
                if (datetime.utcnow() - start_time).seconds >= timeout_seconds:
                    raise Exception("Too much time passed while waiting for text with {}.".format(keyword))
                continue

            # return the special conversation code used to communicated with
            # the user who started the conversation
            self.conversation_code = response_data['conversation_code']
            break

    def send_message(self, message):
        """
        Send a message to the user's phone.

        Example:

        converstaion.send_message("Hi! You love compliments?  Well I got tons of 'em!")

        :param message: The message sent to the user's phone.
        """
        self._send_message(message)

    def send_picture(self, picture_or_url, message=""):
        """
        Send a message to the user's phone.

        Examples:

        converstaion.send_picture("http://dreamatico.com/data_images/kitten/kitten-2.jpg", "It's a kitten!")
        converstaion.send_picture("http://dreamatico.com/data_images/kitten/kitten-7.jpg")

        picture = conversation.get_picture("Gimme your best selfie")
        picture.add_glasses("kanye_shades")
        conversation.send_picture(picture, "You with Kanye Shades")

        :param picture_or_url: Either a Picture object or a url to an image.
        :param message: Optional message to send along with the picture
        """
        url = picture_or_url
        if type(picture_or_url) is Picture:
            url = picture_or_url._get_url()
        self._send_message(message, picture_url=url)

    def get_string(self, prompt_message):
        """
        Asks the user to reply with a message and returns it as a string.

        Examples:

        name = conversation.get_string("What's your name?")
        conversation.send_message("Hi, " + name)

        :param prompt_message: The message to send to the user, prompting for a response.
        :return: The message sent by the user in reply as a string.
        """
        self.send_message(prompt_message)
        return self._get_response_message("string")

    def get_integer(self, prompt_message):
        """
        Asks the user to reply with a message and returns it as a string.

        Examples:

        age = conversation.get_integer("What's your age?")
        age_after_ten_years = age + 10
        conversation.send_message("In 10 years you'll be " + age_after_ten_years)

        :param prompt_message: The message to send to the user, prompting for a response.
        :return: The message sent by the user in reply as an integer.
        """
        self.send_message(prompt_message)
        return self._get_response_message("int")

    def get_floating_point(self, prompt_message):
        """
        Asks the user to reply with a message and returns it as a string.

        Examples:

        price = conversation.get_floating_point("How much was the bill?")
        tip = price * 1.20  # tip 20%
        conversation.send_message("You should tip " + tip)

        :param prompt_message: The message to send to the user, prompting for a response.
        :return: The message sent by the user in reply as an float.
        """
        self.send_message(prompt_message)
        return self._get_response_message("float")

    def get_picture(self, prompt_message):
        """
        Asks the user to reply with a picture and returns it as a Picture object.

        Examples:

        picture = conversation.get_picture("Gimme your best selfie")
        picture.add_glasses("kanye_shades")
        conversation.send_picture(picture, "You with Kanye Shades")

        :param prompt_message: The message to send to the user, prompting for a response.
        :return: The picture sent by the user in reply as a Picture object.
        """
        self.send_message(prompt_message)
        picture_code = self._get_response_message("picture")
        return Picture(self.conversation_code, picture_code)

    def _send_message(self, message, picture_url=None):
        """
        Handles asking the SMS Playground server to send a message to the user
        in this conversation.  This is used by the `send_message` and `send_picture`
        methods.

        :param message: The message getting sent to the user
        :param picture_url: Optionally, a url to the image getting sent to the user.
        """
        request = Request(send_message_url.format(self.conversation_code), json.dumps({
            'message': message,
            'picture_url': picture_url,
        }).encode('utf-8'), {'Content-Type': 'application/json'})
        response = urlopen(request)

        # If the server told us something was wrong with our request, stop the program
        if response.getcode() != 200:
            raise Exception("Failed to send message: {}".format(response.read()))

    def _get_response_message(self, response_type):
        """
        Handles asking the SMS Playground server for the user's response to our previous message
        sent in the conversation.  This is used by the `get_string`, `get_integer`, `get_float` and
        `get_picture` methods.

        :param message: The message getting sent to the user
        :param picture_url: Optionally, a url to the image getting sent to the user.
        """
        timeout_seconds = 120
        start_time = datetime.utcnow()

        while (True):
            # Ask the server for the message the user sent to respond
            # to our last message sent to them
            url = get_response_message_url.format(self.conversation_code, response_type)
            request = Request(url, json.dumps({
                'messages_must_be_older_than': str(start_time),
            }).encode('utf-8'), {'Content-Type': 'application/json'})
            response_data = json.loads(urlopen(request).read().decode('utf8'))

            # If the user hasn't responded yet, wait a bit and check again.
            # If it's been a really long time, stop waiting and stop the program.
            if 'wait_for_seconds' in response_data:
                time.sleep(response_data['wait_for_seconds'])
                if (datetime.utcnow() - start_time).seconds >= timeout_seconds:
                    raise Exception("Too much time passed while waiting for a response")
                continue

            # return the special conversation code used to communicated with
            # the user who started the conversation
            if response_type == "picture":
                return response_data['picture_code']
            else:
                return response_data['message']


class Picture(object):
    """
    A Picture represents a picture send by the user in a text conversation.  It provides method's
    for manipulating the picture, for example adding sunglasses if there's a face in the picture.
    Picture objects can be sent back to the user's phone by using the `send_picture` method
    in a TxtConversation object.

    Here's a simple example of what a program could look like:

        from kidmuseum import TxtConversation

        conversation = TxtConversation("Hipster")
        selfie_picture = converstaion.get_picture("Hi! Send me a selfie, and I'll send you back a hipster!")

        selfie_picture.add_moustache("moustache1")
        selfie_picture.add_glasses("glasses1")

        conversation.send_picture(selfie_picture)

    Now, let's pretend the phone number for the SMS Playground was 240-555-0033.  Here's what the
    conversation would look like If someone texted I <3 compliments to that number.

        Person:   Hipster
        Program:  Hi! Send me a selfie, and I'll send you back a hipster!
        Person:  <takes selfie with camera and sends it>
        Program:  <replies with selfie, only with hipster sunglasses and moustache pasted on>
    """
    def __init__(self, conversation_code, picture_code):
        self.conversation_code = conversation_code
        self.picture_code = picture_code

    def add_moustache(self, moustache_name):
        """
        Adds a moustache to the image if there's a face on it.  Valid moustaches are "moustache1", "moustache2",
        "moustache3", "moustache4", "moustache5", "moustache6", and "moustache7".

        :param moustache_name: The name of the moustache. See list of valid moustache above.
        """
        # Tell the server to send a text message to the user in the conversation
        request = Request(add_to_picture_url.format(self.conversation_code, self.picture_code, "moustache"), json.dumps({
            'moustache_name': moustache_name,
        }).encode('utf-8'), {'Content-Type': 'application/json'})

        try:
            urlopen(request)
        except HTTPError as error:
            # If the server told us something was wrong with our request, stop the program
            raise Exception("Failed to add a moustsache: {}".format(error.read()))

    def add_glasses(self, glasses_name):
        """
        Adds glasses to the image if there's a face on it.  Valid glasses are "glasses1", "glasses2",
        "glasses3", "glasses4", and "glasses5".

        :param moustache_name: The name of the glasses. See list of valid glasses above.
        """
        # Tell the server to send a text message to the user in the conversation
        request = Request(add_to_picture_url.format(self.conversation_code, self.picture_code, "glasses"), json.dumps({
            'glasses_name': glasses_name,
        }).encode('utf-8'), {'Content-Type': 'application/json'})

        try:
            urlopen(request)
        except HTTPError as error:
            # If the server told us something was wrong with our request, stop the program
            raise Exception("Failed to add glasses: {}".format(error.read()))

    def _get_url(self):
        """
        Asks the server for the URL for the picture with all the modifications defined (glasses, moustache, etc).
        :return: The URL for the modified picture.
        """
        request = Request(get_transformed_picture_url.format(self.conversation_code, self.picture_code))
        response_data = json.loads(urlopen(request).read().decode('utf8'))
        return response_data['url']
