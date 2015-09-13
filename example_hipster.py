from kidmuseum import TxtConversation

conversation = TxtConversation('hipster')

conversation.send_message("Welcome to Hipster Face!")

selfie = conversation.get_picture("Reply with a selfie and see what happens :P")
selfie.add_moustache("moustache1")
selfie.add_glasses("sunglasses1")

conversation.send_picture(selfie)
