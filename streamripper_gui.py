__author__ = 'OpenStove'
#!/usr/bin/env python
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
import sys
from gi.repository import Gtk,GObject

from time import sleep

class statusWindow(Gtk.Window):
    def __init__(self,controller):
        Gtk.Window.__init__(self,title="StreamRipper Status")
        self.controller=controller
        self.stream_header=None
        self.streams=[]


        self.box = Gtk.ListBox()
        self.add(self.box)

        self.status_grid=statusGrid(self)
        self.box.add(self.status_grid)
        self.status_grid.add_header(['status','author','title', 'total_size','total_count', 'size'])

        for cs in self.controller.workers:
            print "worker name=%s" % cs.name
            self.status_grid.add_stream(cs.get_status())
        #self.add_stream()




    def on_button1_clicked(self, widget):
        print("Hello")

    def on_button2_clicked(self, widget):
        print("Goodbye")





class statusGrid(Gtk.Grid):
    def __init__(self,parent=None):
        Gtk.Grid.__init__(self)
        self.set_column_spacing(6)
        self.parent=parent
        self.streams={}
        self.header_col={}


    def add_header(self,labels):
        i=1
        for k  in labels:
            l=Gtk.Label(k)
            l.set_justify=Gtk.Justification.LEFT
            self.attach(l,i,1,1,1)
            self.header_col[k]=i
            i+=1

    def add_stream(self,props):
        myLabels={}
        row=len(self.streams)+2
        for k,v in props.items():
            l=Gtk.Label(v)
            l.set_justify=Gtk.Justification.LEFT
            self.attach(l,self.header_col[k],row,1,1)
            myLabels[k]=l
        self.streams[props["Stream"]]=myLabels





class Trayicon (GObject.Object):
    def __init__(self,controller):
        self.controller=controller
        self.element=None
        self.active=False
        __gtype_name__ = 'TrayiconPlugin'
        object = GObject.property (type=GObject.Object)
        self.do_activate()


    def do_activate (self):
        self.staticon = Gtk.StatusIcon ()
        self.staticon.set_from_stock (Gtk.STOCK_ABOUT)
        self.staticon.connect ("activate", self.trayicon_activate)
        self.staticon.connect ("popup_menu", self.trayicon_popup)
        self.staticon.set_visible (True)
        Gtk.main()




    def trayicon_activate (self, widget, data = None):

        if self.element==None :
            self.element=statusWindow(self.controller)

        print "toggle app window! state=%s" % self.element.is_active()
        self.element.show_all()
        if self.element.is_active():

            self.element.show_all()
        else :
            pass
            #self.element.hide_all()




    def trayicon_quit (self, widget, data = None):
        print "quit app!"
        del self.controller
        self.destroy()



    def trayicon_popup (self, widget, button, time, data = None):
        self.menu = Gtk.Menu ()


        menuitem_toggle = Gtk.MenuItem ("Show / Hide")
        menuitem_quit = Gtk.MenuItem ("Quit")
        menuitem_about=Gtk.MenuItem ("About")


        menuitem_toggle.connect ("activate", self.trayicon_activate)
        menuitem_quit.connect ("activate", self.trayicon_quit)
        menuitem_about.connect("activate",self.show_about_dialog)


        self.menu.append (menuitem_toggle)
        self.menu.append (menuitem_quit)
        self.menu.append(menuitem_about)


        self.menu.show_all ()
        self.menu.popup(None, None, lambda w,x: self.staticon.position_menu(self.menu, self.staticon), self.staticon, 3, time)


    def do_deactivate (self):
        self.staticon.set_visible (False)
        del self.staticon

    def show_about_dialog(self, widget):
        about_dialog = Gtk.AboutDialog()

        about_dialog.set_destroy_with_parent(True)
        about_dialog.set_name("StreamRipper Tray")
        about_dialog.set_version("0.1")
        about_dialog.set_authors(["Open Stove"])

        about_dialog.run()
        about_dialog.destroy()