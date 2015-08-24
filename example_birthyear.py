from kidmuseum import TxtConversation
from datetime import date

conversation = TxtConversation('birth year')

# Ask for the person's name and age
conversation.send_message("Hi!")
name = conversation.get_string("What's your name?")
age = conversation.get_integer("Hey, {}. How old are you?".format(name))

# Calculate the person's birth year
today = date.today()
birth_year = today.year - age

# Tell the person their birth year
conversation.send_message("You were born in {}.".format(birth_year))
