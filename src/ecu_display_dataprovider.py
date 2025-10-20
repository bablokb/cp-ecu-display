# ----------------------------------------------------------------------------
# Read current power from an APSystems ECU-x.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-ecu-display
# ----------------------------------------------------------------------------

import gc
import time
from settings import app_config

# --- main data-provider class   ---------------------------------------------

class DataProvider:

  def __init__(self):
    self._debug = getattr(app_config, "debug", False)
    self._wifi  = None
    self._inverter = None
    self._mock_index = 0

  # --- print debug-message   ------------------------------------------------

  def msg(self,text):
    """ print (debug) message """
    if self._debug:
      print(text)

  # --- set wifi-object   ----------------------------------------------------

  def set_wifi(self,wifi):
    """ set wifi-object """
    self._wifi = wifi

  # --- create inverter-object   ---------------------------------------------

  def _create_inverter(self):
    """ create inverter object """

    # setup interface
    self.msg("DataProvider: creating EcuReader")
    import ecu_reader
    if not self._wifi.radio:
      self._wifi.connect()
    self._inverter = ecu_reader.EcuReader(
      app_config.remote_ip,self._wifi.pool,
      port=getattr(app_config, "remote_port", 8899),
      debug=self._debug)

  # --- return mock data   ---------------------------------------------------

  def _get_mock_data(self):
    """ create mock data """

    data = {}
    data['current_power'] = app_config.mock_data[self._mock_index]
    self._mock_index = (self._mock_index+1) % len(app_config.mock_data)

    # use "now" for timestamp
    ts = time.localtime()
    data['timestamp'] = "%04d-%02d-%02d %02d:%02d:%02d" % (
        ts.tm_year,ts.tm_mon,ts.tm_mday,
        ts.tm_hour,ts.tm_min,ts.tm_sec
        )
    return data

  # --- query data   ---------------------------------------------------------

  def update_data(self,data):
    """ callback for App: query data and update data-object """

    if not self._inverter and not app_config.mock:
      self._create_inverter()
    
    # read data from socket
    self.msg("DataProvider: reading data...")
    if app_config.mock:
      self.msg("DataProvider: using mock data...")
      ecu_data = self._get_mock_data()
    else:
      ecu_data = self._inverter.asdict()                 # this will auto-update
    self.msg(f"DataProvider: {ecu_data=}")

    # update
    data.update(ecu_data)
