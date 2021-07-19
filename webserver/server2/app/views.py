from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
import requests

def index(request):
	return render(request, 'app/index.html', {})

def results(request):
	if request.method == "POST":
		response = requests.post("http://127.0.0.1:8000/polls/1/vote/", {"choice":request.POST['choice']})
	return HttpResponse(requests.get("http://127.0.0.1:8000/polls/1/results/"))