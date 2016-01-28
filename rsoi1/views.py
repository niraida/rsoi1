from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import Context
from django.template.loader import get_template
from urllib.parse import urlencode
import requests
import rsoi1.config

def _get_auth_url():
    return 'https://api.instagram.com/oauth/authorize/?client_id={0}&redirect_uri={1}&response_type=code'.format(rsoi1.config.Config.client_id, rsoi1.config.Config.redirect_uri)

def _get_recent_url(access_token):
    return 'https://api.instagram.com/v1/users/self/media/recent?access_token={0}'.format(access_token)

def _redirect_view_error(request):
    raise Http404

def _redirect_view_code_received(request):
    request_params = dict()
    request_params['code'] = request.GET['code']
    request_params['redirect_uri'] = rsoi1.config.Config.redirect_uri
    request_params['grant_type'] = 'authorization_code'
    request_params['client_secret'] = rsoi1.config.Config.client_secrect
    request_params['client_id'] = rsoi1.config.Config.client_id

    instagram_response = requests.post('https://api.instagram.com/oauth/access_token', data=urlencode(request_params))
    instagram_response = instagram_response.json()

    if 'access_token' in instagram_response:
        request.session.set_expiry(5 * 60)
        request.session['access_token'] = instagram_response['access_token']
        templ = get_template('success.html')
        return HttpResponse(templ.render(Context({})))
    else:
        raise Http404

def app(request):
    if 'access_token' not in request.session:
        templ = get_template('login.html')

        return HttpResponse(templ.render(Context({'auth_url': _get_auth_url()})));
    else:
        instagram_response = requests.get(_get_recent_url(request.session['access_token']));
        instagram_response = instagram_response.json()

        if 'data' not in instagram_response:
            templ = get_template('login.html')
            return HttpResponse(templ.render(Context({'auth_url': _get_auth_url()})));

        media = []

        for img_data in instagram_response['data']:
            if img_data['type'] != 'image':
                continue
            media.append(img_data['images']['standard_resolution']['url'])

        templ = get_template('app.html')

        return HttpResponse(templ.render(Context({'media': media})));

def redirect_view(request):
    if 'code' in request.GET:
        return _redirect_view_code_received(request)
    else:
        return _redirect_view_error(request)

def logout(request):
    if 'access_token' in request.session:
        del request.session['access_token']

    return redirect('/rsoi1/app')