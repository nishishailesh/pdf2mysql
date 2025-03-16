#!bin/python3




#python3 -m venv .
#source bin/activate
#pip install pymysql
#pip install pymupdf


import pymupdf
from pprint import pprint
import datetime,fcntl,os, logging, shutil,time, sys
import mysql_lis

#For mysql password
sys.path.append('/var/gmcs_config')
import astm_var_clg as astm_var

#for log file
logging.basicConfig(filename='/var/log/ehospital.log',level=logging.DEBUG)  

def save_data(data_dictionary):

  m=mysql_lis.mysql_lis()
  #link=m.get_link(astm_var.my_host,astm_var.my_user,astm_var.my_pass,astm_var.my_db)
  link=m.get_link("stem.gmcsurat.edu.in","cluser","Tbsnn@420","clg")

  #not that %s becomes %(name)s
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
  cur=m.run_query(link,sql,data_dictionary)
  m.close_cursor(cur)
  m.close_link(link)


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
'''

doc = pymupdf.open("x.pdf") # open document
print("length of doc:{}".format(len(doc)))

m=mysql_lis.mysql_lis()
#link=m.get_link("stem.gmcsurat.edu.in","cluser","Tbsnn@420","clg")
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
      #save_data(data_dictionary)
      cur=m.run_query(link,sql,data_dictionary)
      m.close_cursor(cur)

m.close_link(link)
