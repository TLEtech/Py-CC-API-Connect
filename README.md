# Py-CC-API-Connect
Ongoing project involving connection to Constant Contact API using Python requests module.

A significant amount of credit goes to Kevin Tran (kevin@kqtran.com, kqtran.com), who was instrumental in getting the ball rolling with this project.

5-13-21
Project is just about ready to start rolling out to production. Only thing remaining is to make sure we have safeguards in place to prevent data loss.
After we verify that, and verify proper auditing and rollbacks (if necessary), we will start updating email addresses.
Future additions to work on are the following:
  1 - Complete automation: refresh token seems to not work completely. Have to get this working in order to fully automate
  2 - Web dashboard linking analysis/audits and visualizations for managers (in short, make this mess more user friendly)
  3 - Update other information: lists, campaigns, etc.

5-18-21
Ran into a significant issue that needs to be addressed.

Our environment identifies customers through the custom field CustID. through
working on this, we've found almost a thousand customers that have duplicate
CustIDs. Seeing as contacts on Constant Contact CANNOT have duplicate email
addresses, we need to find a way to remove the duplicate contacts from the
equation somehow.

My working idea is to target the duplicate contacts other than the most recently
updated one, change their emails, and delete them (I say change their emails
because a recently deleted email will still count in regards to the unique
email address).

After consulting with leadership, I will move forward with this plan if
approved.

Other than that, there is still some work to do for updating the contacts. The
main loop for updating is commented out at the bottom. Once the dupes are
resolved, we will uncomment and update.

5-19-21

Management (and me) concluded that adding new contacts would be a better, less
destructive option then updating existing contacts and potentially losing emails.
Created a new file (main_addnew.py) for this. This file utilizes a different
endpoint than my previous work, and builds upon the work in main.py.

Basic process of main_addnew.py:
  1 - Go through Oauth2 authorization process
  2 - Gather full contacts list from Constant contact
  3 - Compare list from above to data from local SQL server DB
  4 - From the two lists, create a separate list of emails that are on our local
    db but do not exist in Constant contact
  5 - Morph data as required by CC API. Add fields as needed based on certain
    parameters (for instance: mailing lists, department)
  6 - Morph each individual entry into a "post payload" and create a new contacts
    with the post payload through the POST contact API endpoint.
  7 - Document each change, the response (success or failure), and create an
    audit list of the changes made or not made.

So, the program works. It could still be cleaned up as far as syntax is
concerned, and there is more to add in order to make it more user friendly and
accessible via GUI/dashboards. But for now, success.

Will clean up syntax and organization + improve auditing at a later time.

-TLE

7/7/21
Cleaned up auditing, added functionality to automatically email audit
workbooks to authorized personnel.
