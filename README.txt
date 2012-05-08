The pitch
=========
Are you looking to work in a certain company?
Want to know as soon as you get linkedin with someone who works in that company?
If so then login with to register the companies your interested in and as soon as somone from one of those companies joins your network you will receive an email to tell you so.
I want to join a company and to properly prepare and get an inside view I would like to have a connection in that company.
I look in linkedin in and I see that no-one in my list of connections is in the company.
I would be good to get an alert as soon as someone in my list of connections either joins the company or becomes linked to someone in
that company.

User stories
============
User can login/register to the app using LinkedIn credentials
User can add a company that will be watched for connections to the user
User can unregister from the app
[User receives an email daily with a list of the connections in the companies being watched]

How it works
============
Create a web app where someone can log their interest in a company and receive a daily email when there are people in their network that have
worked or work in that company.
The administration of capturing the company or companies that the user is interested in is done with a web app. As is the capture of the
linkedin user's token that allows the app to query the user's profile.
[for the demo I have included that code for the daily job into the web app request to get instant response]
A daily job runs that for each registered user will iterate through each company the user is interested in and will call the LinkedIn API
to see if any on the user's connections have had a position that matches the company. For this example I have only considered first
level connections.
Any connections found to have had a position that matches the company is added to a list.
The end list is used to write to an email.
If there were no connections found to have positions in none of the companies registered then no email is sent.
A more optimised job would save the connections for a day and then see if there are any changes in the persons network.

Note: the connections API says:
You can only get the connections of the user who granted your
application access. You cannot get connections of that user's
connections. This implies that my app will only work on the 1st level
connections only.

What the demo app does
======================
0. Uses OAuth to get user to authenticate to linkedin and uses that to login to Django app
1. Uses the id of company that the user seeks to work for.
2. Get the list of people in the users network
3. For each person, get the list of companies they worked for and see if they work for now or in the past the same company id
4. Outputs the list of people in the user's network that has a position in their profile that matches the company

The parts of the API that are used
===================================
Oauth
I obtained the API key and secret key from the developer portal, this allows my app to get a request token from the LinkedIn server.
I then send the request token to the server to get a URL for the user to login using their LinkedIn credentials and the access token is then
returned.
The access token is then saved for that user so it can be reused.
The access token is used to sign requests to get user data from the linkedin APIs.
This is more secure than asking a user to provide their linkedin username and password.
The user is authenticated into the Django authentication system using the access token and the LinkedIn identifier.
Once the user is authenticated a request to the LinkedIn API uses the user profile to access the request token and the secret token
necessary to make a request.
People API
To obtain a persons linkedIn profile
To get detail on the user logged in
Also to get detail on a connection to find out their list of positions

Connections API
Used to get the list of 1st level connections of the user



How it's developed
==================
Eclipse with PyDev
I found the linkedin developer thread useful for finding answers to my
newbie questions: e.g. https://developer.linkedin.com/thread/2427
I found Quora useful: e.g.
http://www.quora.com/Why-doesnt-the-LinkedIn-API-provide-email-addresses
 and Stackoverflow: e.g.
http://stackoverflow.com/questions/9981286/linkedin-rest-api-cant-send-message-couldt-parse-mailbox-item-document-error
I found this blog useful:
http://www.princesspolymath.com/princess_polymath/?p=511
I played with this tool initially: https://apigee.com/console/linkedin
I used this REST console from LinkedIn:
http://developer.linkedinlabs.com/rest-console/


