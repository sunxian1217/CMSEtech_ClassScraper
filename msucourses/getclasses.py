from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import time
import pandas as pd
import re

def start():
    '''Install the selenium webdriver'''
    install = ChromeDriverManager().install()
    
    #TODO add code to hide chrome window
    
    #Setup Chrome driver 
    options = Options()
    #options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    #TODO change to seleiumum wait
    #WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "waitCreate")))
    
    # time.sleep(10)
    return driver
    
def scrape_class_list(html_doc):
    '''function written by Xian Sun to scrape the main result of a search'''
    soup = BeautifulSoup(html_doc, 'html.parser')
    values = []
    
    divs = soup.find_all("div", class_="ps-htmlarea")
    for div in divs:
        val = (div.get_text(strip=True))
        values.append(val)
    values = list(filter(lambda x: x != "", values))
    values.pop(0)
    
    reshaped_list = [values[i:i+6] for i in range(0, len(values), 6)]

    # Create a DataFrame from the reshaped list
    col_names = ['Course', 'Type', 'Section', 'Schedule', 'Dates', 'Instructor']
    df = pd.DataFrame(reshaped_list, columns=col_names)
    df[['Course Code', 'Course Name']] = df['Course'].str.split(':', 1, expand=True)
    df[['Type', 'Units']] = df['Type'].str.split('(', 1, expand=True)
    df[['Section', 'Class Nbr', 'Academic Session']] = df['Section'].str.split('/', 2, expand=True)
    df[['Days', 'Time']] = df['Schedule'].str.split(':', 1, expand=True)
    df[['Units','Status']] = df['Units'].str.split(')',1,expand=True)
    df[['Subject','Course Number']] = df['Course Code'].str.split(' ',1,expand=True)

    df = df.drop(['Course', 'Schedule','Course Code'], axis=1)
    df = df[['Subject','Course Number','Course Name','Type','Units','Status','Section','Class Nbr','Academic Session','Days','Time','Dates','Instructor']]
    df['Units'] = df['Units'].str.extract(r'(\d+(?:\.\d+)?)')
    df['Section'] = df['Section'].str.extract(r'(\d+(?:\.\d+)?)')
    df['Class Nbr'] = df['Class Nbr'].str.extract(r'(\d+(?:\.\d+)?)')
    return df

def get_semesters():
    #TODO this code will not be portable as new semesters become avaliable we need to scrap this as well.
    Semester = {'Summer 2020': "'SSR_CSTRMPRV_VW_DESCR$8'",
            'Fall 2020': "'SSR_CSTRMPRV_VW_DESCR$span$7'",
            'Spring 21': "'SSR_CSTRMPRV_VW_DESCR$span$6'",
            'Summer 21': "'SSR_CSTRMPRV_VW_DESCR$5'",
            'Fall 21': "'SSR_CSTRMPRV_VW_DESCR$4'",
            'Spring 22': "'SSR_CSTRMPRV_VW_DESCR$span$3'",
            'Summer 22': "'SSR_CSTRMPRV_VW_DESCR$2'",
            'Fall 22': "'SSR_CSTRMPRV_VW_DESCR$1'",
            'Spring 23': "'SSR_CSTRMPRV_VW_DESCR$0'",
            'Summer 23': "'SSR_CSTRMCUR_VW_DESCR$0'", 
            'Fall 23': "'SSR_CSTRMCUR_VW_DESCR$1'",
           'Spring 24': "'SSR_CSTRMCUR_VW_DESCR$2'",
           'Summer 24': "'SSR_CSTRMCUR_VW_DESCR$3'"}
    return Semester

def scrape_all_classes(driver):
    '''Function to return a dataframe from all classees after a search'''
    #TODO add output to show progress
    
    #TODO Put outer loop here to loop over multiple results pages
    df = scrape_class_list(driver.page_source)

    #TODO Put inner loop here to loop over each class iframe
    rownum = 1
    element = driver.find_element(By.ID, f"DESCR100$0_row_{rownum}") 
    element.click()
    time.sleep(20)
    
    driver.switch_to.frame(0)
    framebody = driver.page_source
    
    #TODO add framebody parser function here.
    
    return df

def getClassesByDepartment(department='CMSE', semester_name='Spring 23'):
    '''Specific function to get classes by department and semester'''
    print("WARNING: This function may take a while")
    
    driver = start()
    
    msuCoursesURL = "https://student.msu.edu/psc/public/EMPLOYEE/SA/c/NUI_FRAMEWORK.PT_AGSTARTPAGE_NUI.GBL?CONTEXTIDPARAMS=TEMPLATE_ID%3aPTPPNAVCOL&scname=MSU_AA_SCHEDULE_NEW0&PanelCollapsible=Y"
    driver.get(msuCoursesURL)
    
    #TODO change to seleiumum wait
    #WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "waitCreate")))
    time.sleep(20)
    
    # Make URL for a sepecific semester and click on it
    Semester = get_semesters()
    url = f"javascript:submitAction_win0(document.win0,{Semester[semester_name]});"
    driver.execute_script(url);
    
    #TODO change to seleiumum wait
    #WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "MSU_CLSRCH_WRK2_SUBJECT")))
    time.sleep(30)
    
    # Enter department string and hit search
    element = driver.find_element(By.ID, 'MSU_CLSRCH_WRK2_SUBJECT')  
    element.send_keys(department)
    url = f"javascript:submitAction_win0(document.win0,'MSU_CLSRCH_WRK_SSR_PB_SEARCH');"
    driver.execute_script(url);
    
    #WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
    time.sleep(20)
    
    classes = scrape_all_classes(driver)
    
    #driver.close()
    
    return classes