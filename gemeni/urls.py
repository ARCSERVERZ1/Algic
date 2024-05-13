
from django.contrib import admin
from django.urls import path , include
from gemeni import views
urlpatterns = [
    path('<str:message>' , views.response),
]