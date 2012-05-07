The pitch
Are you looking to work in a certain company?
Want to know as soon as you get linkedin with someone who works in that company?
If so then login with to register the companies your interested in and as soon as somone from one of those companies joins your network you will receive an email to tell you so.

User stories
User can login/register to the app using LinkedIn credentials
User can add a company that will be watched for connections to the user
User can unregister from the app
[User receives an email daily with a list of the connections in the companies being watched]

How it works
User registers with the app using LinkedIn credentials that are validated with LinkedIn through Oauth2
When user goes to a page he is shown a list of companies he is watching
On the list of companies he can add to that list or delete one of the companies
A daily proc starts and for every user the full linkedin network is obtained
Then each person in the list is checked to see if they work in or have every worked in each company being watched.
If we have a match then that person gets added to the list and the URL to their linkedin profile is added to the email.
If there is more than 0 persons found to have worked in one of the companies then the email is constructed and sent to the email address of the user



