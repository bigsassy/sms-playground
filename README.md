# SMS Playground
Server and client for letting users easily make quick and fun SMS/MMS programs.

## How to create a program for SMS Playground
1. Install python 2.7+ or python 3.4+ if it isn't already installed. If you're on a Mac or Linux,
   it'll already by installed on your computer. If you're on Windows, try the following:
  1.
   you can download Python at
   https://www.python.org/downloads/.
1. Download the kidmuseum.py into a directory on your computer.  [You can get it here.](http://sms-playground.com/kid_museum.py)
1. Fire up your favorite text editor, like [Notepad++](https://notepad-plus-plus.org/) or
   [Sublime Text](http://www.sublimetext.com/) and start a new file.
1. Use the guide below to write a program.  I'd recommend copying one of the examples as a starting point.
1. Save the file with the .py extension (e.g. myprogram.py) in the same directory as kidmuseum.py.
1. Run your program. On windows you should be able to double click the file to run it.

## Quick Guide to using kidmuseum.py

All programs should start by importing the `TxtConversation` class from the `kidmuseum` module.
```python
from kidmuseum import TxtConversation
```
You can then create a `TxtConversation` object, which tells the SMS Playground to wait for someone to text
a certain phrase.  Once they do, the `TxtConversation` object will get created, ready for you to start sending messages.
You can create a `TxtConversation` like this:
```python
conversation = TxtConversation("kittens")
```
In the code above, the variable `conversation` will get set to your `TxtConversation` object once someone texts
`kittens` to the SMS Playground phone number.  That `conversation` variable will have a few methods you can call
from it.

#### send_message
Sends a message to the user's phone.
```python
conversation.send_message("Hi!  How are you?")
```
#### send_picture
Sends an image with either a URL or a Picture object to the user's phone.
```python
converstaion.send_picture("http://dreamatico.com/data_images/kitten/kitten-2.jpg", "It's a kitten!")
converstaion.send_picture("http://dreamatico.com/data_images/kitten/kitten-7.jpg")
```
#### get_string
Sends a message to the user asking for a response, and then returns the user's response as a string.
```python
name = conversation.get_string("What's your name?")
conversation.send_message("Hi, " + name)
```
#### get_integer
Sends a message to the user asking for a response, and then returns the user's response as an integer.
```python
age = conversation.get_integer("What's your age?")
age_after_ten_years = age + 10
conversation.send_message("In 10 years you'll be " + age_after_ten_years)
```
#### get_floating_point
Sends a message to the user asking for a response, and then returns the user's response as an integer.
```python
price = conversation.get_floating_point("How much was the bill?")
tip = price * 1.20  # tip 20%
conversation.send_message("You should tip " + tip)
```
#### get_picture
Sends a message to the user asking for a response, and then returns the user's response as an integer.
```python
picture = conversation.get_picture("Gimme your best selfie")
picture.add_glasses("kanye_shades")
conversation.send_picture(picture, "You with Kanye Shades")
```
The `get_picture` returns a Picture object.  These objects have a few methods of their own that allow
you to add things to the picture and then send it back to the user's phone using the `send_picture`
method above.

#### add_glasses
Adds glasses to the picture if there's a face in it.  You can pass in any of the following as a string:

`shades` | `aviators` | `kanye`
-------- | ---------- | -------
![shades](https://s3.amazonaws.com/sms-playground/readme_images/shades_rm.png) | ![aviators](https://s3.amazonaws.com/sms-playground/readme_images/aviators_rm.png) | ![kanye](https://s3.amazonaws.com/sms-playground/readme_images/kanye_rm.png)
`glasses` | `rectangle_glasses`
--------- | -------------------
![glasses](https://s3.amazonaws.com/sms-playground/readme_images/glasses_rm.png) | ![rectangle_glasses](https://s3.amazonaws.com/sms-playground/readme_images/rectangle_glasses_rm.png)

## Example programs:

### I <3 Compliments
```python
from kidmuseum import TxtConversation

conversation = TxtConversation("I <3 compliments")
converstaion.send_message("Hi! You love compliments?  Well I got tons of 'em!")
name = converstaion.get_string("First, what's your name?")

conversation.send_message("Hey, " + name + " is an awesome name!")
conversation.send_message("I bet you're super smart too.")
conversation.send_message("To be honest, you're the coolest person I've talked today BY FAR :D")
converstaion.send_message("Gotta go, ttyl!")
```
### Kittens!
```python
from kidmuseum import TxtConversation

conversation = TxtConversation('kittens')
conversation.send_message("Who doesn't love kittens?")

conversation.send_picture("http://dreamatico.com/data_images/kitten/kitten-3.jpg")
conversation.send_picture("http://dreamatico.com/data_images/kitten/kitten-2.jpg")
conversation.send_picture("http://dreamatico.com/data_images/kitten/kitten-1.jpg")
conversation.send_picture("http://dreamatico.com/data_images/kitten/kitten-7.jpg")
```
### Birth Year
```python
    from kidmuseum import TxtConversation
    from datetime import date

    conversation = TxtConversation('birth year')
    conversation.send_message("Hi!")
    name = conversation.get_string("What's your name?")
    age = conversation.get_integer("Hey, " + name + ". How old are you?")

    today = date.today()
    birth_year = today.year - age

    conversation.send_message("You were born in " + birth_year)
```
### Tip Calculator
```python
    from kidmuseum import TxtConversation

    conversation = TxtConversation('tip')
    price = conversation.get_string("How much was the bill?")

    tip = price * 1.20  # tip 20%
    conversation.send_message("You should tip " + tip)
```
### Hipster
```python
    from kidmuseum import TxtConversation

    conversation = TxtConversation('hipster')
    conversation.send_message("Welcome to Hipster Face!")
    selfie = conversation.get_picture("Reply with a selfie and see what happens...")

    selfie.add_moustache("moustache1")
    selfie.add_glasses("glasses1")

    conversation.send_picture(selfie)
```