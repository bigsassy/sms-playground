from kidmuseum import TxtConversation, Image
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
curley_mustache = Image("curley mustache")
hipster_sunglasses = Image("sunglasses")

# Paste a mustache and hipster shades on the person's face
# * tell server to add one image onto other image and return updated url
selfie.add_mustache(curley_mustache)
selfie.add_glasses(hipster_sunglasses)

# * tell server to send back updated image to user
conversation.send_picture(selfie)
