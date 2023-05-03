# SPDX-FileCopyrightText: 2020 Brent Rubell for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import time
from random import randrange
import board
import terminalio
from adafruit_matrixportal.matrixportal import MatrixPortal

from adafruit_datetime import datetime, date


# --- Data Setup --- #
# Number of guides to fetch and display from the Adafruit Learning System
DISPLAY_NUM_GUIDES = 5
# Data source URL
#DATA_SOURCE = (
#    "https://learn.adafruit.com/api/guides/new.json?count=%d" % DISPLAY_NUM_GUIDES
#)
DATA_SOURCE = "https://api-v3.mbta.com/predictions?filter%5Bstop%5D=place-wondl&filter%5Bdirection_id%5D=0&filter%5Broute%5D=Blue&page%5Blimit%5D=6&sort=departure_time"
TITLE_DATA_LOCATION = ["jsonapi","version"]

matrixportal = MatrixPortal(
    url=DATA_SOURCE,
    json_path=TITLE_DATA_LOCATION,
    status_neopixel=board.NEOPIXEL,
)

# --- Display Setup --- #

# Colors for guide name
colors = [0xFFA500, 0xFFFF00, 0x008000, 0x0000FF, 0x4B0082, 0xEE82EE]

# Delay for scrolling the text
SCROLL_DELAY = 0.08

FONT = "/IBMPlexMono-Medium-24_jep.bdf"

# Learn guide count (ID = 0)
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(
        (matrixportal.graphics.display.width // 12) - 1,
        (matrixportal.graphics.display.height // 2) - 4,
    ),
    text_color=0x800000,
)
matrixportal.preload_font("0123456789")

# Learn guide title (ID = 1)
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(2, 25),
    text_color=0x000080,
    scrolling=True,
)




def get_guide_info(index):
    """Parses JSON data returned by the DATA_SOURCE
    to obtain the ALS guide title and number of guides an
    sets the text labels.
    :param int index: Guide index to display

    """
    if index > DISPLAY_NUM_GUIDES:
        raise RuntimeError("Provided index may not be larger than DISPLAY_NUM_GUIDES.")
    print("Obtaining guide info for guide %d..." % index)

    # Traverse JSON data for title
    #guide_count = matrixportal.network.json_traverse(als_data.json(), ["data","id"])
    #guide_count = matrixportal.network.json_traverse(als_data.json(), ["jsonapi","version"])
    guide_count = matrixportal.network.json_traverse(als_data.json(), ["data"])
    print("------> guide_count")
    print(guide_count)
    guide_count2 = guide_count[0]["attributes"]["departure_time"]

    isodate = datetime.fromisoformat(guide_count2)

    #delta = adafruit_datetime.timedelta(datetime.now(),isodate)
    #print(delta)

    print("Current time (GMT +1):", datetime.now())

    guide_count2=isodate.time()



  
    print("------> guide_count2")

    print(guide_count2)
    #guide_count2 = matrixportal.network.json_traverse(als_data.json(), ["id"])
    #guide_count2 = matrixportal.network.json_traverse(als_data.json(), ["id"])
    # Set guide count
    print(guide_count2)
    print(guide_count2)
    matrixportal.set_text(guide_count2, 0)

    guides = matrixportal.network.json_traverse(als_data.json(), TITLE_DATA_LOCATION)
    #guide_title = "JEGF test"#guides[index]["guide"]["title"]
    guide_title = "Next Bowdin train"#guides[index]["guide"]["title"]
    print("Guide Title", guide_title)

    # Select color for title text
    color_index = randrange(0, len(colors))

    # Set the title text color
    matrixportal.set_text_color(colors[color_index], 1)

    # Set the title text
    matrixportal.set_text(guide_title, 1)


refresh_time = None
guide_idx = 0
prv_hour = 0
while True:
    if (not refresh_time) or (time.monotonic() - refresh_time) > 900:
        try:
            print("obtaining time from adafruit.io server...")
            matrixportal.get_local_time()
            refresh_time = time.monotonic()
        except RuntimeError as e:
            print("Unable to obtain time from Adafruit IO, retrying - ", e)
            continue

    als_data = matrixportal.network.fetch(DATA_SOURCE)
    if time.localtime()[3] != prv_hour:
        print("New Hour, fetching new data...")
        # Fetch and store guide info response
        als_data = matrixportal.network.fetch(DATA_SOURCE)
        prv_hour = time.localtime()[3]

    # Cycle through guides retrieved
    if guide_idx < DISPLAY_NUM_GUIDES:
        get_guide_info(guide_idx)

        # Scroll the scrollable text block
        matrixportal.scroll_text(SCROLL_DELAY)
        guide_idx += 1
    else:
        guide_idx = 0
    time.sleep(0.05)

