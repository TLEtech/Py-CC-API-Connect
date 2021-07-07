import random
import openpyxl
import requests
import base64
import re
import yaml
import pandas as pd
import json
import sqldata
from datetime import date, datetime
import collections
import cc_api_connect_functions as func
import mail

with open("config.yml", 'r') as configInfo:
    config = yaml.safe_load(configInfo)

# Class Custom Fields
cust_ID = config['CustomFields']['custID']
rep_ID = config['CustomFields']['rep']
contact = config['CustomFields']['contact']
dep = config['CustomFields']['department']
add = config['CustomFields']['apiadd']

# Create a class for formatting data for post calls. Will add this to another file soon.
class PostContact:
    def __init__(self, CustID, Company, Email, Contact, Lists, Dep, Add):
        self.CustID = CustID
        self.Company = Company
        self.Email = Email
        self.Lists = Lists
        self.Contact = Contact
        self.Dep = Dep
        self.Add = Add

    def to_post_payload(self):
        new_payload = {"email_address": {"address": self.Email},
                       "company_name": self.Company,
                       "create_source": "Account",
                       "custom_fields": [{"custom_field_id": 'a07b9bd0-ba8c-11e3-9f0e-d4ae528eaba9', "value": self.CustID},
                                         {"custom_field_id": '87cd90b0-b94b-11e5-9b31-d4ae528eaba9', "value": self.Contact},
                                         {"custom_field_id": '839075c6-1576-11eb-8315-fa163eaf1c42', "value": self.Dep},
                                         {"custom_field_id": '8cd2e50c-b8e0-11eb-a5e5-fa163eaf1c42', "value": self.Add}],
                       "list_memberships": self.Lists}
        return new_payload



# Functions
def update_token(headers, refresh_token):
    token_params = (
        ('refresh_token', refresh_token),
        ('grant_type', 'refresh_token'),
    )
    token_response = requests.post('https://idfed.constantcontact.com/as/token.oauth2',
                                   headers=headers, params=token_params)
    return token_response


# Variables
# Import from config.yml
API_ID = 'Post-New'
username = config['Creds']['user']
password = config['Creds']['userPW']
custid_field = config['Misc']['custid_field']
api_url = config['URL']['apibase']
csv_contacts_export_url = config['Endpoints']['exportCSV']
base_url = config['URL']['oAuth2Base']
client_id = config['Creds']['ID']
client_secret = config['Creds']['secret']
token_url = config['URL']['token']
local_url = config['URL']['callback']
code = config['Misc']['code']
scopes = config['Params']['scopes']
response_type = config['Params']['responseType']
redirect_uri = config['URL']['redirect']
grant_type = config['Params']['grantType']
b64string = config['Creds']['b64string']
contacts_url = config['URL']['contacts']
email_address_blank = {'address': ''}
email_address_blank_backup = {'address': '', 'permission_to_send': 'implicit', 'created_at': '',
                       'updated_at': '', 'opt_in_source': 'Account',
                       'opt_in_date': '', 'confirm_status': 'off'}

# list variables
L_blades = config['Lists']['blades']
L_tile = config['Lists']['tile']
L_abrasives = config['Lists']['abrasives']
L_tools = config['Lists']['tools']
L_all = config['Lists']['all']
L_welders = config['Lists']['welders']
L_new = config['Lists']['new']

# Compound/RE variables
base_code = '{url}/code?={code}'.format(url=local_url, code=code)
auth_url = (base_url + "?client_id=" + client_id + "&redirect_uri=" + redirect_uri + "&response_type=" + response_type
            + "&scope=" + scopes)
print(auth_url)
url_code = input('Enter the URL:\n')
url_rx = '^https:\/\/.*\/\?code=(.*)'
m = re.match(url_rx, url_code)
code = m.groups(1)[0]



# Still need these? Probably not. Will probably remove later
client_string = '{client_id}:{client_secret}'.format(client_id=client_id, client_secret=client_secret)
pre_header = bytes("Basic ", 'utf-8')
encoded_string = base64.b64encode(client_string.encode('ascii'))

headers = {
    'authorization': 'Basic {0}'.format(b64string),
}

# API Call Parameter Variables

contacts_limit = 500
contacts_include = ['custom_fields', 'list_memberships']
params = (
    ('code', code),
    ('redirect_uri', redirect_uri),
    ('grant_type', grant_type),
    ('limit', contacts_limit),
    ('include', 'list_memberships,custom_fields')
)

response = requests.post('https://idfed.constantcontact.com/as/token.oauth2', headers=headers, params=params)
access_token = response.json()['access_token']
refresh_token = response.json()['refresh_token']

headers = {
    'Authorization': 'Bearer {access_token}'.format(access_token=access_token)
}

postHeaders = {
    'Authorization': 'Bearer {access_token}'.format(access_token=access_token),
    "Accept": "application/json",
    "Content-Type": "application/json"
}

data = {
    "token": access_token
}

update_token(headers, refresh_token)

print(response)

contacts_response = requests.get(contacts_url, headers=headers, params=params)
contacts_json_1 = (contacts_response.json())
contacts_json = (contacts_response.json())
contacts_list_1 = contacts_json_1['contacts']
contacts_list_full = contacts_json_1['contacts']

next_link = api_url + (contacts_json['_links']['next']['href'])
print('creating contacts_list_full list...')
while next_link:
    contacts_addon = requests.get(next_link, headers=headers,
                                  params=params).json()
    contacts_list_full.extend(contacts_addon['contacts'])
    print('contacts list contains ' + str(len(contacts_list_full)) + ' items')
    try:
        if contacts_addon['_links']['next']['href']:
            print('updating with next page...')
            next_link = api_url + requests.get(next_link, headers=headers, params=params).json()['_links']['next'][
                'href']
    except KeyError:
        print('reached end of contacts list. moving on...')
        break

# Gather lots of info for reference

# list of constant contact emails
cc_email_set = set()
for contact in contacts_list_full:
    try:
        if contact['email_address']['address'] not in cc_email_set:
            cc_email_set.add(contact['email_address']['address'].lower())
        else:
            continue
    except KeyError:
        continue

# import local data as JSON, oriented by records
DIT_update_list = sqldata.df.to_json(orient="records")
# parse into usable list of dicts (same as data retrieved by Constant Contact)
DIT_update_list = json.loads(DIT_update_list)
for cust in DIT_update_list:
    cust['CustID'] = int(cust['CustID'])

# Grab source emails
dit_email_set = set()
for entry in DIT_update_list:
    dit_email_set.add(entry['ContactEmailAddr'].lower())
print('unique emails from source database: ' + str(len(dit_email_set)))

# grab emails from source that don't exist in target
import_email_set = set()
for email in dit_email_set:
    if email not in cc_email_set:
        import_email_set.add(email)
print('unique emails from source database not in target: ' + str(len(import_email_set)))

# assemble initial email add package
initial_add_package = []
dev_mode = 1
dev_audit = []
for email in import_email_set:
    for contact in DIT_update_list:
        if contact['ContactEmailAddr'].lower() == email.lower():
            add = contact
            add['ContactEmailAddr'] = add['ContactEmailAddr'].lower()
            add['ContactName'] = add['ContactName'].title()
            add['lists'] = set()
            add['CustID'] = str(add['CustID'])
            initial_add_package.append(add)

# Step 2: Add lists if they exist in a prior custID
package_2 = initial_add_package
for entry in package_2:
    custid = entry['CustID']
    for contact in contacts_list_full:
        try:
            for field in contact['custom_fields']:
                if field['custom_field_id'] == custid_field:
                    if field['value'] == custid:
                        for list_entry in contact['list_memberships']:
                            entry['lists'].add(list_entry)
        except KeyError:
            if dev_mode == 1:
                print('Key Error: ' + str(entry))
            continue

# Step 3: add department field (Blades, Tools, etc)
package_3 = package_2
for entry in package_2:
    entry['Dep'] = ''
    if entry['Territory'] == '1113':
        entry['Dep'] = 'Tools'
    if entry['Territory'] == '1117':
        entry['Dep'] = 'Abrasives'
    if entry['Territory'] == '1713':
        entry['Dep'] = 'Blades'
    if entry['Territory'] == '1711':
        entry['Dep'] = 'Blades'
    if entry['Territory'] == '1712':
        entry['Dep'] = 'Blades'

# If lists do not exist in prior custID, add lists based on territory field
for entry in package_3:
    if len(entry['lists']) == 0:
        if entry['Territory'] == '1113':
            entry['lists'].add(L_tools)
        if entry['Territory'] == '1117':
            entry['lists'].add(L_abrasives)
        if entry['Territory'] == '1713':
            entry['lists'].add(L_blades)
        if entry['Territory'] == '1711':
            entry['lists'].add(L_blades)
        if entry['Territory'] == '1712':
            entry['lists'].add(L_blades)
        entry['lists'].add(L_all)
    else:
        continue

# Working on the final payload...
package_4 = []
for payload in package_3:
    payload['lists'] = list(payload['lists'])
    add = PostContact(payload['CustID'], payload['CustName'], payload['ContactEmailAddr'],
                              payload['ContactName'], payload['lists'], payload['Dep'],
                              API_ID).to_post_payload()
    package_4.append(add)


# Auditing: make sure each contact has lists.
counter = 0
lists = []
for entry in package_4:
    if len(entry['list_memberships']) == 0:
        counter = counter + 1
        lists.append(entry['company_name'])
print(str(counter) + ' additions without a list.')
print(lists)

testpost_audit = []
import_package = package_4

# Create an audit CSV so we know what was added
audit_package = []
for contact in package_3:
    audit_package_add = {'email_address': contact['ContactEmailAddr'],
                         'custID': contact['CustID'],
                         'company': contact['CustName'],
                         'department': contact['Dep'],
                         'date': str(date.today()),
                         'import_response': '',
                         'response_detail': ''}
    audit_package.append(audit_package_add)

print('Audit sheet will be created, containing ' + str(len(audit_package)) + ' contacts.')

# Send post API call to attempt creation of new contacts.
# Logs response codes, both successes and failures, for auditing.
counter = 0
for payload in import_package:
    payload_custid = ''
    for field in payload['custom_fields']:
        if field['custom_field_id'] == config['CustomFields']['custID']:
            payload_custid = field['value']
        else:
            continue
    final_payload = func.prepare_payload_string(str(payload))
    audit_add = payload
    post_response = requests.post(config['URL']['contacts'], data=final_payload, headers=postHeaders)
    audit_add['API_response'] = str(post_response)
    for contact in audit_package:
        try:
            if payload['email_address']['address'] == contact['email_address']:
                contact['import_response'] = audit_add['API_response']
        except KeyError:
            continue
    counter = counter + 1
    print(str(counter) + ': ' + payload['email_address']['address'] + ' - ' + str(post_response) + ' - ' +
          payload_custid)
    testpost_audit.append(payload)

# Add notes on the response types for easier understanding of audit workbook
# Will clean this up later with variables via config file
for contact in audit_package:
    if contact['import_response'] == '<Response [400]>':
        contact['response_detail'] = 'Bad request. Most likely contains an email input incorrectly.'
    if contact['import_response'] == '<Response [409]>':
        contact['response_detail'] = 'Email conflict - most likely the email already exists'
    if contact['import_response'] == '<Response [201]>':
        contact['response_detail'] = 'Success. New contact created.'
    else:
        continue


# Create dataframe with pandas and then export to file
audit_df = pd.DataFrame(audit_package)
audit_df.to_excel("Audits\Post\ConstantContact_API_Add_" + str(date.today()) + '.xlsx', index=False)
audit_file_path = "Audits\Post\ConstantContact_API_Add_" + str(date.today()) + '.xlsx'

# Email post audit attachment with selected parameters in config
mail.email_post_audit_attachment()

