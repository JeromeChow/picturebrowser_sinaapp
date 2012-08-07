from django.template.loader import get_template
from django.template import Context, Template
from django.shortcuts import render_to_response

from django.http import HttpResponse
from django.http import HttpResponseRedirect

import logging
import datetime
import json

from weibo import APIClient

# Static vars
APP_KEY = '3591066593' # app key/consumer key
APP_SECRET = 'a9e5ab0fec71ead8fb744ee83682bd57' # app secret/consumer secret
#CALLBACK_URL = 'http://127.0.0.1:8080/' # local debug call back url, WARNING!! has to be exactly the same as set in api.weibo.com
CALLBACK_URL = 'http://picturebrowser.sinaapp.com'

DEBUG_TRACE = logging.getLogger('mysite.custom')

def getFriendList(total_friend_info):
    friend_list = [{'screen_name' : user['screen_name'],
                     'avatar_large' : user['avatar_large'],
                     'description' : user['description'],
                     'id' : user['id']}
                         for user in total_friend_info['users']]
    return friend_list
    
def getPhotoList(client, screen_name, count, page):
    user_timeline_photo = client.get.statuses__user_timeline(screen_name=screen_name, feature=2, count=count, page=page)
    photo_list_all = []
    for photo in user_timeline_photo['statuses']:
        if photo.has_key('original_pic') is True:
            photo_list_all.append({'text': photo['text'],
                                   'image' : photo['original_pic']})
        elif photo.has_key('retweeted_status') is True:
            if photo['retweeted_status'].has_key('original_pic') is True:
                photo_list_all.append({'text': photo['retweeted_status']['text'],
                                       'image' : photo['retweeted_status']['original_pic']})
    return photo_list_all

def getPhotoListFoo(client, screen_name, count, page):
    print "getPhotoListFoo"

def index(request):
    weibo_client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
    if request.COOKIES.has_key('access_token') is False:
        if request.GET.has_key('code') is False:
            # Got request for app main page from browser
            redirect_url = weibo_client.get_authorize_url()
            # Redirect browser to OAuth2 login page
            return HttpResponseRedirect(redirect_url)
        else:
            # Got request from OAuth2 server with auth code
            code = request.GET['code']
            r = weibo_client.request_access_token(code)
            access_token = r.access_token
            expires_in = r.expires_in
            uid = r.uid
            # Store them in cookies and send back to browser.
            response = HttpResponseRedirect(CALLBACK_URL)
            response.set_cookie('access_token', access_token)
            response.set_cookie('expires_in', expires_in)
            response.set_cookie('uid', uid)

            # Redirect browser to app main page
            return response
    else:
        print "printing!"
        # Got request for app main page from browser
        access_token = request.COOKIES['access_token']
        expires_in = request.COOKIES['expires_in']
        uid = request.COOKIES['uid']

        weibo_client.set_access_token(access_token, expires_in)
            
        # Get user info
        user_info = weibo_client.get.users__show(uid=uid)
        screen_name = user_info.screen_name
        avatar_large = user_info.avatar_large
        description = user_info.description
            
        # Get friend info
        friend_info = weibo_client.get.friendships__friends(uid=uid, count=20)
        friend_list = getFriendList(friend_info)
        friend_number = friend_info['total_number']
        next_friend_cursor = friend_info['next_cursor']
        friend_count = 20
                    
        return render_to_response('index.html', {
                                      'screen_name' : screen_name,
                                      'avatar_large' : avatar_large,
                                      'description' : description,
                                      'friend_list' : friend_list,
                                  })
def morefriends(request):
    weibo_client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
    if request.COOKIES.has_key('access_token') is False:
        DEBUG_TRACE.debug("Has no acccess token")
        return HttpResponseRedirect(CALLBACK_URL)
    else:
        access_token = request.COOKIES['access_token']
        expires_in = request.COOKIES['expires_in']
        uid = request.COOKIES['uid']
        friend_cursor = request.GET['friend_cursor']
        
        weibo_client.set_access_token(access_token, expires_in)
        friend_info = weibo_client.get.friendships__friends(uid=uid, count=20, cursor=friend_cursor)
        friend_list = getFriendList(friend_info)
        
        t = Template(""" 
                     {% for friend in friend_list %}
		                <li><a href="photogallary?query_screen_name={{ friend.screen_name }}" data-transition="slide">
	                        <img width="80" height="80" src="{{ friend.avatar_large }}"></img>
				            <h3>{{ friend.screen_name }}</h3>
				            <p>{{ friend.description }}</p>
	                    </a></li>
                    {% endfor %} """)
                    
        c = Context({'friend_list': friend_list})
        html = t.render(c)
        response = HttpResponse(html)
        return response
                                      
def photogallary(request):
    weibo_client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
    if request.COOKIES.has_key('access_token') is False:
        DEBUG_TRACE.debug("Has no acccess token")
        return HttpResponseRedirect(CALLBACK_URL)
    else:
        access_token = request.COOKIES['access_token']
        expires_in = request.COOKIES['expires_in']
        uid = request.COOKIES['uid']
        query_screen_name = request.GET['query_screen_name']
        
        weibo_client.set_access_token(access_token, expires_in)
        user_info = weibo_client.get.users__show(screen_name=query_screen_name)
        screen_name = user_info.screen_name
        avatar_large = user_info.avatar_large
        photo_list = getPhotoList(weibo_client, query_screen_name, count=5, page=1)
        
        return render_to_response('photogallary.html', {'photo_list' : photo_list,
                                                        'screen_name' : screen_name,
                                                        'avatar_large' : avatar_large,})

def morepictures(request):
    weibo_client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
    if request.COOKIES.has_key('access_token') is False:
        DEBUG_TRACE.debug("Has no acccess token")
        return HttpResponseRedirect(CALLBACK_URL)
    else:
        access_token = request.COOKIES['access_token']
        expires_in = request.COOKIES['expires_in']
        uid = request.COOKIES['uid']
        page = request.GET['page']
        name = request.GET['name']
        weibo_client.set_access_token(access_token, expires_in)
        user_info = weibo_client.get.users__show(screen_name=name)
        screen_name = user_info.screen_name
        avatar_large = user_info.avatar_large

        photo_list = getPhotoList(weibo_client, screen_name, 5, page)
        t = Template(""" 
		            {% for photo in photo_list %}
		                <li data-icon="false"><a href="">
		                    <div class="my-li-thumb">
		                        <img width="50" height="50" src="{{ avatar_large }}" />
		                    </div>
		                    <h3 class="my-li-name">{{ screen_name }}</h3>
		                    <p  class="my-li-text">{{ photo.text }}</p>
		                    <div class="my-li-content">
	                            <img class="my-li-content-image" src="{{ photo.image }}" />
	                        </div>
	                    </a></li>
                    {% endfor %}""")
                    
        c = Context({'photo_list': photo_list, 'screen_name': screen_name, 'avatar_large': avatar_large})
        html = t.render(c)
        response = HttpResponse(html)
        return response

def logout(request):
    weibo_client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
    if request.COOKIES.has_key('access_token') is False:
        DEBUG_TRACE.debug("Has no acccess token")
        return HttpResponseRedirect(CALLBACK_URL)
    else:
        access_token = request.COOKIES['access_token']
        expires_in = request.COOKIES['expires_in']
        uid = request.COOKIES['uid']
        weibo_client.set_access_token(access_token, expires_in)
        weibo_client.get.account__end_session()

def debug(request):
    access_token = request.COOKIES['access_token']
    expires_in = request.COOKIES['expires_in']
    uid = request.COOKIES['uid']
    expires_date = datetime.datetime.fromtimestamp(float(expires_in))
    response = HttpResponse('''
        <html>
          <body>
            <p>access token is: %s</p>
            <p>user id is: %s</p>
            <p>expire date is: %s</p>
          </body>
        </html>''' % (access_token, uid, expires_date))
    return response
    
def hello(request):
    return HttpResponse("Hello world")
