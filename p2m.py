#!bin/python3

########Help to install#######
#python3 -m venv .
#source bin/activate
#pip install pymysql
#pip install pymupdf
#############################

########################
#########config#########
logfile='/var/log/ehospital.log'
########################

import pymupdf
from pprint import pprint
import datetime,fcntl,os, logging, shutil,time, sys
import mysql_lis
#from file_management_lis import file_management_lis

#For mysql password
sys.path.append('/var/gmcs_config')
import astm_var_clg as astm_var

#for log file
logging.basicConfig(filename=logfile,level=logging.DEBUG)  

'''
 0 ['1122',
 1 'POOJA\nPURUSHOTTAM\nKUMAR SINGH',
 2 '15-03-2025\n10.28.11 AM',
 3 '20250088836',
 4 'F',
 5 '15-03-\n1998',
 6 '27 Y',
 7 'Orthopaedics',
 8 'Unit6',
 9 'OPD-6 (Orthopaedic\nOPD)',
 10 'New',
 11 'General/\nRs. 5.0',
 12  'walkin_opd',
 13  '-'],
 
 
 CREATE TABLE `log_entry` (
  `name` varchar(100) NOT NULL,
  `value` varchar(1000) NOT NULL,
  `help` varchar(1000) NOT NULL,
  PRIMARY KEY (`name`)
)


CREATE TABLE `ehospital` (
  `UHID` varchar(100) NOT NULL,
  `visit_date` varchar(100) DEFAULT NULL,
  `prefix` varchar(100) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `middlename` varchar(100) DEFAULT NULL,
  `surname` varchar(100) DEFAULT NULL,
  `sex` varchar(100) DEFAULT NULL,
  `DOB` varchar(100) DEFAULT NULL,
  `billing_type` varchar(100) DEFAULT NULL,
  `department` varchar(100) DEFAULT NULL,
  `unit` varchar(100) DEFAULT NULL,
  `clinic` varchar(100) DEFAULT NULL,
  `address` varchar(100) DEFAULT NULL,
  `f8` varchar(100) DEFAULT NULL,
  `f10` varchar(100) DEFAULT NULL,
  `f11` varchar(100) DEFAULT NULL,
  `f15` varchar(100) DEFAULT NULL,
  `f16` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`UHID`)
) 
'''
collection_string=''    

def log_and_display(log_data,display=0):
  global collection_string
  logging.debug(log_data)
  if(display!=0):
    collection_string=collection_string+'<hr><pre>{}</pre>'.format(log_data)
    
def pdf2mysql_io(file_data_as_string,from_page,to_page):
  global collection_string
  #doc = pymupdf.open("x.pdf")  # open document
  doc=pymupdf.Document(stream=file_data_as_string) #direct tring data

  logging.debug("length of doc:{}".format(len(doc)))

  m=mysql_lis.mysql_lis()
  link=m.get_link(astm_var.my_host,astm_var.my_user,astm_var.my_pass,astm_var.my_db)

  log_sql='insert into log_entry (name,value) values("ehospital_last_visit_date",%s ) on duplicate key update value=%s';
  

  sql='insert into ehospital \
  (\
    `UHID`, `visit_date`, `prefix`, `name`, `middlename`, `surname`, `sex`, `DOB`, `f8`, `billing_type`, `f10`, `f11`, `department`, `unit`, `address`, `f15`, `f16`, `clinic` \
  )\
  values\
  (\
   %(UHID)s, %(visit_date)s, %(prefix)s, %(name)s, %(middlename)s, %(surname)s, %(sex)s, %(DOB)s, %(f8)s, %(billing_type)s, %(f10)s, %(f11)s, %(department)s, %(unit)s, %(address)s, %(f15)s, %(f16)s, %(clinic)s\
  )\
   on duplicate key update\
  `visit_date`=%(visit_date)s, `department`=%(department)s, `unit`=%(unit)s, `clinic`=%(clinic)s , `address`=%(address)s \
  '

  from_page=min(from_page,1)

  to_page=min(len(doc),to_page)
  if(to_page<from_page):
    to_page=from_page
  
  
  #for i in range(0,len(doc)):
  for i in range(from_page-1,to_page):    #to ensure indexing and range do not include last
    page = doc[i] # get the 1st page of the document
    tabs = page.find_tables() # locate and extract any tables on page
    logging.debug(f"{len(tabs.tables)} found on {page}") # display number of found tables
    if tabs.tables:  # at least one table found?
      all_dt=tabs[0].extract()
      for dt in all_dt:
        #pprint(tabs[0].extract())  # print content of first table
        if(dt[4]=='M'):
          dt[4]='Male'
        elif(dt[4]=='F'):
          dt[4]='Female'
        else:
          dt[4]='Other'

        data_dictionary={'UHID': dt[3].replace("\n",""), 'visit_date':dt[2].replace("\n","") , 'prefix': '', 'name': dt[1].replace("\n",""), 'middlename': '', 
                            'surname': '', 'sex': dt[4].replace("\n",""), 'DOB': dt[5].replace("\n",""), 'f8': '', 
                            'billing_type': '', 'f10': '', 'f11': '', 'department': dt[7].replace("\n",""), 'unit': dt[8].replace("\n",""), 'address': '', 
                            'f15': '', 'f16': '', 'clinic': dt[9].replace("\n","")}
        log_and_display(data_dictionary,1)
        #logging.debug(data_dictionary)
        #logging.debug(pprint(data_dictionary))

        cur=m.run_query(link,sql,data_dictionary)
        log_cur=m.run_query(link,log_sql,(dt[2],dt[2]))
        m.close_cursor(log_cur)
        m.close_cursor(cur)
  m.close_link(link)
  return collection_string
  
  
'''
#plain code without function defination

doc = pymupdf.open("x.pdf") # open document
print("length of doc:{}".format(len(doc)))

m=mysql_lis.mysql_lis()
link=m.get_link(astm_var.my_host,astm_var.my_user,astm_var.my_pass,astm_var.my_db)

sql='insert into ehospital \
(\
  `UHID`, `mobile`, `prefix`, `name`, `middlename`, `surname`, `sex`, `DOB`, `f8`, `billing_type`, `f10`, `f11`, `department`, `unit`, `address`, `f15`, `f16`, `clinic` \
)\
values\
(\
 %(UHID)s, %(mobile)s, %(prefix)s, %(name)s, %(middlename)s, %(surname)s, %(sex)s, %(DOB)s, %(f8)s, %(billing_type)s, %(f10)s, %(f11)s, %(department)s, %(unit)s, %(address)s, %(f15)s, %(f16)s, %(clinic)s\
)\
 on duplicate key update\
`mobile`=%(mobile)s, `department`=%(department)s, `unit`=%(unit)s, `clinic`=%(clinic)s , `address`=%(address)s \
'

for i in range(0,len(doc)):
  page = doc[i] # get the 1st page of the document
  tabs = page.find_tables() # locate and extract any tables on page
  print(f"{len(tabs.tables)} found on {page}") # display number of found tables
  if tabs.tables:  # at least one table found?
    all_dt=tabs[0].extract()
    for dt in all_dt:
      #pprint(tabs[0].extract())  # print content of first table
      if(dt[4]=='M'):
        dt[4]='Male'
      elif(dt[4]=='F'):
        dt[4]='Female'
      else:
        dt[4]='Other'

      data_dictionary={'UHID': dt[3].replace("\n",""), 'mobile': '', 'prefix': '', 'name': dt[1].replace("\n",""), 'middlename': '', 
                          'surname': '', 'sex': dt[4].replace("\n",""), 'DOB': dt[5].replace("\n",""), 'f8': '', 
                          'billing_type': '', 'f10': '', 'f11': '', 'department': dt[7].replace("\n",""), 'unit': dt[8].replace("\n",""), 'address': '', 
                          'f15': '', 'f16': '', 'clinic': dt[9].replace("\n","")}
      logging.debug(data_dictionary)
      pprint(data_dictionary)
      cur=m.run_query(link,sql,data_dictionary)
      m.close_cursor(cur)

m.close_link(link)

'''
