from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import Context
from django.template.loader import get_template
from urllib.parse import urlencode
import httplib2
import json
import rsoi1.config

# Create your views here.
def _redirect_view_code_received(request):
    requester = httplib2.Http()
    request_params = dict()
    request_params['code'] = request.GET['code']
    request_params['redirect_uri'] = rsoi1.config.Config.redirect_uri
    request_params['grant_type'] = 'authorization_code'
    request_params['client_secret'] = rsoi1.config.Config.client_secrect
    request_params['client_id'] = rsoi1.config.Config.client_id

    #requester = httplib2.Http(".cache", disable_ssl_certificate_validation=True)
    headers, body = requester.request('https://api.instagram.com/oauth/access_token', 'POST', urlencode(request_params));
    resp_object = json.loads(body)
    if 'access_token' in resp_object:
        request.session.set_expiry(5 * 60)
        request.session['access_token'] = resp_object['access_token']
        templ = get_template('success.html')
        return HttpResponse(templ.render(Context({})))
    else:
        raise Http404

def _redirect_view_error(request):
    raise Http404

def _defirect_view_exception(request):
    raise Http404

def redirect_view(request):
    if 'code' in request.GET:
        return _redirect_view_code_received(request)
    elif 'error' in request.GET:
        return _redirect_view_error(request)
    else:
        return _defirect_view_exception(request)

def logout(request):
    if 'access_token' in request.session:
        del request.session['access_token']
    return redirect('/rsoi1/app')

def _get_auth_url():
    return 'https://api.instagram.com/oauth/authorize/?client_id={0}&redirect_uri={1}&response_type=code'.format(rsoi1.config.Config.client_id, rsoi1.config.Config.redirect_uri)

def _get_liked_url(access_token):
    return 'https://api.instagram.com/v1/users/self/media/liked?access_token={0}'.format(access_token)

def app(request):
    if 'access_token' not in request.session:
        templ = get_template('login.html')
        return HttpResponse(templ.render(Context({'auth_url': _get_auth_url()})));
    else:
        requester = httplib2.Http()
        headers, body = requester.request(_get_liked_url(request.session['access_token']));
        resp_object = json.loads(body)
        if 'data' not in resp_object:
            templ = get_template('login.html')
            return HttpResponse(templ.render(Context({'auth_url': _get_auth_url()})));
        liked_images = []
        for img_data in resp_object['data']:
            if img_data['type'] != 'image':
                continue
            liked_images.append(img_data['images']['standard_resolution']['url'])
        templ = get_template('app.html')
        return HttpResponse(templ.render(Context({'liked_images': liked_images})));