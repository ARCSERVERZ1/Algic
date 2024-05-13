from django.shortcuts import render
from django.http import JsonResponse
import google.generativeai as genai

# Create your views here


var = 'Ironman'
genai.configure(api_key="AIzaSyBcro2ScpI592K-IV5jhQEzO2Qv8X0wjf0")
# Set up the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens": 8192,
  "response_mime_type": "application/json",
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


def response(requests ,message):

    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)
    message = message.replace('_',' ')
    print(message)
    convo = model.start_chat()
    convo.send_message(message)
    context = {
        'response': convo.last.text
    }
    return JsonResponse(context, safe=False)



