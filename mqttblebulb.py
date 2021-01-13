#!/usr/bin/python3

import time
import json
import sys
import paho.mqtt.client as mqtt

from govee_btled import BluetoothLED

# The only values that need to be defined

bulbmac = 'XX:XX:XX:XX:XX:XX'
mqttBroker = "mqttserver ip or address"
mqttBrokerPort = 1883

# define initial values for on, off , brightness, color
# define mqtt topics


#  MQTT: topics
#  state

MQTT_LIGHT_STATE_TOPIC = "office/rgb1/light/status"
MQTT_LIGHT_COMMAND_TOPIC = "office/rgb1/light/switch"

#  color temperature
MQTT_COLOR_TEMP_STATE_TOPIC = "office/rgb1/ct/status"
MQTT_COLOR_TEMP_COMMAND_TOPIC = "office/rgb1/ct/set"

#  brightness
MQTT_LIGHT_BRIGHTNESS_STATE_TOPIC = "office/rgb1/brightness/status"
MQTT_LIGHT_BRIGHTNESS_COMMAND_TOPIC = "office/rgb1/brightness/set"

#  colors (rgb)
MQTT_LIGHT_RGB_STATE_TOPIC = "office/rgb1/rgb/status"
MQTT_LIGHT_RGB_COMMAND_TOPIC = "office/rgb1/rgb/set"

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
 
def publishRGBState():
  global m_rgb_state
  global m_rgb_brightness
  global m_rgb_red
  global m_rgb_green
  global m_rgb_blue

  global max_colortemp
  global min_colortemp
  global m_color_temp

  if m_rgb_state :
    client.publish( MQTT_LIGHT_STATE_TOPIC, LIGHT_ON, true )
  else :
    client.publish( MQTT_LIGHT_STATE_TOPIC, LIGHT_OFF, true )

####################################
 
def publishRGBBrightness():
  global m_rgb_state
  global m_rgb_brightness
  global m_rgb_red
  global m_rgb_green
  global m_rgb_blue

  global max_colortemp
  global min_colortemp
  global m_color_temp

  m_msg_buffer = ("%d" %  m_rgb_brightness)
  client.publish(MQTT_LIGHT_BRIGHTNESS_STATE_TOPIC, m_msg_buffer, true)

####################################
 
def publishCTTemp():
  global m_rgb_state
  global m_rgb_brightness
  global m_rgb_red
  global m_rgb_green
  global m_rgb_blue

  global max_colortemp
  global min_colortemp
  global m_color_temp

  m_msg_buffer = ( "%d" %  m_color_temp )
  client.publish(MQTT_COLOR_TEMP_STATE_TOPIC, m_msg_buffer, true)

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

  m_msg_buffer = ( "%d,%d,%d" % (m_rgb_red, m_rgb_green, m_rgb_blue))
  client.publish(MQTT_LIGHT_RGB_STATE_TOPIC, m_msg_buffer, true)

####################################
 
def setColor(red, green, blue ):
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
    led.set_state(True)
  except:
    print ( "Cannot setstate led, is power on?" )
    sys.exit()

  # time.sleep(1)
  hexcolor = "#" + ("%0.2X" % red) +  ("%0.2X" % green) +  ("%0.2X" % blue)
  print ( "hexcolor = " + hexcolor + "\n" )

  try:
    led.set_color( hexcolor )
  except:
    print ( "Cannot setcolor led, is power on?" )
    sys.exit()

  if (red + green + blue ) == 0:
    try:
      led.set_state(False)
    except:
      print ( "Cannot setstate led, is power on?" )
      sys.exit()

####################################
 
def setWhite( ct ):
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
  # led.set_color_white(-0.4) # range is -1 to 1

  halfrange = ( max_colortemp - min_colortemp +1 )/ 2
  tempct = ( int(ct) - (min_colortemp + halfrange)) / halfrange
  try:
    led.set_color_white( -tempct )
  except:
    print ( "Cannot setstate led, is power on?" )
    sys.exit()

  m_color_temp = int(ct)
  
####################################
 
def setBrightness( bright ):
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
    led.set_brightness( tempbright )
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
  client.subscribe(MQTT_LIGHT_COMMAND_TOPIC)
  client.subscribe(MQTT_LIGHT_BRIGHTNESS_COMMAND_TOPIC)
  client.subscribe(MQTT_LIGHT_RGB_COMMAND_TOPIC)
  client.subscribe(MQTT_COLOR_TEMP_COMMAND_TOPIC)

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
  
  #  state
  if topic ==  MQTT_LIGHT_COMMAND_TOPIC:
    # print ("in the mqtt light command topic")
    # print ( "light_on = " + LIGHT_ON + ":EOF" )
    # print ( "light_off = " + LIGHT_OFF + ":EOF" )
    # print ( "payload = " + payload + ":EOF" )
    if (payload == LIGHT_ON ):
      # print ("Time to turn it on!")
      if (m_rgb_state != true):
        m_rgb_state = true
        setColor(m_rgb_red, m_rgb_green, m_rgb_blue)
        publishRGBState()

    elif (payload == LIGHT_OFF ):
      print ("Time to turn it off!")
      if (m_rgb_state != false):
        m_rgb_state = false
        setColor(0, 0, 0)
        publishRGBState()

  elif topic == MQTT_LIGHT_BRIGHTNESS_COMMAND_TOPIC:
    #do something
    brightness = int( payload )
    if (brightness < 0 or brightness > 100):
      # do nothing...
      return
    else:
      m_rgb_brightness = brightness
      # setColor(m_rgb_red, m_rgb_green, m_rgb_blue)
      setBrightness( brightness )
      publishRGBBrightness()

  elif topic == MQTT_COLOR_TEMP_COMMAND_TOPIC:
    CT = payload
    setWhite ( CT )
    publishCTTemp()

  elif topic == MQTT_LIGHT_RGB_COMMAND_TOPIC:
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
    
    setColor(m_rgb_red, m_rgb_green, m_rgb_blue)
    publishRGBColor()

# this is the end of the different topics

##########################################

try:
  led = BluetoothLED( bulbmac )
except:
  print ( "Cannot open led, is power on?" )
  sys.exit()


try:
  led.ping()
except:
  print ( "Cannot first ping led, is power on?" )
  sys.exit()

prevtime=time.time()
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqttBroker,mqttBrokerPort,60)

client.loop_start()

while True:
  currtime = time.time()
  if ( currtime > (prevtime + 1.5 )):
    print ( "ping led bulb: " + str (currtime) )
    try:
      led.ping()
    except:
      print ( "Cannot ping led, is power on?" )
      sys.exit()

    prevtime = currtime

#### Should never get here
client.loop_stop()

##########################################
