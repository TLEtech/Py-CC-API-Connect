import random

def prepare_payload_string(api_string):
    api_string = str(api_string)
    api_string = api_string.replace("'", '"')
    api_string = api_string.replace("{", "{\n    ")
    api_string = api_string.replace("}", "\n}")
    api_string = api_string.replace(",", ",\n    ")
    api_string = api_string.replace("}]", "}\n]")
    api_string = api_string.replace("[{", "[\n{")
    return api_string


def create_test_range(source):
    range_total = 200
    list_length = len(source)
    start_int = random.randrange(0,(list_length // 2))
    end_int = start_int + range_total
    test_range = source[start_int:end_int]
    return test_range


def find_contact(list, id):
    for entry in list:
        if entry['contact_id'] == id:
            return entry
        elif entry['contact_id'] != id:
            return 'could not find contact_id'


def find_company(list, company):
    for entry in list:
        if entry['company_name'].lower() == company.lower():
            return entry
        elif entry['company_name'].lower() != company.lower():
            return 'could not find company'


def local_find_email(list, email):
    for entry in list:
        if entry['ContactEmailAddr'] == email:
            return entry
        else:
            return 'could not find email'


def local_find_custid(list, custid):
    for entry in list:
        if entry['CustID'] == custid:
            return entry
        else:
            return 'could not find custid'

