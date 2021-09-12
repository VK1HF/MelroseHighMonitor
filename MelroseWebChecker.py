#!/usr/bin/python
# - Web page update checker for Melrose High
# - Written and tested using Python 2.7.16, running from a cron job - twice a day, on a RaspBerry Pi
# - Author : Ian Gilchist - ian@gilian.net
# - Composed at the behest of Stuart McKeller - aka McSkellaMcFella - aka 'Kushinforthepushin
# - Run it cron cron.d - 12 noon at 6pm each day : * 12,18 * * * ~/MelroseHigh/MelroseWebChecker.py >~/MelroseHigh/log.txt
# - Licence : None, feel free to use/modify as you like, be nice if you drop me a line. 
# - Version 1.0 (Initial Release)
# - Date : 12 Sep 2021 - 4 Weeks into Covid Lockdown in the National Capital 

import urllib2
import os
import re
import time
import datetime
import hashlib

url = "https://www.melrosehs.act.edu.au/"
filename = "MelroseHigh_Data"
month_day = datetime.datetime.now()
actual_time = int(time.time())
month_day = datetime.datetime.now()
unix_time_now = int(time.time())
case_count_difference = 0

os.system('clear')
print (str(month_day.strftime("\nBEGIN >> @ %a %d-%b-%y %H:%M:%S\n")))
#print "Unix Time Now : " + str(actual_time)

# Load Previous Data from date file
try:
    data_file = open(filename, "r")
    lines = data_file.readlines()
    last_lines = str(lines[-1:])
    data_file.close()
    file_data = re.search('(\d+),(.{32})', last_lines, re.IGNORECASE)
    Last_Update = int(file_data.group(1))
    Last_Update_Hash = str(file_data.group(2))
except:
    print("** file load failed - must not exist, all good\n")
    Last_Update= 0
    Last_Update_Hash = "xx-no_saved_hash_xx"

from datetime import datetime
print "  Saved << Unix Time : " + (datetime.fromtimestamp(Last_Update).strftime('%Y-%m-%d %H:%M:%S')) + " << Load Web Page MD5 Digest : " + str(Last_Update_Hash)

#Lets grab the main Web Page - strip of a few bits and hash is to MD5
try:
  response = urllib2.urlopen(url)
  webpage_raw = response.read()
  Web_Page_Cleaned = re.sub('Page\sgenerated:\s\d+\s\w+\s\d+\s\d+:\d+:\d+', '', webpage_raw)
  #print(Web_Page_Cleaned)
  Web_Page_hash = hashlib.md5(Web_Page_Cleaned).hexdigest()
  from datetime import datetime
  print "Current >> Unix Time : " + (datetime.fromtimestamp(unix_time_now).strftime('%Y-%m-%d %H:%M:%S')) + " >> Load Web Page MD5 Digest : " + str(Web_Page_hash)

except :
  print("something went wrong with the Web call.. bugging out")
  exit()

# Let's compare the loaded Data (last Saved) and what we are seeing now - if Diff then Save 
if Last_Update_Hash != Web_Page_hash:
  print ("\nDifference noted - >>\n  ..Writing File...\n")
  case_count_difference = 1         # We'll use this to trigger actions based upon there being a noted page update.
  file_data = str(unix_time_now) + "," + Web_Page_hash + "\n"
  text_file = open(filename, "a")
  text_file.write(file_data)
  text_file.close()

  #Prune the file to stay at 100 lines long max
  command = "cat " + filename + " | tail -100 > " + filename + ".new ; mv -f " + filename + ".new " + filename
  os.system(command)

if case_count_difference == 1:
  print "  ..sending SMS notifications"
  import clicksend_client
  import clicksend_client
  from clicksend_client import SmsMessage
  from clicksend_client.rest import ApiException
  
  message_body = "Yo, your fav web page seems to have changed - check it out! \nhttps://www.melrosehs.act.edu.au/\nLast Update was at : " + (datetime.fromtimestamp(Last_Update).strftime('%Y-%m-%d %H:%M:%S'))
  
  # Configure HTTP basic authorization: BasicAuth
  configuration = clicksend_client.Configuration()
  configuration.username = 'your_clicksend_username'
  configuration.password = 'your_clicksend_api_key'
  api_instance = clicksend_client.SMSApi(clicksend_client.ApiClient(configuration))
  
  recipients = ["+61408334455","+61408112233"]
  for recpient_number in recipients:
      sms_message = SmsMessage(source="php",
                          body=(message_body),
                          _from="+61408555555",
                          to=(recpient_number))
      sms_messages = clicksend_client.SmsMessageCollection(messages=[sms_message])
  
      try:
          # Send sms message(s)
          api_response = api_instance.sms_send_post(sms_messages)
          print(api_response)
      except ApiException as e:
          print("Exception when calling SMSApi->sms_send_post: %s\n" % e)

import datetime
month_day = datetime.datetime.now()
print (str(month_day.strftime("\nEND << @ %a %d-%b-%y %H:%M:%S\n")))
