import csv
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import re
import pandas as pd

root_url = "https://www.mcgill.ca/study/2023-2024/courses/search?f%5B0%5D=field_faculty_code%3ASC"
page_path = "&page="

course_names = []
course_department = []
course_descriptions = []
course_terms = []
course_instructors = []
course_prerequisites = []

page_url = ""
number_of_pages = 528

course_urls = []

for i in range(68):
    if i%10 == 0 and i != 0:
        print("Obtained course links from the first " + str(i) + "/68 pages.")
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
    elif i == 67:
        page_url = root_url + page_path + str(i)
        get_html = urlopen(page_url)
        time.sleep(1)
        current_page = get_html.read()
        soup = bs(current_page, 'lxml')
        j = 0
        for link in soup.find_all('a', href=True):
            if "/study/2023-2024/courses/" in link['href'] and j < 3 and link['href'] != '/study/2023-2024/courses/search':
                course_urls.append('http://mcgill.ca' + link['href'])
                j = j+1
        print("Obtained all course links (1343 links) from 68/68 pages. Now extracting course information from each link.")
    else:
        page_url = root_url + page_path + str(i)
        get_html = urlopen(page_url)
        time.sleep(1)
        current_page = get_html.read()
        soup = bs(current_page, 'lxml')
        j = 0
        for link in soup.find_all('a', href=True):
            if "/study/2023-2024/courses/" in link['href'] and j < 20 and link['href'] != '/study/2023-2024/courses/search':
                course_urls.append('http://mcgill.ca' + link['href'])
                j = j+1    

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

j = 0
for j in range(len(course_urls)):
    get_course_html = urlopen(course_urls[j])
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
        if "Offered by" in str(line):
            course_department.append(tmp_line.lstrip())
        elif i == 1:
            course_descriptions.append(tmp_line.lstrip())
        elif "Term" in str(line):
            course_terms.append(tmp_line.lstrip())
        elif "Instructor" in str(line):
            course_instructors.append(tmp_line.lstrip())
        elif "requisite" in str(line):
            course_prerequisites.append(tmp_line.lstrip())
        i = i+1
    if "Offered by" not in str(tmp_text):
        course_department.append("")
    if "Term" not in str(tmp_text):
        course_terms.append("")
    if "Instructor" not in str(tmp_text):
        course_instructors.append("")
    if "requisite" not in str(tmp_text):
        course_prerequisites.append("")

    if j%10 == 0 and j != 0:
        print("Information from " + str(j) + "/1343 courses have been extracted")
    
    if i%100 == 0 and i != 0:
        time.sleep(10)
    
    if j == len(course_urls):
        print("All course information has been extracted. Now packing into dataframe")

course_information = []

for i in range(len(course_names)):
    course_information.append([course_names[i], course_descriptions[i], course_department[i], course_terms[i], course_instructors[i], course_prerequisites[i]])

df = pd.DataFrame(course_information, columns = ['Course Name', 'Description', "Department", "Terms", "Instructors", "Prerequisites"])

print(df)

df_file_name = "mcgill_science_courses_dataframe.pkl" 
df.to_pickle(df_file_name)  
print("Dataframe successfully saved to " + df_file_name)