import mutagen.id3 as m

from pyechonest import song

import Queue
import time
import os
from threading import Thread
import logging
from pyechonest.util import EchoNestAPIError

def my_import(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

class inputSong(m.ID3):
    def __init__(self,path):
        m.ID3.__init__(self,path)
        self.title=self.get("TIT2")
        self.artist=self.get("TPE1")
        
        logging.debug("all keys:%s" % self.items())

    def get_echonest(self,echonest_object):
        self.echonest=echonest_object.getSong(self.artist,self.title)
        
    def set_custom_props(self,echonest_object):
        self.set_tag("TALB", 1, "test")
        print self.get("TALB")
        #self.get_echonest(echonest_object)
        
    def set_tag(self,object,encoding,value):
        #id3=my_import("mutagen.id3" % object)
        frame=getattr(m,object)
        self.add(frame(encoding=encoding,text=value))
        self.save()
        
        
        
class echonest:
    api_limitation_count=8
    api_limitation_time=130
    api_call_first=0
    api_call_count=0
    
    def __init__(self,key):
        from pyechonest import config as echonest_config
        echonest_config.ECHO_NEST_API_KEY=key

    def getSong(self,artist,title):
        try:
            self.check_api_count()
            results = song.search(artist=artist, title=title)
            if len(results)==0:
                logging.warning("Could not retrieve song : %s from %s" % (title,artist))
                return None
            else:
                result = results[0]
                logging.debug("audio summary=%s" % result.audio_summary)
                return result
                
        except EchoNestAPIError,e:
            logging.exception(e)
            time.sleep(60)

            
        except timeout:
            logging.warning("request timed out for song %s from %s" % (title,artist))

            
    def check_api_count(self):
        now=time.time()
        timeDiff=int(now-self.api_call_first)
        if timeDiff>self.api_limitation_time: #time limitation passed:
            self.api_call_first=now #reset time
            self.api_call_count=1 #reset count
            logging.debug("nothing to do : timeDiff=%s count=%s" % (timeDiff,self.api_call_count))
            return True #proceed
        
        else : #time limitation is not passed
            if self.api_call_count+1<self.api_limitation_count:
                self.api_call_count+=1
                logging.debug("nothing to do : count(%s) < limit(%s)" % (self.api_call_count,self.api_limitation_count))
                return True #nothing to do, process call directly
            else:
                logging.debug("need to wait for %s s start=%s now=%s" % (timeDiff,self.api_call_first,now))
                time.sleep(timeDiff)
                self.api_call_first=now #reset time
                self.api_call_count=1 #reset count
                return True

class songTagger(Queue.Queue):
    def __init__(self,**kwargs):
        self.workers=[]
        self.echonest=None
        
        self.controller=kwargs.get("controller",None)
        self.echonest=echonest(kwargs.get("echo_nest_api_key",None))
        workers=kwargs.get("workers",1)
        
        
        Queue.Queue.__init__(self,100)
        
        for i in range(workers):
            t=Thread(target=self.worker)
            t.deamon=True
            t.start()
            self.workers.append(t)
    

        
    def put_file(self,path):
        self.put(path)
        
    def worker(self):
        while True:

                if self.empty():
                    logging.info("song tagging queue is empty at the moment")
                    time.sleep(10)
                else:
                    s=self.get()
                    print s
                    mysong=inputSong(s)
                    mysong.set_custom_props(self.echonest)
                    self.task_done()

    
if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)8s %(module)20s %(funcName)15s %(message)s',filename='streamripper.log', filemode='w', level=logging.DEBUG)
    path=os.path.expanduser("~/Music/")
    tagger=songTagger(echo_nest_api_key="V1XKDXCYPECIX0XC7")
    for file in os.listdir(path):
        current_file= os.path.join(path, file)
        if os.path.isdir(current_file)==False:
            tagger.put(current_file)
        
        
    

