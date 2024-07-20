import time

from django.shortcuts import render
from django.http import JsonResponse
import google.generativeai as genai
from rest_framework.decorators import api_view
from datetime import datetime
import pyrebase
import json

# Create your views here


var = 'Ironman'
genai.configure(api_key="AIzaSyBcro2ScpI592K-IV5jhQEzO2Qv8X0wjf0")
# Set up the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,

}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

convo = None

firebaseConfig = {
    'apiKey': "AIzaSyAMoENs6AiTkSnAhuHuzwpGFkxeaAhGQB4",
    "authDomain": "aura-bifrost.firebaseapp.com",
    "databaseURL": "https://aura-bifrost-default-rtdb.firebaseio.com",
    "projectId": "aura-bifrost",
    "storageBucket": "aura-bifrost.appspot.com",
    "messagingSenderId": "774636407803",
    "appId": "1:774636407803:web:7710f0dec1c433a1b5d95e",
    "measurementId": "G-F8LXP6ZP1Q"
}


@api_view(['POST', 'GET'])
def response(requests):
    def check_condition():
        while True:
            time.sleep(0.1)
            trigger = fbd.child("bifrost").child('bifrost_trigger').get()
            print("waiting for triggger > ", trigger.val())
            if str(trigger.val()) == '2':
                print("trigger received")
                res = fbd.child("bifrost").child('bifrost_response').get()
                print("response is ",res)
                context = {
                    'response': res.val(),
                    'response_time': 0
                }
                print("returing data")
                return context

    if requests.method == 'GET':
        return JsonResponse({"messgae": "server alive"}, safe=False)
    start_time = datetime.now()
    firebase = pyrebase.initialize_app(firebaseConfig)
    fbd = firebase.database()
    response = 'defualt response'
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)
    data = requests.data
    if data['ask'].find('fetch') != -1:
        fbd.child("bifrost").child('bifrost_input').set(data['ask'])
        res = check_condition()

        print("return inside")
        print(res)
        return JsonResponse(res, safe=False)

    elif data['ask']:
        convo = model.start_chat()
        convo.send_message(data['ask'])
        response = convo.last.text
    diff = datetime.now() - start_time
    context = {
        'response': response,
        'response_time': diff.total_seconds()
    }
    return JsonResponse(context, safe=False)
