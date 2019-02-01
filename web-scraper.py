# Blackboard WebScrapper
# CSE 485
# Andrew Bui

#########################################
# Login
# Start at discussion board overview
# Parse and collect all links to threads
# for all thread links:
#     Download page
#     Parse page and write to json
#########################################

###############
# TO DO:
# q/a count?
# grab classname + postdate from blackboard
###############

import os,time,sys,io,re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

##### SETUP FOR CHROME AWS #######
'''
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1280x1696')
chrome_options.add_argument('--user-data-dir=/tmp/user-data')
chrome_options.add_argument('--hide-scrollbars')
chrome_options.add_argument('--enable-logging')
chrome_options.add_argument('--log-level=0')
chrome_options.add_argument('--v=99')
chrome_options.add_argument('--single-process')
chrome_options.add_argument('--data-path=/tmp/data-path')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--homedir=/tmp')
chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
chrome_options.binary_location = os.getcwd() + "/bin/headless-chromium"
'''
################################


# --initial variables -- #
os.environ["PATH"] += os.pathsep + r' <PATH TO CHROMEDRIVER> '
userKey = "<ASU USER ID>"
passKey = "<ASU PASSWORD>"
# browser = webdriver.Chrome(chrome_options=chrome_options)
browser = webdriver.Chrome()
wait = WebDriverWait(browser, 15)

# get past login screen
def login(url):
    #credentials
    browser.get(url)
    username = browser.find_element_by_id("username")
    password = browser.find_element_by_id("password")
    username.send_keys(userKey)
    password.send_keys(passKey)    
    
    #submit
    browser.find_element_by_xpath("//input[@type='submit' and @value='Sign In']").click()    
    return

def grabLinks(url):
    browser.get(url)
    links = browser.find_elements_by_xpath("//a[@href]")        
    regex = "https://myasucourses.asu.edu/webapps/discussionboard/do/forum"
    
    topicLinks = []
    for link in links:
        link = link.get_attribute("href")
        if re.match(regex, str(link)):
            topicLinks.append(link)
    
    return topicLinks

# grab all links from discussionboard overview
def threadLinks(url):
    browser.get(url)
    links = browser.find_elements_by_xpath("//a[@href]")        
    
    regex = "https://myasucourses.asu.edu/webapps/discussionboard/do/message\?action\=list"
    #f= open('test.txt','w') # debug. write urls to textfile
    
    threads = [] 
    for link in links:
        link = link.get_attribute("href")
        if re.match(regex, str(link)):
            threads.append(link)
            #print(link)
    return threads

# download db thread html
# then parse and add to json
def dlThread(url,j):
    browser.get(url)
    html = browser.page_source

    
    #time.sleep(5)    #wait for js to load thread
    # page load, instead of flat time
    WebDriverWait(browser,30).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "dbThreadBody")))
    WebDriverWait(browser,30).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "vtbegenerated")))

    #get thread content
    thread = browser.find_element_by_id('content')
    thread = thread.get_attribute('innerHTML')    
    parseHTML(thread,j)
    return

### remove html artifacts
def cleanText(str):    
    str = str.replace('<div class="vtbegenerated">','').replace('</div>','')
    str = str.replace('</p>','').replace('<p>','')
    str = str.replace('<ul>','').replace('</ul>','')
    str = str.replace('<li>','').replace('</li>','')
    str = str.replace('\n', '').replace('<br>','').replace('</br>','')
    return str

# parse json, add save to json
def parseHTML(thread,j):
    soup = BeautifulSoup(thread, features="html.parser")
    #q - first post
    print("Question:")
    q = soup.find('div', {'class':'vtbegenerated'})
    q = cleanText(str(q))
    print(str(q) + "\n")
    ###
    j.write("\t\t{\n")
    j.write("\t\t\t\"q\": " + "\"" + str(q) + "\",\n")

    #instructor responses
    for node in soup.findAll('div', {'class':'msg-nexus'}):
        hasInstructorResponse = node.find('span', {'class':'author_props'})        
        if (hasInstructorResponse != None):
            print(cleanText(str(hasInstructorResponse)))
            ans = node.find('div', {'class':'vtbegenerated'})
            if (ans != None):
                print("instructor response:")
                ans = cleanText(str(ans))
                print(ans)

                ####
                j.write("\t\t\t\"a\": " + "\"" + str(ans) + "\"\n\t\t},\n")

    
    print("\n")
    # get date
    '''
    for node in soup.findAll({'class':'db_msg_age'}):
        print(node)
    '''    
    # peer responses usually not helpful
    # commented out for now
    '''
    #peer response
    for node in soup.findAll('div', {'class':'msg-nexus'}):
        a = node.find('span', {'class':'author_props'})
        if (a == None):
            b = node.find('div', {'class':'vtbegenerated'})
            if (b != None):
                print("Peer Response:")
                b = str(b).replace('<div class="vtbegenerated"><p>','').replace('</p>','').replace('<p>','').replace('</div>','')
                print(b)
    '''
    return

def lambda_handler():
    # login
    loginURL = "https://weblogin.asu.edu/cas/login?service=https%3A%2F%2Fweblogin.asu.edu%2Fcgi-bin%2Fcas-login%3Fcallapp%3Dhttps%253A%252F%252Fweblogin.asu.edu%252Fblackboard-sso%252Fauthn%253Finit%253Dfalse%2526d%253Dmyasucourses.asu.edu"
    login(loginURL)
    
    # grab links
    discBoard = 'https://myasucourses.asu.edu/webapps/discussionboard/do/conference?toggle_mode=read&action=list_forums&course_id=_385125_1&nav=discussion_board_entry&mode=view'
    topicLinks = grabLinks(discBoard)

    #create json file
    j = open('bb.json','w',encoding='utf-8')
    j.write('{\n')
    j.write('\t\"CSE470\": [\n')
    
    #grab thread links
    # ERASE BREAKS TO GRAB ALL LINKS
    for link in topicLinks:
        threads = threadLinks(link)
        for thread in threads:            
            dlThread(thread,j)
        break
        

    # end json file
    j.write("\t],\n")
    j.write("\t\"title\": \"blackboard scrape\"\n")
    j.write("}")
    j.close()
    
    browser.quit()
    return

lambda_handler()