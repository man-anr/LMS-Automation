import requests
import os
import datetime
from dateutil import parser
from bs4 import BeautifulSoup
import pandas as pd
from tabulate import tabulate


clear = lambda: os.system('cls')

def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if days < 0: 
        return "expired"
    else:
        return f"{days:02d}d "+ f"{hours:02d}h "+ f"{minutes:02d}m"

classroom_table = {
    "id": [],
    "name": []
}

ia_table = {
    "id": [],
    "subject": [],
    "activities": [],
    "due": [],
    "due date": [],
    "submission": []
}


url_login = "https://author.uthm.edu.my/loginscript.php"
data_login = {
    "txt_username":"INSERT USERNAME",
    "txt_password":"INSERT PASSWORD"
}

session = requests.Session()

session.get(url_login)
rq = requests.get(url_login)
shit = str(session.cookies)
bullshit = shit.replace("<RequestsCookieJar[<Cookie ","")
morebs = bullshit.replace(" for author.uthm.edu.my/>]>", "")



 
login_header = {
    "Host": "author.uthm.edu.my",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Length": "44",
    "Origin": "https://author.uthm.edu.my",
    "DNT": "1",
    "Connection": "keep-alive",
    "Referer": "https://author.uthm.edu.my/",
    "Cookie": morebs,
    "Sec-GPC": "1",
}

rq_login = requests.post(url_login, data=data_login, headers=login_header)



url_classroom_by_session = "https://author.uthm.edu.my/student/datalist_classroombysession.php"

classromm_session_data = {
    "session":"6",
    "semester":"1"
}

rq_classrom_by_session = requests.post(url_classroom_by_session, data=classromm_session_data, headers=login_header)
 
# print("Status Code", rq_login.status_code)
clear()
print("\n-> Log in successful") if (str(rq_login.json()) == "{'statuslog': 'success', 'who': 'student'}") else print("\n ->Log in unsuccessfull")
clear()
soup = BeautifulSoup(rq_classrom_by_session.text, "html.parser")
class_code = soup.find_all('input')
class_name = soup.find_all(class_='custom-control-description')
student_name = soup.find('span', style="font-size:smaller ;color: #ffffff")


# print(class_code.get('value'))

for rq_elem in class_code:
    # print("Processing elements...")
    classroom_id = rq_elem.get('value')
    # print("Class ID: %s" % classroom_id)
    classroom_table["id"].append(classroom_id)

for rq_elem in class_name:
    # print("Processing elements...")
    classroom_name = rq_elem.get_text()
    # print("Class Name: %s" % classroom_name)
    classroom_table["name"].append(classroom_name)



df = pd.DataFrame.from_dict(classroom_table, orient='index').transpose()


# data = df.head()
# print(df)




# print("Status Code", rq_classrom_by_session.status_code)
# print(rq_classrom_by_session.text)

url_ia = "https://author.uthm.edu.my/student/datalist_ia.php"
url_a_det = "https://author.uthm.edu.my/student/detail_assignment.php"
n_sub_a = 0
for i in range(len(classroom_table["id"])):

    ia_data = {
        "classroomid": classroom_table["id"][i]
    }

    rq_ia = requests.post(url_ia, data=ia_data, headers=login_header)

    # print(rq_ia.text)

    # print('leght diconary ', len(classroom_table["id"]))
    
    soup = BeautifulSoup(rq_ia.text, "html.parser")
    # print(soup)
    ia_header = soup.find_all('th')
    ia_act = soup.find_all('td')[1::6]#[1::2]
    ia_due = soup.find_all('td')[3::6]#[1::2]

    subject = (classroom_table["name"][i]).replace("(SEM1/20212022)", "").replace("FINAL EXAM: ", "")

    for rq_elem_act in ia_act:
        x = rq_elem_act.get_text()
        # print(x)
        activities = (x[:20] + '...') if len(x) > 20 else x
        ia_table["activities"].append(activities)
        ia_table["subject"].append(subject)
        a_id = rq_elem_act.get('onclick').replace("ia_detailassingment('", "").replace("')", "")
        ia_table["id"].append(a_id)

    for rq_elem_due in ia_due:
        y = rq_elem_due.get_text()
        # print(y)

        due_date = y.replace("@", "")
        try:
            date = parser.parse(due_date)
        except parser.ParserError:
            date = parser.parse("01 JAN 1999 01:01 PM")
        # print(hr)

        present = datetime.datetime.now()
        future = date
        difference = future - present

        due = convert_timedelta(difference)
        ia_table["due"].append(due)
        ia_table["due date"].append(str(due_date).zfill(21))




    
for i in range(len(ia_table["id"])):
    ia_det_data = {
        "id": ia_table["id"][i]
    }

    ia_det = requests.post(url_a_det, data=ia_det_data, headers=login_header)
    # print(ia_det.text)

    soup = BeautifulSoup(ia_det.text,'html.parser')
    spans = soup.find_all(style="color: #287E00")

    for span in spans:
        # print(span.get_text())
        n_sub_a += 1
    # print(n_sub_a)

    if n_sub_a == 0 or n_sub_a == "":
        ia_table["submission"].append("no file")
    elif n_sub_a > 1:
        ia_table["submission"].append(str(n_sub_a) + " files")
    else:
        ia_table["submission"].append(str(n_sub_a) + " file")
    
    # ia_table["submission"].append(str(n_sub_a) + " file(s)")
    n_sub_a = 0

# ia_det_last_data = {
#         "id": ia_table["id"][-1]
#     }

# ia_det_last = requests.post(url_a_det, data=ia_det_last_data, headers=login_header)
#     # print(ia_det.text)

# soup_last = BeautifulSoup(ia_det_last.text,'html.parser')
# spans_last = soup_last.find_all(style="color: #287E00")

# n_sub_a_last = 0
# for span in spans_last:
#     # print(span.get_text())
#     n_sub_a_last += 1
# # print(n_sub_a)

# if n_sub_a_last == 0 or n_sub_a_last == "0":
#     ia_table["submission"].append("no file")
# else:
#     ia_table["submission"].append(str(n_sub_a_last) + " files")












ia_df = pd.DataFrame.from_dict(ia_table, orient='index').transpose()
del ia_df['id']
ia_td = ia_df.sort_values(by='due', ascending=True)[
    ~ia_df.due.str.contains("expired")]
# print(ia_df)
ia_tablated = tabulate(ia_td, showindex=False, headers=ia_td.columns, tablefmt="fancy_grid")
clear()
print(ia_tablated, "\n")
print("Refreshed on: ", str(datetime.datetime.today()))


url_details = "https://author.uthm.edu.my/student/"
rq_details = requests.get(url_details)
# soup = BeautifulSoup(rq_details.text, "html.parser")
# print(soup)
# list = soup.find_all('select', id="sessionid")
# print(list)
# for i in list:
#     print(i['value'])
# print(len(ia_table["id"]))