# ----------------------------------------------------------------------------
# Display current power.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-ecu-display
# ----------------------------------------------------------------------------

import gc
import displayio
import time
import terminalio
import vectorio

from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

from settings import secrets, hw_config, app_config
from ui_settings import UI_SETTINGS, UI_PALETTE, COLOR

# --- main data-provider class   ---------------------------------------------

class UIProvider:

  def __init__(self):
    self._debug   = getattr(app_config, "debug", False)
    self._display = None
    self._view    = None

  # --- map value to color   -------------------------------------------------

  def _get_power_color(self, value):
    """ map value to color """

    ranges = app_config.power_ranges   # e.g. (0, 80, 130, 200)
    colors = app_config.power_colors   # e.g. (red, orange, yellow, green)
    for index, r in enumerate(ranges):
      if value < r:
        return colors[index-1]

  # --- print debug-message   ------------------------------------------------

  def msg(self,text):
    """ print (debug) message """
    if self._debug:
      print(text)

  # --- create complete content   --------------------------------------------

  def create_ui(self,display):
    """ create content """

    if self._view:
      return

    # save display
    self._display = display
    w2 = int(display.width/2)
    h2 = int(display.height/2)

    # text label for current power
    font_L = bitmap_font.load_font(UI_SETTINGS.FONT_L)
    self._power_txt = label.Label(font_L,
                                 text='0 W',
                                 color=UI_PALETTE[COLOR.RED],
                                 anchor_point=(0.5,0.5),
                                 anchored_position=(w2,h2))

    # text label for time
    font_S = bitmap_font.load_font(UI_SETTINGS.FONT_S)
    h_time_txt = h2 + self._power_txt.height/2 + UI_SETTINGS.PADDING
    self._time_txt = label.Label(font_S,
                                 text='00:00',
                                 color=UI_PALETTE[COLOR.RED],
                                 anchor_point=(0.5,0),
                                 anchored_position=(w2,h_time_txt))

    # colored arc as a sort of gauge
    # TODO: implement

    # add objects to group
    self._view = displayio.Group()
    self._view.append(self._power_txt)
    self._view.append(self._time_txt)

  # --- update ui   ----------------------------------------------------------

  def update_ui(self,data):
    """ update data: callback for Application """

    # map value of current_power to a color
    color = self._get_power_color(data['current_power'])

    # current power
    self._power_txt.text  = f"{data['current_power']}W"
    self._power_txt.color = color
    # pretty-print time of last update
    self._time_txt.text = data['timestamp'].split(' ')[1][:5]
    self._time_txt.color = color
    return self._view

  # --- clear UI and free memory   -------------------------------------------

  def clear_ui(self):
    """ clear UI """

    if self._view:
      for _ in range(len(self._view)):
        self._view.pop()
    self._view = None
    gc.collect()

  # --- handle exception   ---------------------------------------------------

  def handle_exception(self,ex):
    """ handle exception """

    import traceback
    try:
      # CircuitPython and CPython > 3.9
      ex_txt = ''.join(traceback.format_exception(ex))
    except:
      # CPython prior to 3.10
      ex_txt = ''.join(traceback.format_exception(None, ex, ex.__traceback__))

    # print to console
    print(60*'-')
    print(ex_txt)
    print(60*'-')

    # and update display
    if not self._display:
      return

    error_txt = label.Label(terminalio.FONT,
                            text=ex_txt,
                            color=UI_PALETTE[COLOR.RED],
                            line_spacing=1.2,
                            anchor_point=(0,0),
                            anchored_position=(0,0))

    g = displayio.Group()
    g.append(error_txt)
    return g
