from django.shortcuts import render
from django.http import JsonResponse
import google.generativeai as genai
from rest_framework.decorators import api_view
from datetime import datetime
import json


@api_view(['POST', 'GET'])
def response(requests):
    return JsonResponse({"message": "server alive"}, safe=False)
