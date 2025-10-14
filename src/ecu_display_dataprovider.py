# ----------------------------------------------------------------------------
# Read current power from an APSystems ECU-x.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-ecu-display
# ----------------------------------------------------------------------------

from settings import app_config

# --- main data-provider class   ---------------------------------------------

class DataProvider:

  def __init__(self):
    self._debug = getattr(app_config, "debug", False)
    self._wifi  = None
    self._inverter = None

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
    self._inverter = ecu_reader.EcuReader(
      app_config.remote_ip,self._wifi.pool,
      port=getattr(app_config, "remote_port", 8899),
      debug=self._debug)

  # --- query data   ---------------------------------------------------------

  def update_data(self,data):
    """ callback for App: query data and update data-object """

    if not self._inverter:
      self._create_inverter()
    
    # read data from socket
    self.msg("DataProvider: reading data...")
    ecu_data = self._inverter.asdict()                 # this will auto-update
    self.msg(f"DataProvider: {data=}")

    # update
    data.update(ecu_data)
