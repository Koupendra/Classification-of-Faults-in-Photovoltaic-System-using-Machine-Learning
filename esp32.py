
import network, time, urequests, ujson, dht
from machine import Pin

def setup(data):
  global ARD
  url = baseURL+"setup"
  data = ujson.dumps(data)
  r = urequests.post(url, data=data)
  print(r.text)
  ARD = int(r.text)
  return r.text


def classify(irr, temp, curr, volt):
  data = {'arduinoId': ARD, 'Irradiance': irr, 'Temperature': temp,
          'Current' : curr, 'Voltage': volt}
  url = baseURL+"classify"
  data = ujson.dumps(data)
  r = urequests.post(url, data=data)
  return r.text

#Buttons Setup
led = Pin(2, Pin.OUT)
rgb_r = Pin(12, Pin.OUT)
rgb_g = Pin(13, Pin.OUT)
rgb_b = Pin(14, Pin.OUT)
sensor = dht.DHT22(Pin(4))
reset_button = Pin(19, Pin.IN)

ARD = None                # No need to change this

'''
IMPORTANT! Edit the values
'''
nSer = None               # Number of PV modules in Series
nPar = None               # Number of PV modules in Parallel
email = None              # Email ID of the PV array owner
trainingData = None       # CSV training data URL
baseURL = None            # Server URL on which app is Running
wifiSSID = None           # SSID of the Wifi to connect the controller to
wifiPassword = None       # Password of the corresponding Wifi


data = {'nSer': nSer, 'nPar':nPar, 'email':email,
        'trainSetUrl': trainingData}

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(wifiSSID, wifiPassword)
while not sta_if.isconnected():
  time.sleep(0.1)
print("Connected")
time.sleep(3)
def set_rgb(r,g,b):
  global rgb_r, rgb_b, rgb_g
  rgb_r.value(r)
  rgb_g.value(g)
  rgb_b.value(b)

rgb_g.value(1)
fault = False
setup(data)

# Add/Edit Test data in format:
# (irradiation, current, voltage)
testData = [(1000, 19, 200), (750, 5, 100)]

    
i = 0
try:
  while sta_if.isconnected():
    led.value(1)
    sensor.measure()
    temp = sensor.temperature()
    print("TEMPERATURE",temp)
    if not fault:
      cond = classify(arr[i][0], temp, arr[i][1], arr[i][2])
      if cond=="Normal":
        set_rgb(0,1,0)
        fault = False
      elif cond=="Open Circuit Fault":
        set_rgb(1,0,0)
        fault = True
      elif cond=="Line-Line Fault":
        set_rgb(0,0,1)
        fault = True
      print(f"{arr[i][0]}, {temp}, {arr[i][1]}, {arr[i][2]} --> {cond}")
      i += 1
    else:
      fault = not reset_button.value()
      if not fault:
        set_rgb(0,1,0)
    led.value(0)
    if fault:
      time.sleep(0.5)
    else:
      time.sleep(10)
except Exception as e:
  print(e)
  print("Simulation completed!")
