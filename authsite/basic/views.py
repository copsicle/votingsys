import os
import cv2
import face_recognition as fr
from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseForbidden
# from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.cache import SessionStore as CacheSession
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
# from django.utils.timezone import now
# from django.views.generic import FormView
from django.conf import settings
from numpy import fromfile
from datetime import datetime, timedelta
# from pytz import UTC
from .models import Voter
from .forms import VoterForm
# Create your views here.


def index(request):
    if request.session.get('tries', 0) == 3 or request.session.get('advtries', 0) == 3:
        return HttpResponseForbidden(content="<h1><strong><center>"
                                             "Too many tries, please try again later."
                                             "</center></strong></h1>")
    status = request.session.get('status', 0)
    if status == 0:
        if request.method == 'GET':
            form = VoterForm()
            return render(request, 'index.html', {'form': form})
        elif request.method == 'POST':
            request.session['tries'] = request.session.get('tries', 0) + 1
            form = VoterForm(request.POST or None)
            try:
                if form.is_valid():
                    vo = Voter.objects.get(pid=form.cleaned_data['pid'], voted=False,
                                           birth=form.cleaned_data['birth'])
                    if vo.session:
                        ses = CacheSession(session_key=vo.session)
                        if ses.get('age', datetime.utcnow()) > datetime.utcnow():
                            raise Voter.DoesNotExist
                        ses.delete()
                        vo.session = None
                        vo.save()
                    request.session['status'] = 1
                    request.session['tries'] = 0
                    request.session['pk'] = vo.pk
                    return HttpResponseRedirect(reverse('basic:advanced'))
                return render(request, 'index.html', {'form': form})
            except Voter.DoesNotExist:
                form.add_error('pid', 'Unknown voter or bad birth date.')
                return render(request, 'index.html', {'form': form})
    elif status == 1:
        return HttpResponseRedirect(reverse('basic:advanced'))
    elif status == 2:
        return redirect(f"https://{settings.ALLOWED_HOSTS[2]}/")
    # elif status == 3:
    #     if request.method == 'GET':
    #         request.session.flush()
    #         form = VoterForm()
    #         return render(request, 'index.html', {'form': form})
    #     elif request.method == 'POST':
    #         return HttpResponseRedirect(reverse('basic:index'))
    return HttpResponseBadRequest(content='<h1><strong><center>Illegal action.</center></strong></h1>')


def advanced(request):
    if request.session.get('tries', 0) == 3 or request.session.get('advtries', 0) == 3:
        return HttpResponseForbidden(content="<h1><strong><center>"
                                             "Too many tries, please try again later."
                                             "</center></strong></h1>")
    status = request.session.get('status', 0)
    if status == 0:
        if request.method == 'GET':
            return HttpResponseRedirect(reverse('basic:index'))
        return HttpResponseForbidden(content="You have been logged out due to inactivity.")
    elif status == 1:
        try:
            vo = Voter.objects.get(pk=request.session['pk'], voted=False)
            if vo.session:
                ses = CacheSession(session_key=vo.session)
                if ses.get('age', datetime.utcnow()) > datetime.utcnow():
                    raise Voter.DoesNotExist
                ses.delete()
                vo.session = None
                vo.save()
        except Voter.DoesNotExist:
            request.session.flush()
            if request.method == 'GET':
                return HttpResponseRedirect(reverse('basic:index'))
            return HttpResponseForbidden(content="You are not eligible to vote currently.\n"
                                                 "Try again in 10 minutes.")
        # except CacheSession.DoesNotExist:
        #     vo.session = None
        #     vo.save()
        if request.method == 'GET':
            return render(request, 'advanced.html')
        elif request.method == 'POST':
            request.session['advtries'] = request.session.get('advtries', 0) + 1
            detected = False
            try:
                enc = fromfile(vo.image, sep=" ")
                blob = request.FILES['video-blob']
                name = request.POST['video-name']
                if blob.size > 25 * (10 ** 6) or blob.content_type != 'video/webm' or blob.size == 4:
                    return HttpResponseBadRequest()
                path = default_storage.save(f"tmp/{name}", ContentFile(blob.file.read()))
                tmpf = os.path.join(settings.MEDIA_ROOT, path)
                cap = cv2.VideoCapture(tmpf)
                while not detected:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    rgb_frame = frame[:, :, ::-1]
                    locs = fr.face_locations(rgb_frame)
                    if not locs:
                        continue
                    encs = fr.face_encodings(rgb_frame, locs)
                    detected = True in fr.compare_faces(encs, enc)
            finally:
                try:
                    os.remove(tmpf)
                    cap.release()
                finally:
                    if detected:
                        request.session['status'] = 2
                        request.session['advtries'] = 0
                        request.session['age'] = datetime.utcnow() + timedelta(minutes=10)
                        vo.session = request.session.session_key
                        vo.save()
                        return HttpResponse(content="You have been identified successfully.\n"
                                                    "You will now be redirected to the voting page.")
                    return HttpResponseBadRequest(content="You have not been identified or something went wrong.\n"
                                                          "Please Try again.")
    elif status == 2:
        if request.method == 'GET':
            return redirect(f"https://{settings.ALLOWED_HOSTS[2]}/")
        return HttpResponse(content="You are already authenticated.\n"
                                    "You will now be redirected to the voting page.")
    return HttpResponseBadRequest(content='<h1><strong><center>Illegal action.</center></strong></h1>')


def voted(request, ses_id):
    if request.method != 'GET':
        return HttpResponseBadRequest()
    try:
        vo = Voter.objects.get(session=ses_id, voted=False)
        vo.session = None
        vo.voted = True
        vo.save()
        return HttpResponse()
    except Voter.DoesNotExist:
        return HttpResponseBadRequest()


# class VoterFormView(FormView):
#     template_name = 'index.html'
#     form_class = VoterForm
#     success_url = '/advanced/'
#
#     def get(self, request, **kwargs):
#         if request.session.get('tries', 0) == 3 or request.session.get('advtries', ) == 3:
#             return HttpResponseBadRequest(content="Too many tries, please try again later")
#         status = request.session.get('status', 'guest')
#         if status == 'basic':
#             return HttpResponseRedirect(reverse('authsite:advanced'))
#         elif status == 'voted':
#             request.session['status'] = 'guest'
#             request.session['tries'] = 0
#             request.session['advtries'] = 0
#             request.session.set_expiry(settings.SESSION_COOKIE_AGE)
#
#         return self.render_to_response(self.get_context_data())
#
#     def form_invalid(self, form):
#         tries = self.request.session.get('tries', 0)
#         self.request.session['tries'] = tries + 1
#         return self.render_to_response(self.get_context_data(form=form))
#
#     def form_valid(self, form):
#         try:
#             vote = Voter.objects.get(pid=form.cleaned_data['pid'], voted=False,
#                                      session=None, birth=form.cleaned_data['birth'])
#         except Voter.DoesNotExist:
#             return self.form_invalid(form)
#         self.request.session['status'] = 'basic'
#         self.request.session['tries'] = 0
#         self.request.session['pk'] = vote.pk
#         return HttpResponseRedirect(self.get_success_url())
