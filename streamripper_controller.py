#!/usr/bin/env python
__author__ = 'OpenStove'
"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import ConfigParser
import threading
from os.path import expanduser
import re
import subprocess
import sys
import humanfriendly
import time
import streamripper_gui as gui

class streamerControler:
    def __init__(self,**kwargs):
        self.workers={}

        self.configFile=kwargs.get("configFile",expanduser("~/.config/streamripper_tray.conf"))
        config=kwargs.get("config",{})

        #get config
        if config=={}:
            self.config=ConfigParser.ConfigParser()
            self.config.read([self.configFile])
            print self.config

        self.parse_config()
        self.start_tray()


    def parse_config(self):
        for s in self.config.sections() :
            if s !="general":
                t=threading.Thread(target=streamerWorker,name=s,args=(s,self))
                t.start()

    def start_tray(self):
        self.appindicator=gui.Trayicon(self)

class streamerWorker():
    def __init__(self,workerName,controler):
        self.name=workerName
        self.controler=controler
        self.config={}

        self.total_size=0
        self.total_count=0

        self.actual={}

        self.parse_config(controler.config)
        self.start()

    def parse_config(self,config):
        for section in ["general",self.name]:
            self.config.update(config.items(section))
            print ("worker='%s' config=%s'" % (self.name,self.config))

    def start(self):
        #print self.config["url"],self.config["options"],"-d",self.config["output_directory"]
        process=subprocess.Popen(["streamripper", self.config["url"],self.config["options"],"-d",self.config["output_directory"]],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        while True:
            out=process.stdout.readline()
            if len(out)==0:
                break
            self.process_output(out)




    def process_output(self,out):

            print  out
            p=re.compile("\[(?P<status>\w+).*\]\s*(?P<author>[^-]*)\s*-\s*(?P<title>[^\[]*)\s*\[\s*(?P<size>[^\]]+)")
            m=re.match(p,out)
            if m!=None:
                new= m.groupdict()
                print new
                if new["status"]=="ripping":
                    self.song_changed(new)




    def song_changed(self,new_props):
        self.actual=new_props
        self.total_count+=1
        self.total_size+=self.get_sizeInBytes(new_props["size"])
        print self.get_status()

    def get_status(self):
        row={}
        row.update(self.actual)
        row.update({"total_size":humanfriendly.format_size(self.total_size),"total_count":self.total_count})
        return row

    def get_sizeInBytes(self,sizeInString):
        r=re.match(re.compile("(?P<num>\d+(,\d+)?)(?P<unit>\w+)"),sizeInString)
        nume=r.group("num")
        nume=int(round(float(nume.replace(",",".")),0))
        hf="%d%s" % (nume,r.group("unit"))
        print hf
        result=humanfriendly.parse_size(hf)
        return result


if __name__ == '__main__':
    test=streamerControler()