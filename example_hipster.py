from kidmuseum import TxtConversation

while True:
    conversation = TxtConversation('hipster')

    conversation.send_message("Welcome to Hipster Face!")

    selfie = conversation.get_picture("Reply with a selfie and see what happens :P")
    selfie.add_mustache("handlebar_mustache")
    selfie.add_sunglasses("sunglasses1")

    conversation.send_picture(selfie)
