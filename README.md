# SMS Playground
Server and client for letting users easily make quick and fun SMS/MMS programs.

## How to create a program for SMS Playground
1. Install python 2.7+ or python 3.4+ if it isn't already installed. If you're on a Mac or Linux,
   it'll already by installed on your computer. If you're on Windows and you havent installed it yet,
   go to https://www.python.org/downloads/ to get the installer.
1. Download the `kidmuseum.py` library into a directory on your computer.  [You can get it here.](http://sms-playground.com/kidmuseum.py)
1. Fire up your favorite text editor, like [Notepad++](https://notepad-plus-plus.org/) or
   [Sublime Text](http://www.sublimetext.com/) and start a new file.
1. Use the guide below to write a program. I'd recommend copying one of the examples at the bottom of this page as a starting point.
1. Save the file with the .py extension (e.g. myprogram.py) in the same directory as kidmuseum.py.
1. Run your program. On windows you should be able to double click the file to run it.
1. Send a text with the phrase that starts the conversation the SMS Playground phone number to run through your program.

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

### TxtConversation Methods

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
Sends a message to the user asking for a response, and then returns the user's response as a floating point number.
```python
price = conversation.get_floating_point("How much was the bill?")
tip = price * 0.20  # tip 20%
conversation.send_message("You should tip " + tip)
```
#### get_picture
Sends a message to the user asking for a response, and then returns the user's response as a Picture.
```python
picture = conversation.get_picture("Gimme your best selfie")
picture.add_glasses("kanye_shades")
conversation.send_picture(picture, "You with Kanye Shades")
```
The `get_picture` returns a Picture object.  These objects have a few methods of their own that allow
you to add things to the picture and then send it back to the user's phone using the `send_picture`
method above.

### Picture Methods

#### add_glasses
Adds glasses to the picture if there's a face in it.  You can pass in any of the following as a string:

 _ | _ | _
:--------: | :----------: | :-------:
`shades` | `aviators` | `kanye`
![shades](https://s3.amazonaws.com/sms-playground/readme_images/shades_rm.png) | ![aviators](https://s3.amazonaws.com/sms-playground/readme_images/aviators_rm.png) | ![kanye](https://s3.amazonaws.com/sms-playground/readme_images/kanye_rm.png)
`glasses` | `rectangle_glasses` |
![glasses](https://s3.amazonaws.com/sms-playground/readme_images/glasses_rm.png) | ![rectangle_glasses](https://s3.amazonaws.com/sms-playground/readme_images/rectangle_glasses_rm.png) |

```python
picture = conversation.get_picture("Gimme your best selfie")
picture.add_glasses("kanye")
conversation.send_picture(picture, "You with Kanye Shades")
```

#### add_moustache
Adds a moustache to the picture if there's a face in it. You can pass any of the following as a string:

 _ | _ | _
:--------: | :----------: | :-------:
`curly` | `handlebar` | `imperial`
![curly](https://s3.amazonaws.com/sms-playground/readme_images/curly_rm.png) | ![handlebar](https://s3.amazonaws.com/sms-playground/readme_images/handlebar_rm.png) | ![imperial](https://s3.amazonaws.com/sms-playground/readme_images/imperial_rm.png)
`walrus` | `reynolds` | `yosemite_sam`
![walrus](https://s3.amazonaws.com/sms-playground/readme_images/walrus_rm.png) | ![reynolds](https://s3.amazonaws.com/sms-playground/readme_images/reynolds_rm.png) | ![yosemite_sam](https://s3.amazonaws.com/sms-playground/readme_images/yosemite_sam_rm.png)
`horseshoe` |  |
![horseshoe](https://s3.amazonaws.com/sms-playground/readme_images/horseshoe_rm.png) |  |

```python
picture = conversation.get_picture("Gimme your best selfie")
picture.add_moustache("curly")
conversation.send_picture(picture, "You in Portland, OR")
```

## Example programs:

### I <3 Compliments
```python
from kidmuseum import TxtConversation

conversation = TxtConversation("I <3 compliments")
conversation.send_message("Hi! You love compliments?  Well I got tons of 'em!")
name = conversation.get_string("First, what's your name?")

conversation.send_message("Hey, %s is an awesome name!" % name)
conversation.send_message("I bet you're super smart too.")
conversation.send_message("To be honest, you're the coolest person I've talked today BY FAR :D")
conversation.send_message("Gotta go, ttyl!")
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
age = conversation.get_integer("Hey, %s. How old are you?" % name)

today = date.today()
birth_year = today.year - age

conversation.send_message("You were born in %s" % birth_year)
```
### Tip Calculator
```python
from kidmuseum import TxtConversation

conversation = TxtConversation('tip')
price = conversation.get_floating_point("How much was the bill?")

tip = price * 0.20  # tip 20%
conversation.send_message("You should tip %0.2f" % tip)
```
### Hipster
```python
from kidmuseum import TxtConversation

conversation = TxtConversation('hipster')
conversation.send_message("Welcome to Hipster Face!")
selfie = conversation.get_picture("Reply with a selfie and see what happens...")

selfie.add_moustache("handlebar")
selfie.add_glasses("shades")

conversation.send_picture(selfie)
```
