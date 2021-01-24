#!/usr/bin/python3

import time
import json
import sys
import paho.mqtt.client as mqtt

# mqtt server and bulbs are defined in config.inc.py.
# there is a sample file, config.inc.py.sample that can be copied for 
# reference and modified to config.inc.py .

import config.inc.py

from govee_btled import BluetoothLED

# define initial values for on, off , brightness, color
# define mqtt topics


#  MQTT: topics
#  state

topicids = ['light','color temperature','brightness','rgbcolor']

#these get published
statustopics = ["light/status","ct/status","brightness/status","rgb/status"]
#these get subscribed
cmdtopics = ["light/switch","ct/set","brightness/set","rgb/set"]

LIGHT_ON = "ON"
LIGHT_OFF = "OFF"
true = 1
false = 0

m_rgb_state = 1
m_rgb_brightness = 100
m_rgb_red = 255
m_rgb_green = 255
m_rgb_blue = 255

max_colortemp = 500
min_colortemp = 153
m_color_temp = 500



#   mqtt client id 

# 
####################################
 
def publishRGBState( idx ):
  global m_rgb_state
  global m_rgb_brightness
  global m_rgb_red
  global m_rgb_green
  global m_rgb_blue

  global max_colortemp
  global min_colortemp
  global m_color_temp
  global mqttroot
  global statustopics

  mqtttopic = mqttroot[idx] . '/' . statustopics[1]
  if m_rgb_state :
    client.publish( mqtttopic, LIGHT_ON, true )
  else :
    client.publish( mqtttopic, LIGHT_OFF, true )

####################################
 
def publishRGBBrightness(idx):
  global m_rgb_state
  global m_rgb_brightness
  global m_rgb_red
  global m_rgb_green
  global m_rgb_blue

  global max_colortemp
  global min_colortemp
  global m_color_temp
  global mqttroot
  global statustopics

  m_msg_buffer = ("%d" %  m_rgb_brightness)
  mqtttopic = mqttroot[idx] . '/' . statustopics[3]
  client.publish(mqtttopic, m_msg_buffer, true)

####################################
 
def publishCTTemp(idx):
  global m_rgb_state
  global m_rgb_brightness
  global m_rgb_red
  global m_rgb_green
  global m_rgb_blue

  global max_colortemp
  global min_colortemp
  global m_color_temp
  global mqttroot
  global statustopics

  m_msg_buffer = ( "%d" %  m_color_temp )
  mqtttopic = mqttroot[idx] . '/' . statustopics[2]
  client.publish(mqttttopic, m_msg_buffer, true)

####################################
 
def publishRGBColor():
  global m_rgb_state
  global m_rgb_brightness
  global m_rgb_red
  global m_rgb_green
  global m_rgb_blue

  global max_colortemp
  global min_colortemp
  global m_color_temp
  global mqttroot
  global statustopics

  m_msg_buffer = ( "%d,%d,%d" % (m_rgb_red, m_rgb_green, m_rgb_blue))
  mqtttopic = mqttroot[idx] . '/' . statustopics[4]
  client.publish(mqttttopic, m_msg_buffer, true)

####################################
## this needs to be modified for using different bulbs and defineable 
#  topics.
###################################

def setColor(ledidx, red, green, blue ):
  global m_rgb_state
  global m_rgb_brightness
  global m_rgb_red
  global m_rgb_green
  global m_rgb_blue

  global max_colortemp
  global min_colortemp
  global m_color_temp

  global led

  try:
    led[ledidx].set_state(True)
  except:
    print ( "Cannot setstate led, is power on?" )
    sys.exit()

  # time.sleep(1)
  hexcolor = "#" + ("%0.2X" % red) +  ("%0.2X" % green) +  ("%0.2X" % blue)
  print ( "hexcolor = " + hexcolor + "\n" )

  try:
    led[ledidx].set_color( hexcolor )
  except:
    print ( "Cannot setcolor led, is power on?" )
    sys.exit()

  if (red + green + blue ) == 0:
    try:
      led[ledidx].set_state(False)
    except:
      print ( "Cannot setstate led, is power on?" )
      sys.exit()

####################################
 
####################################
## this needs to be modified for using different bulbs and defineable 
#  topics.
###################################

def setWhite( ledidx, ct ):
  global m_rgb_state
  global m_rgb_brightness
  global m_rgb_red
  global m_rgb_green
  global m_rgb_blue

  global max_colortemp
  global min_colortemp
  global m_color_temp

  global led

  # The bulb seems to have a white-mode which uses cold/warm white
  #  LEDs instead of the RGB LEDs.
  # ct is a value between 153 and 500 and must be scaled to -1 to 1
  # Supply a value between -1 (warm) and 1 (cold)
  # led[ledidx].set_color_white(-0.4) # range is -1 to 1

  halfrange = ( max_colortemp - min_colortemp +1 )/ 2
  tempct = ( int(ct) - (min_colortemp + halfrange)) / halfrange
  try:
    led[ledidx].set_color_white( -tempct )
  except:
    print ( "Cannot setstate led, is power on?" )
    sys.exit()

  m_color_temp = int(ct)
  
####################################
 
####################################
## this needs to be modified for using different bulbs and defineable 
#  topics.
###################################

def setBrightness( ledidx, bright ):
  global m_rgb_state
  global m_rgb_brightness
  global m_rgb_red
  global m_rgb_green
  global m_rgb_blue

  global max_colortemp
  global min_colortemp
  global m_color_temp

  global led

  # The bulb seems to have a white-mode which uses cold/warm white
  #  LEDs instead of the RGB LEDs.
  # bright is a value between 0 and 100
  # set_brightness incoming must be a value between 0 and 1,
  # so incoming must be divided by 100

  tempbright = bright / 100
  try:
    led[ledidx].set_brightness( tempbright )
  except:
    print ( "Cannot setbrightness led, is power on?" )
    sys.exit()

  m_brightness = bright
  
####################################
 
def on_connect(client, userdata, flags, rc):
  global m_rgb_state
  global m_rgb_brightness
  global m_rgb_red
  global m_rgb_green
  global m_rgb_blue

  global max_colortemp
  global min_colortemp
  global m_color_temp

  print("Connected with result code "+str(rc))

  # Once connected publish an announcement and initial values

  publishRGBState()
  publishRGBBrightness()
  publishRGBColor()
  publishCTTemp()

  # client.subscribe("hello")
  # initialize these in batch for multiple bulbs as well as multiple topics
  # defined in arrays.

  for i in range(len(mqttroot))
    for j in range(len(cmdtopics))
      client.subscribe( mqttroot[i] . '/' . cmdtopics[j] )

####################################
 
def on_message(client, userdata, msg):
  global m_rgb_state
  global m_rgb_brightness
  global m_rgb_red
  global m_rgb_green
  global m_rgb_blue

  global max_colortemp
  global min_colortemp
  global m_color_temp

  print("Transmission received")
  payload = msg.payload.decode()
  topic = msg.topic

  print ( payload )
  print ( topic )
  
  for i in range(len(mqttroot))
    for j in range(len(cmdtopics))
      if topic == ( mqttroot[i] . '/' . cmdtopics[j] )
      break

    # change these states to be more generic since we have so many now.
    # these will need to be specific to individual bulbs.
    #  state
    if j ==  1:
      # print ("in the mqtt light command topic")
      # print ( "light_on = " + LIGHT_ON + ":EOF" )
      # print ( "light_off = " + LIGHT_OFF + ":EOF" )
      # print ( "payload = " + payload + ":EOF" )
      if (payload == LIGHT_ON ):
        # print ("Time to turn it on!")
        if (m_rgb_state != true):
          m_rgb_state = true
          setColor(i, m_rgb_red, m_rgb_green, m_rgb_blue)
          publishRGBState( i )
  
      elif (payload == LIGHT_OFF ):
        print ("Time to turn it off!")
        if (m_rgb_state != false):
          m_rgb_state = false
          setColor(i, 0, 0, 0)
          publishRGBState( i )
  
    elif j == 3:
      #do something
      brightness = int( payload )
      if (brightness < 0 or brightness > 100):
        # do nothing...
        return
      else:
        m_rgb_brightness = brightness
        # setColor(i, m_rgb_red, m_rgb_green, m_rgb_blue)
        setBrightness(i,  brightness )
        publishRGBBrightness( i )
  
    elif j == 2:
      CT = payload
      setWhite (i,  CT )
      publishCTTemp( i )
  
    elif j == 4:
      #  colors (rgb)
      # The line below needs fixing, not sure how yet..
      # rgb_red = payload.substring(0, firstIndex).toInt()
  
      (pred, pgreen, pblue) = payload.split(",")
      rgb_red = int(pred)
      rgb_green = int(pgreen)
      rgb_blue = int(pblue)
  
      if (rgb_red < 0 or rgb_red > 255):
        return
      else:
        m_rgb_red = rgb_red
      
      # The line below needs fixing, not sure how yet..
      # rgb_green = payload.substring(firstIndex + 1, lastIndex).toInt()
  
      if (rgb_green < 0 or rgb_green > 255):
        return
      else:
        m_rgb_green = rgb_green
      
      # The line below needs fixing, not sure how yet..
      # rgb_blue = payload.substring(lastIndex + 1).toInt()
      if (rgb_blue < 0 or rgb_blue > 255):
        return
      else:
        m_rgb_blue = rgb_blue
      
      setColor(i, m_rgb_red, m_rgb_green, m_rgb_blue)
      publishRGBColor( i )

# this is the end of the different topics

##########################################

# initialize bluetooth connections for the bulbs defined in config

for i in range(len(bulbmacs))
  try:
    led[i] = BluetoothLED( bulbmacs[i] )
  except:
    print ( "Cannot open led " . bulbmacs[i] . ", is power on?" )
    # some how mark this as a 'bad' bulb, and move on, initializing
    # the other bulbs.  FOR NOW, just exit.
    sys.exit()
  
prevtime=time.time()
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqttBroker,mqttBrokerPort,60)

client.loop_forever()

