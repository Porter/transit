import RPi.GPIO as GPIO
import requests
from datetime import datetime, timedelta
import json
import time

time.sleep(30)

SDI   = 17
RCLK  = 18
SRCLK = 27

topLeft = 1 << 0
bottomLeft = 1 << 1
bottom = 1 << 2
bottomRight = 1 << 3
middle = 1 << 4
top = 1 << 5
topRight = 1 << 6
dot = 1 << 7
all = 0xff ^ dot

right = bottomRight | topRight
left = bottomLeft | topLeft

zero = left | right | top | bottom
one = right
two = top | middle | bottom | topRight | bottomLeft
three = right | top | middle | bottom
four = topLeft | middle | right
five = top | middle | bottom | topLeft | bottomRight
six = all ^ topRight
seven = top | right
eight = all
nine = all ^ bottomLeft

m = {
	0: zero,
	1: one,
	2: two,
	3: three,
	4: four,
	5: five,
	6: six,
	7: seven,
	8: eight,
	9: nine,
}


def get_times():
	r = requests.get('http://api.511.org/transit/StopMonitoring?api_key=TODO_POPULATE&agency=SF&stopCode=14943')
	j = r.content
	start = j.find(b"{")
	content = j[start:]

	content = content.decode('utf-8')
	stuff = json.loads(content)

	visits = stuff['ServiceDelivery']['StopMonitoringDelivery']['MonitoredStopVisit']

	now = datetime.now()
	times = []
	for visit in visits:
		eta = visit['MonitoredVehicleJourney']['MonitoredCall']['ExpectedArrivalTime']
		parsed = datetime.strptime(eta, '%Y-%m-%dT%H:%M:%SZ')
		delta = parsed - now
		times.append(int(delta / timedelta(minutes=1)))

	times = sorted(times)
	print(times)
	return times

def setup():
	GPIO.setmode(GPIO.BCM)    #Number GPIOs by BCM
	GPIO.setup(SDI, GPIO.OUT)
	GPIO.setup(RCLK, GPIO.OUT)
	GPIO.setup(SRCLK, GPIO.OUT)
	GPIO.output(SDI, GPIO.LOW)
	GPIO.output(RCLK, GPIO.LOW)
	GPIO.output(SRCLK, GPIO.LOW)

def hc595_shift(dat):
	for bit in range(0, 16):	
		val = 0x8000 & (dat << bit)
		GPIO.output(SDI, val)
		GPIO.output(SRCLK, GPIO.HIGH)
		time.sleep(0.001)
		GPIO.output(SRCLK, GPIO.LOW)
	GPIO.output(RCLK, GPIO.HIGH)
	time.sleep(0.001)
	GPIO.output(RCLK, GPIO.LOW)

def destroy():   #When program ending, the function is executed. 
	hc595_shift(0)
	GPIO.cleanup()

def loop(val):
	for i in range(65):
		tens = val % 10
		ones = int(val / 10)
		code = (m[tens] << 8) | m[ones]
		hc595_shift(code)
		time.sleep(1)

if __name__ == '__main__': #Program starting from here 
	with open('/home/pi/out.txt', 'w') as f:
		f.write('Running')
	setup() 
	try:
		while True:
			times = get_times()
			loop(times[0])
	except KeyboardInterrupt:  
		destroy()  
