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
headers = {'x-li-format':'json'}

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

# NB: This doesn't below in the web app
# this would be in a scheduled job running daily
# with the and an LinkedIn email would be sent at the end
#
# Provide the list of people who have worked in a given companay
def getPeopleWhoWorkedAtACompany(client,companyId, userId):    
    # Get the list of IDs of the user's connections
    url = "http://api.linkedin.com/v1/people/~/connections:(id,first-name,last-name)"
    resp, content = client.request(url, "GET", headers=headers)
    arrayOfConnectionIds = []
    if resp['status'] != '200':
        return [] # can't get anything back
    else: 
        profile = json.loads(content)
        listOfProfiles = profile['values']
        if profile['_total'] > 0:
            for i in range(len(listOfProfiles)):
                aConnection = listOfProfiles[i]
                aConnectionId = str(aConnection['id'])
                arrayOfConnectionIds.append(aConnectionId)
                
    # For each connection, get the list of positions and see if any match the company
    arrayOfConnectionsWhoWorkedForCompany = []
    
    for connectionIndex in range(len(arrayOfConnectionIds)):
        personUserID = arrayOfConnectionIds[connectionIndex]
   
        url = "http://api.linkedin.com/v1/people/id=" + personUserID + ":(positions)"
        resp, content = client.request(url, "GET", headers=headers)

        if resp['status'] != '200':
            continue # problem getting the list of connections (throttleing or connection errror)
        else: 
            profile = json.loads(content)
            positions = profile['positions']
            if positions['_total'] > 0:
                listOfPositions = positions['values']
                for positionIndex in range(len(listOfPositions)):
                    aPosition = listOfPositions[positionIndex]
                    companyOfPosition = aPosition['company']
                    if companyOfPosition.has_key('id'): # SOME DON'T since they were gone pre-Linkedin or not registered
                        companyOfPositionId = companyOfPosition['id']
                        companyName = companyOfPosition['name']
                        if companyId == companyOfPositionId: # the comapny id's match so great
                            arrayOfConnectionsWhoWorkedForCompany.append(personUserID) # Add this user since they work(d) in the company
                            break # found a position that matches this person to the company, done it!
    return arrayOfConnectionsWhoWorkedForCompany

def outputPeopleWhoHaveWorkedAtACompany(client, companyName, companyId, userId):
    html = '<h1>People in my network who have worked at ' + companyName + '</h1>'
    
    listOfPeopleWhoWorkedInCompany = getPeopleWhoWorkedAtACompany(client,companyId, userId)
    if len(listOfPeopleWhoWorkedInCompany) == 0:
        html += 'No one in my network has worked in ' + companyName
    else:
        for i in range(len(listOfPeopleWhoWorkedInCompany)):
            url = "http://api.linkedin.com/v1/people/id=" + str(listOfPeopleWhoWorkedInCompany[i]) + ":(first-name,last-name)"
            resp, content = client.request(url, "GET", headers=headers)
            if resp['status'] != '200':
                html += 'person not authenticated'
            else: 
                profile = json.loads(content)
                html += "<br> Name: " + profile['firstName'] + " " + profile['lastName']
                # I could use the Communications API to inmail them automatically here
                
    return html

# / (requires login)
@login_required
def home(request):
    html = "<html><body>"
    token = oauth.Token(request.user.get_profile().oauth_token,request.user.get_profile().oauth_secret)
    client = oauth.Client(consumer,token)
    
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
    userId = str(profile['id']) # This is the userId of the LinkedIn authenticated user
                


    # Let's list out the people who are in the network
    FIDELITY_ID = 1307
    INFORMATIONMOSAIC_ID = 22637
    ADAPTIVEMOBILE_ID = 30591
    html += outputPeopleWhoHaveWorkedAtACompany(client, 'FIDELITY', FIDELITY_ID, userId)
    html += outputPeopleWhoHaveWorkedAtACompany(client, 'INFORMATIONMOSAIC', INFORMATIONMOSAIC_ID, userId)
    html += outputPeopleWhoHaveWorkedAtACompany(client, 'ADAPTIVEMOBILE', ADAPTIVEMOBILE_ID, userId)


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
    url = "http://api.linkedin.com/v1/people/~:(id,first-name,last-name)"
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
