#!/usr/bin/python3

import time
import json
import sys
import paho.mqtt.client as mqtt

# mqtt server and bulbs are defined in config.inc.py.
# there is a sample file, config.inc.py.sample that can be copied for 
# reference and modified to config.inc.py .

from config import *

global bulbmacs
global mqttroots

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

# for i in range(len(cmdtopics)):
  # print ( "cmdtopics[" + str(i) + "]: " + cmdtopics[i] )

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

#######################################
def enablebulb( idx ):

  global goodled
  global led
  global bulbmacs

  # print ( "enablebulb: idx = " + str(idx) )
  try:
    goodled[idx] = 1
    led[idx] = BluetoothLED( bulbmacs[idx] )
  except:
    # print ( "enablebulb: Cannot open led " + bulbmacs[idx] + ", is power on?" )
    # some how mark this as a 'bad' bulb, and move on, initializing
    # the other bulbs.  FOR NOW, just exit.
    # since the led has not been created, just make it is NOT good.
    goodled[idx] = 0
    led[idx] ="NOTHING HERE"

  if ( goodled[idx] == 1 ):
    # print ( "enablebulb: LED " + bulbmacs[idx] + " REconnected" )
    publishLWT(idx, goodled[idx] )

#######################################

def updgoodled(badidx):
  global led
  global goodled

  print ( "updgoodled: Cannot access led " + bulbmacs[badidx] + ", is power on?" )
  # print ( " updgoodled: led count before delete = " + str(len(led)) )
  # print ( " updgoodled: badidx = " + str(badidx ))

  goodled[badidx] = 0
  publishLWT(badidx, goodled[badidx])

  try:
    led[badidx].stopit()
    del led[badidx]

  except:   #already been deleted by bluetooth_led
    pass
    # print( "updgoodled: bulb " + bulbmacs[badidx] + " already deleted")
    # print ( " updgoodled: led count in except after delete = " + str(len(led)) )

  #fix up the array since the deleted led member changes the index for led
  #and breaks the logic for checking  existing bulbs

  max = len(bulbmacs)
  i = max-1

  # print ( " updgoodled: max = " + str(max ) )
  # print ( " updgoodled: i = " + str( i ) )
  # print ( " updgoodled: badidx = " + str(badidx ) )
  # print ( " updgoodled: led count JUST after delete = " + str(len(led)) )
  if (len(led) < len(bulbmacs)):
    if badidx < i:
      led.append(led[i-1])
    else:
      led.append("NOTHING HERE" )

    while ( i > badidx ):
      led[i] = led[i-1]
      i -= 1
  
  #finally fill the hole left by the delete above with something

  led[badidx] = "NOTHING HERE"
  # print ( " updgoodled: led count after fixup = " + str(len(led)) )
  # print ( " updgoodled: led count after nothing fix = " + str(len(led)) )

####################################
 
def publishLWT ( idx, state ):
  global mqttroots

  mqtttopic = mqttroots[idx] + "/" + "LWT"
  if state == 1 :
    client.publish( mqtttopic, "Online", true )
  else:
    client.publish( mqtttopic, "Offline", true )

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
  global mqttroots
  global statustopics

  mqtttopic = mqttroots[idx] + "/" + statustopics[0]
  if m_rgb_state :
    client.publish( mqtttopic, LIGHT_ON, true )
  else :
    client.publish( mqtttopic, LIGHT_OFF, true )

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
  global mqttroots
  global statustopics

  m_msg_buffer = ( "%d" %  m_color_temp )
  mqtttopic = mqttroots[idx] + '/' + statustopics[1]
  client.publish(mqtttopic, m_msg_buffer, true)

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
  global mqttroots
  global statustopics

  m_msg_buffer = ("%d" %  m_rgb_brightness)
  mqtttopic = mqttroots[idx] + '/' + statustopics[2]
  client.publish(mqtttopic, m_msg_buffer, true)

####################################
 
def publishRGBColor(idx):
  global m_rgb_state
  global m_rgb_brightness
  global m_rgb_red
  global m_rgb_green
  global m_rgb_blue

  global max_colortemp
  global min_colortemp
  global m_color_temp
  global mqttroots
  global statustopics

  m_msg_buffer = ( "%d,%d,%d" % (m_rgb_red, m_rgb_green, m_rgb_blue))
  mqtttopic = mqttroots[idx] + '/' + statustopics[3]
  client.publish(mqtttopic, m_msg_buffer, true)

####################################

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
  global goodled

  thisled = led[ledidx]
  try:
    thisled.set_state(True)
  except:
    print ( "setColor: Cannot setstate led " + bulbmacs[ledidx] + " , is power on?" )
    updgoodled(ledidx)

  # time.sleep(1)
  hexcolor = "#" + ("%0.2X" % red) +  ("%0.2X" % green) +  ("%0.2X" % blue)
  # print ( "hexcolor = " + hexcolor + "\n" )

  try:
    thisled.set_color( hexcolor )
  except:
    print ( "setColor2: Cannot setcolor led " + bulbmacs[ledidx] + " , is power on?" )
    updgoodled(ledidx)

  if (red + green + blue ) == 0:
    try:
      thisled.set_state(False)
    except:
      print ( "setColor3: Cannot setstate led, is power on?" )
      updgoodled(ledidx)

####################################
 
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
  global goodled

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
    updgoodled(ledidx)

  m_color_temp = int(ct)
  
####################################
 
####################################

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
  global goodled

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
    updgoodled(ledidx)

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
  global goodled

  print("on_connect: Connected to mqtt with result code "+str(rc))

  # Once connected publish an announcement and initial values

  for i in range(len(mqttroots)):

    publishRGBState(i)
    publishRGBBrightness(i)
    publishRGBColor(i)
    publishCTTemp(i)
    publishLWT(i,goodled[i])

  # client.subscribe("hello")
  # initialize these in batch for multiple bulbs as well as multiple topics
  # defined in arrays.

  for i in range(len(mqttroots)):
    if goodled[i] == 0:  # this is a bad led, so skip it.
      continue

    for j in range(len(cmdtopics)):
      client.subscribe( mqttroots[i] + '/' + cmdtopics[j] )

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
  global goodled

  payload = msg.payload.decode()
  topic = msg.topic

  print ( "on_message: topic: " + topic )
  print ( "on_message: payload: " + payload )
  
  match = 0
  for i in range(len(mqttroots)):
    if goodled[i] == 0:    # this bulb has been marked as bad
      print ( "on_message: bulb " + bulbmacs[i]) + " is disabled."
      continue

    for j in range(len(cmdtopics)):
      if (topic != ( mqttroots[i] + '/' + cmdtopics[j] )):
         continue
      else:
         match = 1
         break

    if match != 1:
       continue

    # change these states to be more generic since we have so many now.
    # these will need to be specific to individual bulbs.
    #  state
    if j == 0:
      if (payload == LIGHT_ON ):
        print ("on_message: turn it on")
        if (m_rgb_state != true):
          m_rgb_state = true
          setColor(i, m_rgb_red, m_rgb_green, m_rgb_blue)
          publishRGBState( i )
  
      elif (payload == LIGHT_OFF ):
        print ("on_message: turn it off")
        if (m_rgb_state != false):
          m_rgb_state = false
          setColor(i, 0, 0, 0)
          publishRGBState( i )
  
    elif j == 1:
      CT = payload
      setWhite (i,  CT )
      publishCTTemp( i )
  
    elif j == 2:
      brightness = int( payload )
      if (brightness < 0 or brightness > 100):
        return
      else:
        m_rgb_brightness = brightness
        # setColor(i, m_rgb_red, m_rgb_green, m_rgb_blue)
        setBrightness(i,  brightness )
        publishRGBBrightness( i )
  
    elif j == 3:
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

    # End of topic loop

    if match == 1:
      break

  # End of bulb loop
  # now see if any of the bulbs can be re-enabled.

##################################################
# The following section would attempt to re-enable the bulbs,
# howerver, if the bulbs are still out of service, the attempt
# takes a LONG time to timeout when waiting for the bulb to wake up.
# for the time being, I have commented this section.
##################################################

##########################################################
# This section attempts to wake up a bulb that has been previously disabled.
# as indicated above, there is a significant time delay when waiting for a
# connection when a bulb is still not available.
#
#  for i in range(len(mqttroots)):
#    if goodled[i] == 1:    # this bulb is good, continue
#      continue
#
#    print ( "on_message: trying to re-enable bulb " + bulbmacs[i])
#    enablebulb( i )
#    if goodled[i] == 0:    # this bulb is still disabled
#      continue

# this is the end of the different topics

##########################################

# initialize bluetooth connections for the bulbs defined in config

goodled = []
led = []

goodsum = 0
print ( "MAIN: starting initialize" )
for i in range(len(bulbmacs)):
  goodled.append( 1 )
  for j in range(3):
    print ( "MAIN: --------------------------------------------------" )
    print ( "MAIN: attempting connect to " + bulbmacs[i] )
    try:
      goodled[i] = 1
      led.append ( BluetoothLED( bulbmacs[i] ))
      goodsum = goodsum + 1
    except:
      print ( "MAIN: Cannot open led " + bulbmacs[i] + ", is power on?" )
      # some how mark this as a 'bad' bulb, and move on, initializing
      # the other bulbs.  FOR NOW, just exit.
      # since the led has not been created, just make it is NOT good.
      goodled[i] = 0

    if ( goodled[i] == 1 ):
      print ( "MAIN: LED " + bulbmacs[i] + " connected" )
      break
    time.sleep (2)

  if ( goodled[i] == 0 ):
    led.append( "NOTHING HERE" )

if goodsum == 0:   #NO bulbs available , exiting.
  print( "NO bulbs are available, exiting.")
  exit()
 
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqttBroker,mqttBrokerPort,60)

client.loop_forever()

