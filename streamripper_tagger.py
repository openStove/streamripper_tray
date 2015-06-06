from mutagen.id3 import ID3
from pyechonest import song

class songTags(ID3):
    def __init__(self,path):
        ID3.__init__(self,path)
        self.title=self.get("TIT2")
        self.artist=self.get("TPE1")
        self.printAll()

    def printAll(self):
        for k in self.keys():
            print "%s=%s" % (k,self.get(k))


class echonest_request:
    def __init__(self,api_key):
        self.api_key=api_key

    def getSong(self,artist,title):
        results = song.search(artist=artist, title=title)
        result = results[0]
        print result.artist_location
        print 'tempo:',result.audio_summary['tempo'],'duration:',result.audio_summary['duration']
        print result.audio_summary

test=songTags(r"/home/wsb/Music/Africando - Ma Won Mio.mp3")


from pyechonest import config
config.ECHO_NEST_API_KEY=API_KEY
r=echonest_request(API_KEY).getSong(test.artist,test.title)