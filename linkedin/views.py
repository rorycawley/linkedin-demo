# Python
import oauth2 as oauth

import cgi
import simplejson as json
import datetime
import re
# Django
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
# Project
from linkedin.models import UserProfile
# from settings.py
consumer = oauth.Consumer(settings.LINKEDIN_TOKEN, settings.LINKEDIN_SECRET)
client = oauth.Client(consumer)
request_token_url = 'https://api.linkedin.com/uas/oauth/requestToken'
access_token_url = 'https://api.linkedin.com/uas/oauth/accessToken'
authenticate_url = 'https://www.linkedin.com/uas/oauth/authenticate'

# /login
def oauth_login(request):
    # Step 0. Get the current hostname and port for the callback
    if request.META['SERVER_PORT'] == 443:
     current_server = "https://" + request.META['HTTP_HOST']
    else:
     current_server = "http://" + request.META['HTTP_HOST']
     oauth_callback = current_server + "/login/authenticated"
    
    # Step 1. Get a request token from Provider.
    resp, content = client.request("%s?oauth_callback=%s" % (request_token_url,oauth_callback), "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response from Provider.")
    # Step 2. Store the request token in a session for later use.
    request.session['request_token'] = dict(cgi.parse_qsl(content))

    # Step 3. Redirect the user to the authentication URL.
    url = "%s?oauth_token=%s" % (authenticate_url,
        request.session['request_token']['oauth_token'])
    print url
    return HttpResponseRedirect(url)


# Provide the list of people who have worked in a given companay
# Input id of id of company, arrayOfPeopleIds
# Output list of names of people who have been in that company
# ID: 30591 Name: Adaptive Mobile
# ID: 22637 Name: Information Mosaic
# ID: 1337 Name: LinkedIn
def peopleWhoWorkedAtACompany(client, companyId, arrayOfPeopleIds):
    arrayOfConnections = []
    for connectionIndex in range(len(arrayOfPeopleIds)):
        userID = arrayOfPeopleIds[connectionIndex]
   
        # LIST OUT THE POSITIONS SOMEONE WORKED FOR
        url = "http://api.linkedin.com/v1/people/id=" + userID + ":(positions)"
        headers = {'x-li-format':'json'}
        resp, content = client.request(url, "GET", headers=headers)

        if resp['status'] != '200':
            print resp['status']
            continue
        else: 
            profile = json.loads(content)
            positions = profile['positions']
            if positions['_total'] > 0:
                listOfPositions = positions['values']
                for positionIndex in range(len(listOfPositions)):
                    aPosition = listOfPositions[positionIndex]
                    companyOfPosition = aPosition['company']
                    if companyOfPosition.has_key('id'): # SOME DON'T!!!
                        companyOfPositionId = companyOfPosition['id']
                        companyName = companyOfPosition['name']
                        if companyId == companyOfPositionId:
                            arrayOfConnections.append(userID)
                            break
                        
    print "Foo"
    return arrayOfConnections



# / (requires login)
@login_required
def home(request):
    html = "<html><body>"
    token = oauth.Token(request.user.get_profile().oauth_token,request.user.get_profile().oauth_secret)
    client = oauth.Client(consumer,token)
    headers = {'x-li-format':'json'}
    
    # https://developer.linkedin.com/documents/linkedin-api-resource-map
    url = "http://api.linkedin.com/v1/people/~/connections"
    
    # Get the person's id
    url = "http://api.linkedin.com/v1/people/~:(id,first-name,last-name,headline)"
    resp, content = client.request(url, "GET", headers=headers)
    html += '<h1>ID of the logged in user</h1>'
    if resp['status'] != '200':
        html += 'person not authenticated'
    else: 
        profile = json.loads(content)
        html += "ID: " + str(profile['id']) + "<br> Name: " + profile['firstName'] + " " + profile['lastName']
    userID = str(profile['id'])
    
    # Get the list of IDs of the user's connections
    url = "http://api.linkedin.com/v1/people/~/connections:(id,first-name,last-name)"
    resp, content = client.request(url, "GET", headers=headers)
    arrayOfConnections = []
    html += '<h1>IDs of the connections of the logged in user</h1>'
    if resp['status'] != '200':
        html += 'person not authenticated'
    else: 
        profile = json.loads(content)
        listOfProfiles = profile['values']
        if profile['_total'] > 0:
            for i in range(len(listOfProfiles)):
                aConnection = listOfProfiles[i]
                aConnectionId = str(aConnection['id'])
                arrayOfConnections.append(aConnectionId)

    
    html += '<h1>List of people who have worked at Fidelity</h1>'
    listOfPeople = peopleWhoWorkedAtACompany(client, 1307, arrayOfConnections)    # Fidelity
    for i in range(len(listOfPeople)):
        url = "http://api.linkedin.com/v1/people/id=" + str(listOfPeople[i]) + ":(first-name,last-name)"
        resp, content = client.request(url, "GET", headers=headers)
        if resp['status'] != '200':
            html += 'person not authenticated'
        else: 
            profile = json.loads(content)
            html += "<br> Name: " + profile['firstName'] + " " + profile['lastName']
            
    #listOfPeople = peopleWhoWorkedAtACompany(client, 30591, arrayOfConnections)    # Adaptive Mobile
    #listOfPeople = peopleWhoWorkedAtACompany(client, 22637, arrayOfConnections)    # Information Mosaic
    #listOfPeople = peopleWhoWorkedAtACompany(client, 1337, arrayOfConnections)    # LinkedIn
    
    return HttpResponse(html)



# /logout (requires login)
@login_required
def oauth_logout(request):
    # Log a user out using Django's logout function and redirect them
    # back to the homepage.
    logout(request)
    return HttpResponseRedirect('/')



#/login/authenticated/
def oauth_authenticated(request):
    # Step 1. Use the request token in the session to build a new client.
    token = oauth.Token(request.session['request_token']['oauth_token'],
        request.session['request_token']['oauth_token_secret'])
    if 'oauth_verifier' in request.GET:
        token.set_verifier(request.GET['oauth_verifier'])
    client = oauth.Client(consumer, token)
    # Step 2. Request the authorized access token from Provider.
    resp, content = client.request(access_token_url, "GET")
    if resp['status'] != '200':
        print content
        raise Exception("Invalid response from Provider.")
    access_token = dict(cgi.parse_qsl(content))
    headers = {'x-li-format':'json'}
    url = "http://api.linkedin.com/v1/people/~:(id,first-name,last-name,industry)"
    token = oauth.Token(access_token['oauth_token'],
        access_token['oauth_token_secret'])
    client = oauth.Client(consumer,token)
    resp, content = client.request(url, "GET", headers=headers)
    profile = json.loads(content)    
    # Step 3. Lookup the user or create them if they don't exist.
    firstname = profile['firstName']
    lastname = profile['lastName']
    identifier = profile['id']
    try:
        user = User.objects.get(username=identifier)
    except User.DoesNotExist:
        user = User.objects.create_user(identifier,
            '%s@linkedin.com' % identifier,
            access_token['oauth_token_secret'])                 
        user.first_name = firstname
        user.last_name = lastname
        user.save()
        # Save our permanent token and secret for later.
        userprofile = UserProfile()
        userprofile.user = user
        userprofile.oauth_token = access_token['oauth_token']
        userprofile.oauth_secret = access_token['oauth_token_secret']
        userprofile.save()
    # Authenticate the user and log them in using Django's pre-built
    # functions for these things.
    user = authenticate(username=identifier,
        password=access_token['oauth_token_secret'])
    login(request, user)
    return HttpResponseRedirect('/')
