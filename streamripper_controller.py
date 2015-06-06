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
import streamripper_tray as gui
import my_utils
from gi.repository import Gtk

class StopThread(StopIteration): pass

class streamercontroller:
    def __init__(self,**kwargs):
        self.workers=[]
        self.appindicator=None

        self.configFile=expanduser(kwargs.get("configFile","~/.config/streamripper_tray.conf"))
        config=kwargs.get("config",{})

        #get config
        if config=={}:
            self.config=ConfigParser.ConfigParser()
            self.config.read([self.configFile])
            print "actual config from streamercontroller:\n %s with sections=%s" % (self.config,self.config.sections())
            if len(self.config.sections())==0:
                sys.exit("unable to load config file : aborting")
                
        self.test_config()
        self.parse_config()
        


    def parse_config(self):
        for s in self.config.sections() :

            if s !="general":
                self.workers.append(streamerWorker(s,self))
                
    def test_config(self):
        exe=self.config.get("general","streamripper_bin")
        #test streamripper binary
        if not my_utils.exe_exists(exe):
            sys.exit("Could not find streamripper executable : %s" % exe)
            

    def start_tray(self):
        self.appindicator=gui.Trayicon(self)

    def quit(self):
        for k,v in self.workers.items():
            v.stop()

    def get_streamWorker_by_name(self,name):
        for i in self.workers:
            if i.name==name:
                return i

class streamerWorker():
    def __init__(self,workerName,controller):
        self.name=workerName
        self.controller=controller
        self.config={}
        self.running=0
        self.status="stopped"
        self.process=None

        self.total_size=0
        self.total_count=0

        self.actual={}


        self.parse_config(controller.config)

        if self.config["autostart"] in ["True","true"]:
            self.start()

    def parse_config(self,config):
        for section in ["general",self.name]:
            self.config.update(config.items(section))
            print ("worker='%s' config=%s'" % (self.name,self.config))

    def start(self):
        self.running=True
        self.thread=threading.Thread(target=self.run, name=self.name)
        self.thread.start()
        self.status="running"


    def stop(self):
        print "try to stop thread %s" % self.name
        self.status="stopped"
        self.running=False
        if self.process:
            self.process.kill()
        #self.thread.join()

    def run(self):
        #preparing executable array
        exe=[]
        exe.append(self.controller.config.get("general","streamripper_bin"))
        exe.append(self.config["url"])
        for o in self.config["options"].split():
            exe.append(o)
        exe.append("-d")
        exe.append(self.config["output_directory"])
        print "start executing... %s" % exe
        self.process=getattr(subprocess,"Popen")(exe,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        while self.running==True:
            out=self.process.stdout.readline()
            if len(out)==0:
                break
            self.process_output(out)
        print "%s exiting" % self.name




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
        row={"Stream":self.name}
        row.update(self.actual)
        row.update({"running":self.running,"status":self.status,"total_size":humanfriendly.format_size(self.total_size),"total_count":self.total_count})
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
    test=streamercontroller()
    Gtk.main()