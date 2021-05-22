#!/usr/bin/env python
# coding: utf-8


import requests
import pandas as pd
import http.client
import json
from glom import glom
from discord import Webhook, RequestsWebhookAdapter
import paho.mqtt.client as mqtt
import datetime
import time
import os
datecount=0
dateincreament = 7

mqttaddress = os.getenv('mqttaddress', '192.168.1.11')
print("mqttaddress env value",mqttaddress)
mqttport = os.getenv('mqttport', '1883')
print("mqttport env value",mqttport)
discord = os.getenv('discord', 'aaa')
print("discord env value", discord)

client = mqtt.Client()
client.connect(mqttaddress,int(mqttport))
client.publish("topic/vaccine_status", "no",retain=True)
webhook = Webhook.from_url(discord, adapter=RequestsWebhookAdapter())


while True: 
    if datecount==0:
        x = datetime.datetime.now()
        date1=x.strftime("%d-%m-%Y")
        datecount= datecount + 1
    elif datecount==3:
        dateincreament = 7
        datecount = 0
        print("\n sleeping for 5min \n")
        time.sleep(300)
        client.disconnect()
        client.connect(mqttaddress,int(mqttport))
        continue
    else:
        date_1 = datetime.datetime.strptime(date1, "%d-%m-%Y")
        end_date = date_1 + datetime.timedelta(days=dateincreament)
        print("date1:", date1 , "end date:" , end_date)
        date1=end_date.strftime("%d-%m-%Y")
        dateincreament = dateincreament + dateincreament
        datecount= datecount+1

    print("\n ********date ************** ", date1 , "\n\n")
    

    conn = http.client.HTTPSConnection("cdn-api.co-vin.in")
    payload = ''
    headers = {}

    conn.request("GET", "/api/v2/appointment/sessions/public/calendarByDistrict?district_id=266&date="+date1, payload, headers)
    res = conn.getresponse()
    data = res.read()

    # print(data.decode())
    df = pd.read_json(data.decode())
    level1=df['centers'].apply(lambda row: glom(row, 'sessions'))
    dump = pd.DataFrame()
    for i in level1:
        for j in i:
            content = json.dumps(j)
            df1=pd.read_json(content)
            dump=dump.append(df1)
    try:
            dffiler=dump.loc[(dump['min_age_limit'] == 18) & (dump['available_capacity'] >0 )]
            print("hit 1")
    except:
            print("hit 2 , no data")
            continue
    dump = pd.DataFrame()
    for i in level1:
        for j in i:
            content = json.dumps(j)
            df1=pd.read_json(content)
            dump=dump.append(df1)
    
    # print(dffiler)
    
    # webhook.send("vaccination found for date:"+date1)
    if dffiler.empty:
        print("empty")
    #     webhook.send("")
    else:
        sendString = ""
        client.publish("topic/vaccine_status", "yes",retain=True)
        client.publish("topic/vaccine_daterange",date1,retain=True)
        webhook.send("vaccination found for date:"+date1)
        for index, row in dffiler.iterrows():
            sendString = sendString+ "\n" + row.date.strftime("%d %b, %Y")+";"+str(row.available_capacity)+";"+str(row.min_age_limit)+";"+str(row.vaccine)+";"+str(row.slots)
        print(sendString)
        # client.publish("topic/vaccine_details",sendString)
        webhook.send(sendString)
    # client.disconnect()
# time.sleep()