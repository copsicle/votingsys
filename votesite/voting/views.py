from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.conf import settings
from datetime import datetime
from requests import get
from .models import Party
# Create your views here.


def index(request):
    if request.session.get('tries', 0) == 3 or request.session.get('advtries', 0) == 3:
        return HttpResponseBadRequest(content="<h1><strong><center>"
                                              "Too many tries, please try again later"
                                              "</center></strong></h1>")
    if request.session.get('status', 0) != 2:
        return redirect(f"https://{settings.ALLOWED_HOSTS[0]}/")
    elif request.session.get('age', datetime.utcnow()) <= datetime.utcnow():
        request.session.flush()
        return redirect(f"https://{settings.ALLOWED_HOSTS[0]}/")
    elif request.method == 'GET':
        plist = Party.objects.exclude(letters="פסול")
        return render(request, 'index.html', {'plist': plist})
    elif request.method == 'POST':
        key = request.session.session_key
        request.session.flush()
        if get(f"https://{settings.ALLOWED_HOSTS[0]}/voted/{key}").status_code != 200:
            return HttpResponseBadRequest(content="<h1><strong><center>Could not mark voter.</center></strong></h1>")
        choice = request.POST['note']
        try:
            party = Party.objects.get(letters=choice)
            party.count += 1
            party.save()
            return HttpResponse(content="<h1><strong><center>Voted successfully.</center></strong></h1>")
        except Party.DoesNotExist:
            party = Party.objects.get(letters="פסול")
            party.count += 1
            party.save()
            return HttpResponseBadRequest("<h1><strong><center>Voting failed.</center></strong></h1>")
    return HttpResponseBadRequest(content="<h1><strong><center>Unhandled request.</center></strong></h1>")
