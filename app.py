import os
import sys
import json
import luis
import urllib2
import urllib
import requests
from random import randint
from flask import Flask, request
from googleplaces import GooglePlaces, types, lang

# Azure portal URL.
base_url = 'https://westus.api.cognitive.microsoft.com/'
# Your account key goes here. (used for cognitive services)
account_key = ''
google_places_key = ''

headers = {'Content-Type':'application/json', 'Ocp-Apim-Subscription-Key':account_key}

luis_url = luis_url = luis.Luis('')
google_places = GooglePlaces(google_places_key)

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    send_message(sender_id, determineCourseOfAction(message_text))

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200

def determineCourseOfAction(input, diaryEntry=True):
    if(classifyIntent(input)=="Greeting"):
        return Greeting(input)
    elif(classifyIntent(input)=="Information"):
        return Information(input) 
    elif(classifyIntent(input)=="Bye"):
        return Bye(input)
    elif(classifyIntent(input)=="Emotion"):
        return Emotion(input, diaryEntry)
    elif(classifyIntent(input)=="HowAreYou"):
        return HowAreYou(input)
    elif(classifyIntent(input)=="Store"):
        return Store(input)
     #This means we have already recorded our diary entry
    else:
        return none(input)
        
def classifyIntent(input): 
    
    luisData = luis_url.analyze(input)
    return luisData.best_intent().intent #Return the intent
    
#Functions that deal with intents 
def Greeting(name):
    #Todo If it is the user's first time using the application, give a brief explanation
    randomChoice = randint(0,5)
    if(randomChoice ==1):
        return "Hello! My name is Tonzo." 
    elif(randomChoice ==2):
        return "Greetings!"
    elif(randomChoice == 3):
        return "Howdy!"
    elif(randomChoice == 4):
        return "Hello!"
    else:
        return "Hey!"

def Diary(input):
    StoreSentiment(getSentimentValue(input)) #Store sentiment
    currentMood = getMoodCheck(input)
    Emotion(input)
    
def HowAreYou(input):
    randomChoice = randint(0,5)
    if(randomChoice == 1):
        return "I'm Good."
    elif(randomChoice ==2):
        return "I'm fine and dandy."
    elif(randomChoice == 3):
        return "I am fantastic."
    elif(randomChoice == 4):
        return "I'm well beyond describing!"
    elif(randomChoice == 5):
        return "I'm marvelous."
    
def Bye(input):
    randomChoice = randint(0,4)
    if(randomChoice == 1):
        return "Bye Bye!"
    elif(randomChoice == 2):
        return "Talk to you later!"
    elif(randomChoice == 3):
        return "Bye!"
    elif(randomChoice == 4):
        return "Bye bye for now!"
        
    
def Emotion(input, askedAboutDay=False):
    if(askedAboutDay==False):
        return "Tell me about your day"
    else: 
        currentMood = getMoodCheck(input)
        if(currentMood=="Happy"):
            return Happy()
        elif(currentMood == "Stressed"): 
            return Stressed()
        elif(currentMood == "Sad"):
            return Sad(input)
        
        
def Sad(input):
    randomChoice = randint(0,10)
    value = "Here I have a joke for you: "
    if "dying" in input:
        return Crisis() 
    elif(randomChoice ==0):
        value += "Where did the military commander keep his armies? In his sleevies."
    elif(randomChoice ==1):
        value += "What happens to a frog's car when it breaks down? It gets toad away."
    elif(randomChoice ==2):
        value += "What did the duck say when he bought lipstick? Put it on my bill."
    elif(randomChoice == 3):
        value += "Can a kangaroo jump higher than the Empire State Building? Of course. The Empire State building can't jump."
    elif(randomChoice ==4):
        value += "Did you hear about the kidnapping at school? It's ok. He woke up."
    elif(randomChoice == 5):
        value += "Why does Humpty Dumpty love autumn? Because Humpty Dumpty had a great fall."
    elif(randomChoice == 6):
        value += "What do you call a pig that does karate? A pork chop."
    elif(randomChoice == 7):
        value += "I was wondering why the ball kept getting bigger and bigger, and then it hit me."
    elif(randomChoice == 8):
        value += "A man got hit in the head with a can of Coke, but he was alright because it was a soft drink."
    elif(randomChoice == 9):
        value += "What starts with E, ends with Em and only have 1 letter in it? A Envelope."
    elif(randomChoice == 10):
        value += "If you ever get cold, just stand in the corner of a room for a while. They're normally around 90 degrees."
    return value

def Crisis():
    #Todo->use location to return for different places
    return "Here's a hotline for you to call: 1-866-531-2600"
    
def Stressed():
    randomChoice = randint(0,20)
    if(randomChoice ==0):
        return "Try watching a comedy show."
    elif(randomChoice == 1):
        return "Maybe try going for a walk?"
    elif(randomChoice ==2):
        return "Have you tried journaling?"
    elif(randomChoice ==3):
        return "How about you give guided meditation a try?"
    elif(randomChoice ==4):
        return "Treat yourself to a nice massage."
    elif(randomChoice == 5):
        return "How about you take a bubble bath!"
    elif(randomChoice == 6):
        return "Try exercising!"
    elif(randomChoice == 7):
        return "Listen to running water."
    elif(randomChoice == 8):
        return "Read a good book."
    elif(randomChoice == 9):
        return "Have you tried listening to some of your favourite music?"
    elif(randomChoice == 10):
        return "Maybe go on a lunch date with a good friend?"
    elif(randomChoice == 11):
        return "Take a nap. Remember that sleep is important."
    elif(randomChoice == 12):
        return "Have you tried going for a bike ride?"
    elif(randomChoice == 13):
        return "Maybe try doodling?"
    elif(randomChoice == 14):
        return "Try going for a walk on a beach."
    elif(randomChoice == 15):
        return "Have a dance party with some of your favourite songs!"
    elif(randomChoice == 16):
        return "Stretch and take some deep breaths!"
    elif(randomChoice == 17):
        return "You should treat yourself to your favourite meal."
    elif(randomChoice == 18):
        return "Watch some funny videos on youtube."
    elif(randomChoice == 19):
        return "Try curling up with your favourite hot beverage!"
    elif(randomChoice == 20):
        return "Try going to your local pet store"
    
    
def Happy():
    randomChoice = randint(0,4)
    value = "I'm glad that you are ok. "
    if(randomChoice== 0):
        value += "Tell me what your favourite song is?"
    elif(randomChoice==1):
        value += "Tell me what your favourite movie is?"
    elif(randomChoice==2):
        value+= "Tell me what your favourite book is?"
    elif(randomChoice==3):
        value +=  "What kind of activites do you enjoy?"
    elif(randomChoice==4):
        value += "Who are you friends with?"  
    return value  
        
def Information(input):
    input = input.lower()

    if "depression" in input:
        return "Here's what I dug up for you: http://www.cmha.ca/mental-health/understanding-mental-illness/depression/"
    elif "anxiety" in input:
        return "Here's what I dug up for you: http://www.cmha.ca/mental_health/understanding-anxiety-disorders/#.V-SGFKIrJaE"
    elif "bipolar" in input:
        return "Here's what I dug up for you: http://www.cmha.ca/mental-health/understanding-mental-illness/bipolar-disorder/"
    elif "ptsd" in input:
        return "Here's what I dug up for you: http://www.mayoclinic.org/diseases-conditions/post-traumatic-stress-disorder/basics/definition/con-20022540"
    elif "ocd" in input:
        return "Here's what I dug up for you: http://www.cmha.ca/mental_health/obsessive-compulsive-disorder/#.V-SGtKIrJaE"
    elif "schizophrena" in input:
        return "Here's what I dug up for you: http://www.cmha.ca/mental_health/facts-about-schizophrenia/#.V-SGcaIrJaE"  
    #Location stuff
    elif "counselor" in input:
        return getLocation(getLocationName(input), "counselor")
    elif "counsellor" in input:
        return getLocation(getLocationName(input), "counsellor")
    elif "psychologist" in input:
        return getLocation(getLocationName(input), "psychologist")
    elif "psychiatrist" in input:
        return getLocation(getLocationName(input), "psychiatrist")
    else:
        return "Sorry, I don't understand."

def getLocation(location, searchTerm):
   query_result = google_places.nearby_search(location=location, keyword=searchTerm, radius=20000)
   query_result.places[0].get_details()
   informationStr = query_result.places[0].name +' '
   informationStr += 'Phone Number: ' + query_result.places[0].local_phone_number + ' '
   if(query_result.places[0].website != None):
       informationStr += 'Website: ' +  query_result.places[0].website + ' '
   return informationStr
   #Want to create string of information that we return

def getLocationName(input):
    if "location" in input:
        location = input.split("location",1)[1] #Change to regrex
    elif "in" in input:
        location = input.split("in",1)[1]
    else:
        return "London, England"
    return location    

def Store(input):
    randomChoice = randint(0,4)
    if(randomChoice==1):
        return "Neat! I'll have to check it out some time."
    elif(randomChoice == 2):
        return "Cool!"
    elif(randomChoice == 3):
        return "Neato!"
    elif(randomChoice == 4):
        return "Super coolio!"

def none(input):
    return "Sorry, I don't quite understand. I am still learning."
    
def Retrieve(type):

    return "OK"
    
def getMoodCheck(input):
    if(getSentimentValue(input) > 0.80):
        return "Happy"
    elif(getSentimentValue(input) < 0.30):
        return "Sad"
    elif(getSentimentValue(input) < 0.015):
        return "Stressed"
    
def StoreSentiment(input):
    print "Test"
    #Stores sentiment value in the database
def getInputText(input):
    return '{"documents":[{"id":"1","text":"' + input + '"}]}'
    
def getSentimentValue(input):
    batch_sentiment_url = base_url + 'text/analytics/v2.0/sentiment'
    batch_sentiment_url = base_url + 'text/analytics/v2.0/sentiment'
    input_texts = getInputText(input)
    req = urllib2.Request(batch_sentiment_url, input_texts, headers) 
    response = urllib2.urlopen(req)
    result = response.read()
    obj = json.loads(result)
    for sentiment_analysis in obj['documents']:
        return sentiment_analysis['score']
        
def getKeyPhrases(input):
    batch_keyphrase_url = base_url + 'text/analytics/v2.0/'
    input_texts = getInputText(input)
    req = urllib2.Request(batch_keyphrase_url, input_texts, headers) 
    response = urllib2.urlopen(req)
    result = response.read()
    obj = json.loads(result)
    for keyphrase_analysis in obj['documents']:
        return map(str,keyphrase_analysis['keyPhrases'])

def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

    
def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
