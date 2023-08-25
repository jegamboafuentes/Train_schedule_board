#August 25 2023
#V2
#Jorge Enrique Gamboa Fuentes
#Subway schedule board - single direction
#Data from: Boston - MBTA
# .l. - .l. - .l. - .l. - .l. - .l. - .l. - .l. - .l. - .l. - .l. - .l. - .l. - .l. - .l. - .l. -

import time
import microcontroller
from board import NEOPIXEL
import displayio
import adafruit_display_text.label
from adafruit_datetime import datetime
from adafruit_bitmap_font import bitmap_font
from adafruit_matrixportal.matrix import Matrix
from adafruit_matrixportal.network import Network
import json

#CONFIGURABLE PARAMETERS
#-*-/-*-\-*--*-/-*-\-*--*-/-*-\-*--*-/-*-\-*--*-/-*-\-*--*-/-*-\-*--*-/-*-\-*--*-/-*-\-*-
BOARD_TITLE = 'Bowdoin'
STOP_ID = 'place-wondl'
DIRECTION_ID = '0'
ROUTE = 'Blue'
BACKGROUND_IMAGE = 'TBlue-dashboard.bmp'
PAGE_LIMIT = '3'
DATA_SOURCE = 'https://api-v3.mbta.com/predictions?filter%5Bstop%5D='+STOP_ID+'&filter%5Bdirection_id%5D='+DIRECTION_ID+'&page%5Blimit%5D='+PAGE_LIMIT+'&sort=departure_time'
DATA_SOURCE2 = 'https://www.mbta.com/schedules/finder_api/departures?id=Blue&stop=place-wondl&direction=0'
UPDATE_DELAY = 15
SYNC_TIME_DELAY = 30
MINIMUM_MINUTES_DISPLAY = 9
ERROR_RESET_THRESHOLD = 3
#-*-/-*-\-*--*-/-*-\-*--*-/-*-\-*--*-/-*-\-*--*-/-*-\-*--*-/-*-\-*--*-/-*-\-*--*-/-*-\-*-

def get_arrival_in_minutes_from_now(now, date_str):
    train_date = datetime.fromisoformat(date_str).replace(tzinfo=None) # Remove tzinfo to be able to diff dates
    return round((train_date-now).total_seconds()/60.0)

#New 8/25/23 - this function gets directly the time from the API
def get_arrival_times2():
    now = datetime.now()
    print(now)
    print("Data source: "+DATA_SOURCE2)
    stop_trains =  network.fetch_data(DATA_SOURCE2)
    res = json.loads(stop_trains)
    times = []
    for entry in res:
        try:
            time = entry['realtime']['prediction']['time']
            print(entry['realtime']['prediction']['time'])
            if time[0] == 'arriving':
                times.append('brding')
            else:
                times.append("{:02}".format(int(time[0])) + ' ' + time[2])
        except KeyError:
            continue
        if len(times) == 3:
            break
    return times 

#Old - this function retrives using the PREDICT API from MBTA
def get_arrival_times():
    now = datetime.now()
    print(now)
    print("Data source: "+DATA_SOURCE)
    stop_trains =  network.fetch_data(DATA_SOURCE)
    res = json.loads(stop_trains)
    try:
        train1 = res["data"][0]["attributes"]["departure_time"]
        train1_min = get_arrival_in_minutes_from_now(now, train1) - 1
    except:
        train1_min=-999
    try:
        train2 = res["data"][1]["attributes"]["departure_time"]
        train2_min = get_arrival_in_minutes_from_now(now, train2) - 1
    except:
        train2_min=-888
    try:
        train3 = res["data"][2]["attributes"]["departure_time"]
        train3_min = get_arrival_in_minutes_from_now(now, train3) - 1
    except:
        train3_min=-777

    return train1_min,train2_min,train3_min

def text_formating(trainMinutes):
    textFormated = ""
    if(trainMinutes<0&trainMinutes<-700):
        trainMinutes = 0
    if(trainMinutes<10):
        textFormated = "%s  min" % (trainMinutes)
    else:
        textFormated = "%s min" % (trainMinutes)
    if(trainMinutes<=0):
        textFormated = "brding"

    if(trainMinutes==-777):
        textFormated = "-----"
    elif(trainMinutes==-888):
        textFormated = "-----"
    elif(trainMinutes==-999):
        textFormated = "-----"

    return textFormated


def update_text(t1, t2, t3):
#def update_text(t1):
    print(t1)
    if(text_formating(t1)=="brding"):
        text_lines[2].color =  colors[2]
    else:
        text_lines[2].color =  colors[1]

    text_lines[2].text = text_formating(t1)
    text_lines[3].text = text_formating(t2)
    text_lines[4].text = text_formating(t3)

    display.show(group)
    
def update_text2(t1, t2, t3):
    #print("in update_text2")
    text_lines[2].text = t1#"hola"
    text_lines[3].text = t2
    text_lines[4].text = t3

    display.show(group)

# --- Display setup ---
matrix = Matrix()
display = matrix.display
network = Network(status_neopixel=NEOPIXEL, debug=False)

# --- Drawing setup ---
group = displayio.Group()
bitmap = displayio.OnDiskBitmap(open(BACKGROUND_IMAGE, 'rb'))
colors = [0x444444, 0xDD8000, 0x9966cc]  # [dim white, gold]

font = bitmap_font.load_font("fonts/6x10.bdf")
text_lines = [
    displayio.TileGrid(bitmap, pixel_shader=getattr(bitmap, 'pixel_shader', displayio.ColorConverter())),
    adafruit_display_text.label.Label(font, color=colors[0], x=20, y=3, text=BOARD_TITLE),
    adafruit_display_text.label.Label(font, color=colors[1], x=26, y=11, text="- min"),
    adafruit_display_text.label.Label(font, color=colors[1], x=26, y=20, text="- min"),
    adafruit_display_text.label.Label(font, color=colors[1], x=26, y=28, text="- min"),
]
for x in text_lines:
    group.append(x)
display.show(group)

error_counter = 0
last_time_sync = None
while True:
    try:
        if last_time_sync is None or time.monotonic() > last_time_sync + SYNC_TIME_DELAY:
            # Sync clock to minimize time drift
            network.get_local_time()
            last_time_sync = time.monotonic()
        #print("-*--> ENRIQUE HERE")
        #print(get_arrival_times())
        #arrivals = get_arrival_times()
        arrivals = get_arrival_times2()
        #update_text(*arrivals)
        update_text2(*arrivals)
    except (ValueError, RuntimeError) as e:
        print("Some error occured, retrying! -", e)
        error_counter = error_counter + 1
        if error_counter > ERROR_RESET_THRESHOLD:
            microcontroller.reset()

    time.sleep(UPDATE_DELAY)
