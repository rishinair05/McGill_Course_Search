import csv
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import re
import pandas as pd

root_url = "https://www.mcgill.ca/study/2023-2024/courses/search"
page_path = "?page="

course_information = []

course_names = []
course_department = []
course_descriptions = []
course_terms = []
course_instructors = []
course_prerequisites = []

page_url = ""
number_of_pages = 528

course_urls = []

i = 0
while i < number_of_pages:
    if i%10 == 0 and i != 0:
        print("Obtained course links from the first " + str(i) + "/527 pages.")
    if i%100 == 0 and i != 0:
        time.sleep(10)

    if i == 0:
        page_url = root_url
        get_html = urlopen(page_url)
        time.sleep(1)
        current_page = get_html.read()
        soup = bs(current_page, 'lxml')
        j = 0
        for link in soup.find_all('a', href=True):
            if "/study/2023-2024/courses/" in link['href'] and j < 20 and link['href'] != '/study/2023-2024/courses/search':
                course_urls.append('http://mcgill.ca' + link['href'])
                j = j+1
        print("Obtained course links from home page.")

    elif i == 527:
        page_url = root_url + page_path + str(i)
        get_html = urlopen(page_url)
        time.sleep(1)
        current_page = get_html.read()
        soup = bs(current_page, 'lxml')
        j = 0
        for link in soup.find_all('a', href=True):
            if "/study/2023-2024/courses/" in link['href'] and j < 11 and link['href'] != '/study/2023-2024/courses/search':
                course_urls.append('http://mcgill.ca' + link['href'])
                j = j+1
        print("Obtained all course links (10551 links) from 527/527 pages. Now extracting course information from each link.")

    else:
        page_url = root_url + page_path + str(i)
        try:
            get_html = urlopen(page_url)
        except ConnectionError:
            print("page" + str(i+1) + "has failed")
            page_url = root_url + page_path + str(i+1)
            get_html = urlopen(page_url)
            i = i+1
        time.sleep(1)
        current_page = get_html.read()
        soup = bs(current_page, 'lxml')
        j = 0
        for link in soup.find_all('a', href=True):
            if "/study/2023-2024/courses/" in link['href'] and j < 20 and link['href'] != '/study/2023-2024/courses/search':
                course_urls.append('http://mcgill.ca' + link['href'])
                j = j+1
    
    i = i + 1

'''
get_html = urlopen(root_url)
current_page = get_html.read()
soup = bs(current_page, 'lxml')

i = 0
for link in soup.find_all('a', href=True):
    if "/study/2023-2024/courses/" in link['href'] and i < 20 and link['href'] != '/study/2023-2024/courses/search':
        course_urls.append('http://mcgill.ca' + link['href'])
        i = i+1
'''
url_chunks = [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 10551]

for k in range(len(url_chunks)):
    if k == 0:
        j = 0
    else:
        j = url_chunks[k-1]
    l = url_chunks[k]
    while j < l:
        try:
            get_course_html = urlopen(course_urls[j])
        except ConnectionError:
            get_course_html = urlopen(course_urls[j+1])
            print("Course link#" + str(j) + " has been skipped")
            course_names.append("")
            course_descriptions.append("")
            course_department.append("")
            course_terms.append("")
            course_instructors.append("")
            course_prerequisites.append("")
            j = j+1

        time.sleep(1)
        current_course_page = get_course_html.read()
        soup = bs(current_course_page, 'lxml')

        tmp_text = soup.find_all('p')
        course_names.append(str(soup.title)[7:][:-40])

        i=0
        tmp_line = ""
        for line in tmp_text:
            tmp_line = str(line.text)
            tmp_line = re.sub(' +', ' ', tmp_line)
            if "Offered by:" in str(line):
                course_department.append(tmp_line.lstrip())
            elif i == 1:
                course_descriptions.append(tmp_line.lstrip())
            elif "Terms" in str(line):
                course_terms.append(tmp_line.lstrip())
            elif "Instructors" in str(line):
                course_instructors.append(tmp_line.lstrip())
            elif "Prerequisite" in str(line):
                course_prerequisites.append(tmp_line.lstrip())
            i = i+1
        if len(course_department) < j+1:
            course_department.append("")
        if len(course_descriptions) < j+1:
            course_descriptions.append("No Available Description")
        if len(course_terms) < j+1:
            course_terms.append("")
        if len(course_instructors) < j+1:
            course_instructors.append("")
        if len(course_prerequisites) < j+1:
            course_prerequisites.append("")
        if len(course_department) > j+1:
            course_department.pop()
        if len(course_descriptions) > j+1:
            course_descriptions.pop()
        if len(course_terms) > j+1:
            course_terms.pop()
        if len(course_instructors) > j+1:
            course_instructors.pop()
        if len(course_prerequisites) > j+1:
            course_prerequisites.pop()

        if j%10 == 0 and j!=0:
            print("Information from " + str(j) + "/10551 courses have been extracted")
        
        if j%100 == 0 and j!=0:
            time.sleep(10)
        
        if j == len(course_urls):
            print("All course information has been extracted. Now packing into dataframe")
        
        j = j + 1

    for i in range(len(course_names)):
        course_information.append([course_names[i], course_descriptions[i], course_department[i], course_terms[i], course_instructors[i], course_prerequisites[i]])
        #course_information has several repeated entries. Go into shell to take last 10551 entries in dataframe.

    df = pd.DataFrame(course_information, columns = ['Course Name', 'Description', "Department", "Terms", "Instructors", "Prerequisites"])

    print(df)

    df_file_name = "mcgill_courses_dataframe.pkl" 
    df.to_pickle(df_file_name)  
    print("Dataframe successfully saved to " + df_file_name)