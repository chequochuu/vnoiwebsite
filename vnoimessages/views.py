from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View


def index(request):
    return HttpResponse("This is message home")


def inbox(request):
    return HttpResponse("This is inbox page")

