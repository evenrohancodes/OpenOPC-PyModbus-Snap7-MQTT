import network
import time
from math import sin
from umqtt.simple import MQTTClient
from machine import Pin

# Setup the onboard LED so we can turn it on/off
led = Pin("LED", Pin.OUT)

# Fill in your WiFi network name (ssid) and password here:
wifi_ssid = "Fusion Automate"
wifi_password = "Fusion_Automate"

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifi_ssid, wifi_password)
while wlan.isconnected() == False:
    print('Waiting for connection...')
    time.sleep(1)
print("Connected to WiFi")

# Fill in your Adafruit IO Authentication and Feed MQTT Topic details
mqtt_host = "io.adafruit.com"
mqtt_username = "PyLin"  # Your Adafruit IO username
mqtt_password = "aio_bDkZ61W9t0PVqkZ8L8ZhP1xKaSbv"  # Adafruit IO Key
mqtt_publish_topic = "PyLin/feeds/feed-fusion"  # The MQTT topic for your Adafruit IO Feed
mqtt_receive_topic = "PyLin/feeds/pi-pico-w-led"  # The MQTT topic for your Adafruit IO Feed

# Enter a random ID for this MQTT Client
# It needs to be globally unique across all of Adafruit IO.
mqtt_client_id = "Fusion_Automate_PI_PICO_W_PUB_SUB"

# Initialize our MQTTClient and connect to the MQTT server
mqtt_client = MQTTClient(
        client_id=mqtt_client_id,
        server=mqtt_host,
        user=mqtt_username,
        password=mqtt_password)

# So that we can respond to messages on an MQTT topic, we need a callback
# function that will handle the messages.
def mqtt_subscription_callback(topic, message):
    print (f'Topic {topic} received message {message}')  # Debug print out of what was received over MQTT
    if message == b'on':
        print("LED ON")
        led.value(1)
    elif message == b'off':
        print("LED OFF")
        led.value(0)
        

# Before connecting, tell the MQTT client to use the callback
mqtt_client.set_callback(mqtt_subscription_callback)
mqtt_client.connect()

# Set the initial state of the LED to off, and let the MQTT topic know about it
led.value(0)
mqtt_client.publish(mqtt_receive_topic, "off")

# Once connected, subscribe to the MQTT topic
mqtt_client.subscribe(mqtt_receive_topic)
print("Connected and subscribed")

# Publish a data point to the Adafruit IO MQTT server every 3 seconds
# Note: Adafruit IO has rate limits in place, every 3 seconds is frequent
#  enough to see data in realtime without exceeding the rate limit.
counter = 0
try:
    while True:
        # Generate some dummy data that changes every loop
        sine = sin(counter)
        counter += .8
        
        # Publish the data to the topic!
        print(f'Publish {sine:.2f}')
        mqtt_client.publish(mqtt_publish_topic, str(sine))
        # Infinitely wait for messages on the topic.
        # Note wait_msg() is a blocking call, if you're doing multiple things
        # on the Pico you may want to look at putting this on another thread.
        print(f'Waiting for messages on {mqtt_receive_topic}')
        mqtt_client.wait_msg()
        
        # Delay a bit to avoid hitting the rate limit
        #time.sleep(3)
except Exception as e:
    print(f'Failed to publish message: {e}')
finally:
    mqtt_client.disconnect()