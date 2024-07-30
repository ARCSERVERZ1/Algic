import os.path
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




def bifrost(query, context, user):
    def waiting_until_response(context):
        start_time = datetime.now()
        counter = 0
        while True:
            time.sleep(0.1)
            # print(f'Counter = {counter}')
            counter = counter + 1
            if counter > 100:
                time_out_res = {
                    'query': query,
                    'context': context,
                    'response_time': str(datetime.now() - start_time),
                    'response': 'its taking too long to respond try another one'
                }
                return time_out_res

            trigger = fbd.child(user).child('res_status').get()
            if str(trigger.val()) == 'end':
                print("process end trigger received from bifrost")
                res = fbd.child(user).child('response').get()
                print("response is ", res)
                context = {
                    'query': query,
                    'context': context,
                    'response_time': str(datetime.now() - start_time),
                    'response': res.val(),
                }
                fbd.child(user).child('res_status').set('end')
                return context

    firebase = pyrebase.initialize_app(firebaseConfig)
    fbd = firebase.database()
    if context == 'RAG':
        print("writing data to firebase")
        fbd.child(user).child('query').set(query)
        fbd.child(user).child('res_status').set('set')
        return waiting_until_response(context)


def synchat(data, user):
    start_time = datetime.now()
    file_name = str(datetime.now().date())+'_'+user+'_synchat.txt'
    with open(file_name, 'a') as file:
        file.write(data + '\n')  # Append first line with a newline character

    if data.find('close daily chat') != -1:

        context = '-'
    else:
        context = 'synchat'

    return {
        'context':context,
        'response_time': str(datetime.now() - start_time),
        'response': 'mm..ok'
    }



@api_view(['POST', 'GET'])
def response(requests):

    def json_update(dict):
        with open(chat_file_name, 'w') as file:
            json.dump(dict, file, indent=4)

    data = requests.data
    user = 'sanjay' if data['user'] == '' else data['user']
    chat_file_name = str(user) + '_chat_data.json'

    json_data = {
        "context": '-',
        "last_convo_time": "-"
    }

    if not os.path.exists(chat_file_name):
        with open(chat_file_name, 'w') as file:
            json.dump(json_data, file, indent=4)
    else:
        json_data = json.loads(open(chat_file_name).read())

    if json_data["context"] != '-':
        last_convo_time = datetime.strptime(json_data['last_convo_time'].split('.')[0], '%Y-%m-%d %H:%M:%S')
        print(datetime.now()-last_convo_time )
        # time_diff = datetime.now()-last_convo_time
        # context = json_data["context"] if time_diff.total_seconds()/60 < 1 else '-'
        context = json_data['context']
    else:
        context = json_data['context']

    print("Query : ",data['ask'])

    if data['ask'].find('search for') != -1 or context == 'RAG':
        res = bifrost(data['ask'], 'RAG', user)
        json_update({
            'context': res['context'],
            'last_convo_time': str(datetime.now())
        })
        return JsonResponse(res, safe=False)

    elif data['ask'].lower().find('activate daily chat') != -1 or context == 'synchat':
        res = synchat(data['ask'], user )
        json_update({
            'context': res['context'],
            'last_convo_time': str(datetime.now())
        })
        return JsonResponse(res, safe=False)



    else:
        # gemeni
        start_time = datetime.now()
        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)
        convo = model.start_chat()
        convo.send_message(data['ask'])
        response = convo.last.text
        diff = datetime.now() - start_time
        context = {
            'response': response,
            'response_time': diff.total_seconds()
        }
        return JsonResponse(context, safe=False)

#
# @api_view(['POST', 'GET'])
# def ref_response(requests):
#     def check_condition():
#         while True:
#             time.sleep(0.1)
#             trigger = fbd.child("bifrost").child('bifrost_trigger').get()
#             print("waiting for triggger > ", trigger.val())
#             if str(trigger.val()) == '2':
#                 print("trigger received")
#                 res = fbd.child("bifrost").child('bifrost_response').get()
#                 print("response is ",res)
#                 context = {
#                     'response': res.val(),
#                     'response_time': 0
#                 }
#                 print("returing data")
#                 fbd.child("bifrost").child('bifrost_trigger').set(0)
#                 return context
#
#
#     if requests.method == 'GET':
#         return JsonResponse({"messgae": "server alive"}, safe=False)
#     start_time = datetime.now()
#     firebase = pyrebase.initialize_app(firebaseConfig)
#     fbd = firebase.database()
#     response = 'defualt response'
#     model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
#                                   generation_config=generation_config,
#                                   safety_settings=safety_settings)
#     data = requests.data
#     if data['ask'].find('search') != -1:
#         fbd.child("bifrost").child('bifrost_input').set(data['ask'])
#         res = check_condition()
#
#         print("return inside")
#         print(res)
#         return JsonResponse(res, safe=False)
#     elif data['ask'].find('sync chat'):
#         return JsonResponse({'answer':'sync chat activated'}, safe=False)
#
#     elif data['ask']:
#         convo = model.start_chat()
#         convo.send_message(data['ask'])
#         response = convo.last.text
#     diff = datetime.now() - start_time
#     context = {
#         'response': response,
#         'response_time': diff.total_seconds()
#     }
#     return JsonResponse(context, safe=False)
