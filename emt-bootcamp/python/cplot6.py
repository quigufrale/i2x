# Copyright (C) 2018-2023 Battelle Memorial Institute
# file: cplot6.py
""" Plots COMTRADE channels from plant model SCR ramping.
"""

import sys
import os
import math
import matplotlib.pyplot as plt
import numpy as np
from comtrade import Comtrade

plt.rcParams['savefig.directory'] = os.getcwd()

kVLNbase = 230.0 / math.sqrt(3.0)
MVAbase = 100.0
kAbase = MVAbase / kVLNbase / 3.0

def scale_factor(lbl, bPSCAD):
  if 'P' in lbl:
    return 1.0 / MVAbase
  elif 'Q' in lbl:
    return 1.0 / MVAbase
  elif 'I' in lbl:
    return 1.0 / kAbase / math.sqrt(2.0)
  elif 'Vrms' in lbl:
    if not bPSCAD:
      return 1.0 / kVLNbase
  elif 'V' in lbl:
    return 1.0 / kVLNbase / math.sqrt(2.0)
  return 1.0

def setup_plot_options():
  plt.rcParams['savefig.directory'] = os.getcwd()
  lsize = 12
  plt.rc('font', family='serif')
  plt.rc('xtick', labelsize=lsize)
  plt.rc('ytick', labelsize=lsize)
  plt.rc('axes', labelsize=lsize)
  plt.rc('legend', fontsize=10)

def show_case_plot(channels, units, title, bPSCAD, tmax=40.0, PNGName=None):
  x_ticks = np.linspace (0.0, tmax, 10)
  t = channels['t']
  fig, ax = plt.subplots(5, 1, sharex = 'col', figsize=(15,10), constrained_layout=True)
  fig.suptitle (title)
  for lbl in ['VA', 'VB', 'VC']:
    ax[0].plot (t, scale_factor(lbl, bPSCAD) * channels[lbl], label=lbl)
    ax[0].set_ylabel ('V(t) [pu]')
  for lbl in ['IA', 'IB', 'IC']:
    ax[1].plot (t, scale_factor(lbl, bPSCAD) * channels[lbl], label=lbl)
    ax[1].set_ylabel ('I(t) [pu]')
  for lbl in ['Vrms']:
    ax[2].plot (t, scale_factor(lbl, bPSCAD) * channels[lbl], label=lbl)
    ax[2].set_ylabel ('V [pu]')
  for lbl in ['P', 'Q']:
    ax[3].plot (t, scale_factor(lbl, bPSCAD) * channels[lbl], label=lbl)
    ax[3].set_ylabel ('P, Q [pu]')
  for lbl in ['F']:
    ax[4].plot (t, scale_factor(lbl, bPSCAD) * channels[lbl], label=lbl)
    ax[4].set_ylabel ('F [Hz]')
  for i in range(5):
    ax[i].set_xticks (x_ticks)
    ax[i].set_xlim (x_ticks[0], x_ticks[-1])
    ax[i].grid()
    ax[i].legend(loc='lower right')
  ax[4].set_xlabel ('seconds')
  if PNGName is not None:
    plt.savefig(PNGName)
  plt.show()
  plt.close(fig)

# load all the analog channels from each case into dictionaries of numpy arrays. Expecting:
#   1..3 = Va..Vc
#   4..6 = Ia..Ic
#   7 = Vrms
#   8 = P
#   9 = Q
#   10 = F
def load_channels(comtrade_path, bDebug=False):
  if bDebug:
    print (comtrade_path)
  rec = Comtrade ()
  rec.load (comtrade_path + '.cfg', comtrade_path + '.dat')
  t = np.array(rec.time)

  channels = {}
  units = {}
  channels['t'] = t
  print ('{:d} channels ({:d} points) read from {:s}.cfg'.format (rec.analog_count, len(t), comtrade_path))
  for i in range(rec.analog_count):
    lbl = rec.analog_channel_ids[i].strip()
    # for PSCAD naming convention, truncate the channel at first colon, if one exists
    idx = lbl.find(':')
    if idx >= 0:
      lbl = lbl[0:idx]
    ch_config = rec.cfg.analog_channels[i]
    scale = 1.0
    if ch_config.pors.upper() == 'P':
      scale = ch_config.secondary / ch_config.primary
    elif ch_config.pors.upper() == 'S':
      scale = ch_config.primary / ch_config.secondary
    if bDebug:
      print ('  "{:s}" [{:s}] scale={:.6e}'.format(lbl, ch_config.uu, scale))
    channels[lbl] = scale * np.array (rec.analog[i])
    units[lbl] = ch_config.uu

  return channels, units

if __name__ == '__main__':
  bPSCAD = True
  bSavePNG = False
  test = 'rampscr'
  if len(sys.argv) > 1:
    if int(sys.argv[1]) == 1:
      bPSCAD = False
    if len(sys.argv) > 2:
      if int(sys.argv[2]) == 1:
        bSavePNG = True

  setup_plot_options()

  # set the session_path to match location of your unzipped sample cases
  if bPSCAD:
    case_tag = 'Solar'
    session_path = 'c:/temp/i2x/pscad/Solar6.if18_x86/rank_00001/Run_00001'
    tmax = 40.0
  else:
    session_path = 'c:/temp/i2x/emtp'
    case_tag = 'Wind'
    tmax = 45.0
  if bSavePNG:
    PNGName = '{:s}_{:s}.png'.format (case_tag, test)
  else:
    PNGName = None

  tag_path = os.path.join (session_path, 'rampscr')
  channels, units = load_channels (tag_path)
  if bPSCAD: # cosmetic initialization of the frequency plot
    channels['F'][0] = 60.0
  show_case_plot (channels, units, 'Ramping SCR test: {:s}'.format(case_tag), bPSCAD, tmax, PNGName)

