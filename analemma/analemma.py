#!/usr/bin/env python3
'''
Copyright <2019> <Danny Antaki>
Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
of the Software, and to permit persons to whom the Software is furnished to 
do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in 
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
SOFTWARE.
'''

from pysolar.solar import *
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from argparse import RawTextHelpFormatter
import argparse,os,sys
import numpy as np
from sys import platform as sys_pf
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")


__version__='0.0.1'
__usage__="""

   \    \ |   \   |    __|  \  |  \  |   \   
  _ \  .  |  _ \  |    _|  |\/ | |\/ |  _ \  
_/  _\_|\_|_/  _\____|___|_|  _|_|  _|_/  _\ 

-------- map the analemma in the sky --------

Version {}
Author: Danny Antaki dantaki at ucsd dot edu
  analemma  -lat <latitude>  -lon <longitude>
            -y <year> -h <hour> -m <minute>
            -s <seasons> -f <figsize> -o <output> 
    
arguments:
  
  -lat      latitude in decimal degrees      [default: -23.43678]
  -lon      longitude in decimal degrees     [default: 0]
  -y        year                             [default: 2018]
  -h        hour in 24-hour clock format     [default: 12]
  -m        minute                           [default: 0]
  -s        label the equinoxes and soltices 
  -o        output file                      [default: analemma.png]
  
  -help        show this message and exit
     
""".format(__version__)

### date functions
def get_dates(year,hour,minute):
    # return the dates
    months = list(range(1,13))
    days = list(range(1,30,15))
    dates = []
    for m in months:
        for d in days:
            dates.append(datetime.datetime(year,m,d,hour,minute,tzinfo=datetime.timezone.utc))
    return dates
def seasons(year,hour,minute):
    # hardcoded only for 2018 
    # can implement pyephem to get actual dates of  seasons
    dates = []
    m = [3,6,9,12]
    d = [20,21,23,21]
    for i in range(0,4):
        dates.append(datetime.datetime(year,m[i],d[i],hour,minute,tzinfo=datetime.timezone.utc))
    return dates

### solar functions
def solar_alt_azi(lat,lon,year=2019,hour=12,minute=0):
    # returns the altitude and the azimuth of the sun
    # at a given location and time
    dates = get_dates(year,hour,minute)
    alt,azi = [],[]
    for d in dates:
        alt.append(get_altitude(lat,lon,d))
        azi.append(get_azimuth(lat,lon,d))
    return alt,azi,dates
def solar_alt_azi_seasons(lat,lon,year,hour,minute):
    # returns the altitude and the azimuth of the sun
    # at a given location and year for the starts of the seasons
    dates = seasons(year,hour,minute)
    alt,azi = [],[]
    for d in dates:
        alt.append(get_altitude(lat,lon,d))
        azi.append(get_azimuth(lat,lon,d))
    return alt,azi,dates

### plotting functions
def plot_analemma(alt,azi,figsize=8, 
                  label_coord=True,label_seasons=True, label_card=True, 
                 sky_color='#b9e3f3', sun_color = '#FDB813' ):
    
    # plotting function for the analemma 
    f, ax = plt.subplots(1,1,figsize=(figsize,figsize))
    width = 20000000
    m = Basemap(width=width,height=width,projection='aeqd',
                lat_0=90,lon_0=180,celestial=True,resolution='f',ax=ax)

    m.drawmapboundary(fill_color=sky_color)
    m.drawparallels(np.arange(0,91, 10),color='gray',dashes=[1,3])
    coord_labs = [1,1,1,1]
    if label_coord==False: coord_labs = [0,0,0,0] 
    m.drawmeridians(np.arange(-180,180,10),color='gray',dashes=[1,3],labels=coord_labs)
    
    xpt,ypt = m(azi,alt)
    m.plot(xpt,ypt,'ko',color=sun_color,markeredgecolor='k',markersize=12)
    if label_card == True:
        ax.annotate('N', xy=(0.485, 0.95), xycoords='axes fraction',weight='bold',fontsize=18)
        ax.annotate('E', xy=(0.95, 0.485), xycoords='axes fraction',weight='bold',fontsize=18)
        ax.annotate('W', xy=(0.01, 0.485), xycoords='axes fraction',weight='bold',fontsize=18)
        ax.annotate('S', xy=(0.485, 0.01), xycoords='axes fraction',weight='bold',fontsize=18)

    return f,ax,m

def plot_season(alt,azi,dates,ax,basemap, \
                sun_color = '#FDB813',label_dates=True):
    
    # plotting function for the seasons

    labs = ['Mar. Equinox', 'Jun. Solstice', 'Sep. Equinox', 'Dec. Solstice']
    offs = [1,1,-1,-1]
    xoff = [5,1,42,1]
    yoff = [1,10,1,20]
    xpt,ypt = basemap(azi,alt)
    basemap.plot(xpt,ypt,'ko',color=sun_color,markeredgecolor='k',markersize=12,zorder=0)
    if label_dates==True:
        for i, (x,y) in enumerate(zip(xpt,ypt)):
            ax.annotate(labs[i], (x,y), \
                        xytext=(2*offs[i]*xoff[i],1*yoff[i]*offs[i]),\
                        textcoords='offset points', weight='bold')

#######################################

def Analemma(lat,lon=0,year=2018,hour=12,minute=0,
             savefig=None,plot_seasons=True,figsize=8):
    
    # main function. Best to assume longitude is on GMT
    alt,azi,dates = solar_alt_azi(lat,lon,year,hour,minute)
    f, ax, m = plot_analemma(alt,azi,figsize)
    salt,sazi,sdates = solar_alt_azi_seasons(lat,lon,year,hour,minute)
    if plot_seasons==True:
        plot_season(salt,sazi,sdates,ax,m)
    
    f.tight_layout()
    
    if savefig!=None:
        f.savefig(savefig,bbox_inches='tight',dpi=500)

#######################################
# MAIN
#######################################
def main():
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter, usage=__usage__, add_help=False)
    args = parser.add_argument_group('arguments')
    args.add_argument('-lat',type=float,default=-23.43678,required=False)
    args.add_argument('-lon',type=float,default=0,required=False)
    args.add_argument('-y',type=int,default=2018,required=False)
    args.add_argument('-h',type=int,default=12,required=False)
    args.add_argument('-m',type=int,default=0,required=False)
    args.add_argument('-s',required=False, action="store_true", default=True)
    args.add_argument('-f',type=int,default=8,required=False)
    args.add_argument('-o',type=str,default='analemma.png',required=False)
    args.add_argument('-H', '-help', required=False, action="store_true", default=False)
    
    _args = parser.parse_args()
    lat, lon = _args.lat, _args.lon
    year, hour, minute = _args.y, _args.h, _args.m
    figsize, seasons, out, _help = _args.f, _args.s, _args.o, _args.H
    if (_help==True ):
        print(__usage__)
        sys.exit(0)

    Analemma(lat,lon,year,hour,minute,out,seasons,figsize)
    