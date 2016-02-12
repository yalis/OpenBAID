# -*- coding: utf-8 -*-
import time
from django.shortcuts import redirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

def home(request):
    return redirect('accounts:login')


def handler404(request):
    response = render(request, '404.html')
    response.status_code = 404
    return response


def handler500(request):
    response = render(request, '500.html')
    response.status_code = 500
    return response
