#!/usr/bin/python3
#from bottle import route, run, template
from bottle import template, request, post, route, redirect
from datetime import datetime
from mysql_lis import mysql_lis
import sys, logging, bcrypt, csv, pprint
from functools import wraps
from io import StringIO
from p2m import pdf2mysql_io
#For mysql password
sys.path.append('/var/gmcs_config')
###########Setup this for getting database,user,pass for HLA database##########
import astm_var_clg as astm_var
##############################################################
logging.basicConfig(filename="/var/log/ehospital.log",level=logging.DEBUG)  

collection_string=''    
#this goes on increasing at each run. 
#wsgi create functions and use. 
#so it is not reset everytime page 
#reset when there is apache restart
#so zero out it at each route function
 
def log_and_display(log_data,display=0):
  global collection_string
  logging.debug(log_data)
  if(display!=0):
    collection_string=collection_string+'<hr><pre>{}</pre>'.format(log_data)
    
def tuple_to_html(tpl):
  str(tpl).replace(',','<li>').replace('(','<ul>').replace(')','</ul>').replace('{','<ul>').replace('}','</ul>')
  return tpl
  
def verify_user():
  if(request.forms.get("uname")!=None and request.forms.get("psw")!=None):
    uname=request.forms.get("uname")
    psw=request.forms.get("psw")
    logging.debug('username and password are provided')
    m=mysql_lis()
    con=m.get_link(astm_var.my_host,astm_var.my_user,astm_var.my_pass,astm_var.my_db)
    cur=m.run_query(con,prepared_sql='select * from user where user=%s',data_tpl=(uname,))
    user_info=m.get_single_row(cur)
    if(user_info==None):
      logging.debug('user {} not found'.format(uname))
      m.close_cursor(cur)
      m.close_link(con)
      return False
    m.close_cursor(cur)
    m.close_link(con)

    '''
    Python: bcrypt.hashpw(b'mypassword',bcrypt.gensalt(rounds= 4,prefix = b'2b')
    PHP:    password_hash('mypassword',PASSWORD_BCRYPT);

    Python:bcrypt.checkpw(b'text',b'bcrypted password')
    PHP: password_verify('text,'bcrypted password')
    '''
    
    #try is required to cache NoneType exception when supplied hash is not bcrypt
    try:
      if(bcrypt.checkpw(psw.encode("UTF-8"),user_info[2].encode("UTF-8"))==True):
        logging.debug('user {}: password verification successful'.format(uname))
        return True
      else:
        return False
    except Exception as ex:
      logging.debug('{}'.format(ex))
      return False
  else:
    logging.debug("else reached")
    return False
    
def decorate_verify_user(fun):
  def nothing():
    logging.debug("no username password available") 
    return template("failed_login.html",post_data="No post_data")
  @wraps(fun)   #not essential
  def do_it():
    if(verify_user()==True):
      logging.debug("#fun() reached...")
      return fun()  #return essential to return template
    else:
      return nothing() #return essential to return template
  logging.debug("function name of do_it is {}".format(do_it.__name__))
  return do_it
    
@route('/start', method='POST')
def start():
    post_data=request.body.read()
    uname=request.forms.get("uname")
    psw=request.forms.get("psw")
    if(verify_user()==True):
      return template("initial_page.html",post_data=post_data,uname=uname,psw=psw)
    else:
      return template("failed_login.html",post_data=post_data,uname=uname,psw=psw)
    
@route('/')
def index():
    return template("index.html")

@route('/upload_pdf', method='POST')
@decorate_verify_user
def upload_pdf():
  global collection_string
  collection_string=''
  all_file_objects= request.files
  
  from_page=int(request.forms.get("from_page"))
  to_page=int(request.forms.get("to_page"))
  
  log_and_display("all_file_objects keys:{}".format(all_file_objects.keys()),1)       #Class Files
  log_and_display("total file objects in this form:{}".format(len(all_file_objects)),1)
  for one_file_object in list(all_file_objects.keys()):                           #Class fileUpload
    log_and_display("one file object key:{}".format(one_file_object),1)
    log_and_display("one file object file io object:{}".format(all_file_objects[one_file_object].file),1)
    log_and_display("one file object name of form upload field:{}".format(all_file_objects[one_file_object].name),1)
    log_and_display("one file object raw_filename (original with spaces etc):{}".format(all_file_objects[one_file_object].raw_filename),1)    
    log_and_display("one file object headers (dict ype):{}".format(all_file_objects[one_file_object].headers),1)    
    log_and_display("one file object headers data:{}".format(dict(all_file_objects[one_file_object].headers)),1)    
    log_and_display("one file object content_type:{}".format(all_file_objects[one_file_object].content_type),1)    
    log_and_display("one file object content_length:{}".format(all_file_objects[one_file_object].content_length),1)    
    log_and_display("one file object space etc removed filename:{}".format(all_file_objects[one_file_object].filename) ,1)   
    
    #log_and_display("=====file data======",1)
    file_data_as_string=all_file_objects[one_file_object].file.read()
    #log_and_display("one file object file io object read() (like any other io handle):{}".format(file_data_as_string),1)
    local_collection=pdf2mysql_io(file_data_as_string,from_page,to_page)
    collection_string=collection_string+local_collection
  #return template("dummy.html",files=collection_string)
  return template("import_pdf.html",files=collection_string)


'''
class FileUpload[source]
    file        Open file(-like) object (BytesIO buffer or temporary file)
    name        Name of the upload form field
    raw_filename        Raw filename as sent by the client (may contain unsafe characters)
    headers        A HeaderDict with additional headers (e.g. content-type)
    content_type        Current value of the ‘Content-Type’ header.
    content_length        Current value of the ‘Content-Length’ header.
    get_header(name, default=None)[source]        Return the value of a header within the multipart part.
    filename()[source]        Name of the file on the client file system, but normalized to ensure file system compatibility. An empty filename is returned as ‘empty’.
    save(destination, overwrite=False, chunk_size=65536)    Save file to disk or copy its content to an open file(-like) object. If destination is a directory, filename is added to the path. Existing files are not overwritten by default (IOError).
        Parameters:                destination – File path, directory or file(-like) object.                overwrite – If True, replace existing files. (default: False)
                chunk_size – Bytes to read at a time. (default: 64kb)
'''
