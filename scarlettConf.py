#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk 
from gi.repository import Gdk 
from gi.repository import GLib, GObject 
import subprocess
import os
import configparser


def saveSettings(settings) :
    with open(settings[1], "w") as configfile :
        settings[0].write(configfile)
    print("settings saved")

def clicked_MixerButton(widget, settings) :
    cmd = settings[0]["scarlettConf"]["mixer"]
    try :
        subprocess.Popen(cmd)
    except :
        print("could not start mixer")

def setFile_FileButton(widget, settings, FileSaver) :
    conf = widget.get_filename()
    alsactl = settings[0]["scarlettConf"]["alsactlPath"]
    try :
        subprocess.run([alsactl, "--file", conf, "restore"])
        settings[0]["scarlettConf"]["config"] = conf
        saveSettings(settings)
        FileSaver.set_filename(conf)
    except :
        print("could not load config")

def clicked_SaveButton(widget,FileSaver, settings) :
    FileSaver.show()

def clicked_PrefButton(widget, PrefWindow) :
    PrefWindow.show()

def clicked_PrefCloseButton(widget, PrefWindow) :
    PrefWindow.hide()

def changed_PrefMixerEntry(widget, eventFocus, settings) :
    settings[0]["scarlettConf"]["mixer"] = widget.get_text()
    saveSettings(settings)

def changed_PrefAlsactlEntry(widget, eventFocus, settings) :
    settings[0]["scarlettConf"]["alsactlPath"] = widget.get_text()
    saveSettings(settings)

def toggled_PrefMixButton(widget, settings) :
    settings[0]["scarlettConf"]["startMixer"] = str(widget.get_active())
    saveSettings(settings)

def clicked_FileSaverSave(widget, settings, FileSaver, FileButton) :
    conf = FileSaver.get_filename()
    alsactl = settings[0]["scarlettConf"]["alsactlPath"]
    try :   
        subprocess.run([alsactl, "--file", conf, "store"])
        FileButton.set_filename(conf)
        settings[0]["scarlettConf"]["config"] = conf
        saveSettings(settings)
    except :
        print("could not save config")

    FileSaver.hide()

def hide_FileSaver(widget, FileSaver) :
    FileSaver.hide()



def app_activate(app) :

    # create config dir and file
    settingsDir = os.environ["HOME"] + "/.config/scarlettConf"
    if not os.path.isdir(settingsDir) :
        os.mkdir(settingsDir)
    settingsFile = settingsDir + "/settings.ini"
    if not os.path.isfile(settingsFile) :
        os.mknod(settingsFile)
    
    # load settings from file or set defaults
    parser = configparser.ConfigParser()
    parser.read(settingsFile)
    if not "scarlettConf" in parser :
        parser.add_section("scarlettConf")

    if not "alsactlPath" in parser["scarlettConf"] :
        alsactl = "/usr/bin/alsactl"
        parser["scarlettConf"]["alsactlPath"] = alsactl
    else :
        alsactl = parser["scarlettConf"]["alsactlPath"]
    
    if not "mixer" in parser["scarlettConf"] :
        mixer = "scarlettmixer"
        parser["scarlettConf"]["mixer"] = mixer
    else :
        mixer = parser["scarlettConf"]["mixer"]
    
    if not "startMixer" in parser["scarlettConf"] :
        startMixer = False
        parser["scarlettConf"]["startMixer"] = str(startMixer)
    else :
        startMixer = parser["scarlettConf"].getboolean("startMixer")

    if not "config" in parser["scarlettConf"] :
        conf = " " 
    else :
        conf = parser["scarlettConf"]["config"]

    # save settings
    settings = (parser, settingsFile)
    saveSettings(settings)


    builder = Gtk.Builder()
    # gui is defined in xml ( made with glade) see line 178 to 475
    builder.add_from_string(gui)

    # set up Mainwindow
    MainWindow = builder.get_object("MainWindow")
    MainWindow.set_application(app)
    MainWindow.show()

    FileButton = builder.get_object("FileButton")
    if conf == " " :
        FileButton.set_current_folder(os.environ["HOME"])
    else :
        FileButton.set_filename(conf)

    FileSaver = builder.get_object("FileSaver")
    if conf == " " :
        FileSaver.set_current_folder(os.environ["HOME"])
    else :
        FileSaver.set_filename(conf)


    PrefMixButton = builder.get_object("PrefMixButton")
    PrefMixButton.set_active(startMixer)

    PrefMixerEntry = builder.get_object("PrefMixerEntry")
    PrefMixerEntry.set_text(mixer)

    PrefAlsactlEntry = builder.get_object("PrefAlsactlEntry")
    PrefAlsactlEntry.set_text(alsactl)

    # set up Preferences window
    PrefWindow = builder.get_object("PrefWindow")

    handler = {
            "on_MixerButton_clicked" : (clicked_MixerButton, settings),
            "on_FileButton_file_set" : (setFile_FileButton, settings, FileSaver),
            "on_SaveButton_clicked"  : (clicked_SaveButton,FileSaver, settings),
            "on_PrefButton_clicked"  : (clicked_PrefButton, PrefWindow),
            "on_PrefCloseButton_clicked"  : (clicked_PrefCloseButton, PrefWindow),
            "on_PrefMixerEntry_focus_out_event" : (changed_PrefMixerEntry, settings),
            "on_PrefAlsactlEntry_focus_out_event" : (changed_PrefAlsactlEntry, settings),
            "on_PrefMixButton_toggled": (toggled_PrefMixButton, settings),
            "on_FileSaverCancel_clicked" : (hide_FileSaver, FileSaver),
            "on_FileSaverSave_clicked" : (clicked_FileSaverSave, settings, FileSaver, FileButton)
            }
    builder.connect_signals(handler)

    # start scarlettmixer if startMixer is set to true
    if startMixer :
        print("run", mixer)
        subprocess.Popen(mixer)

def main() :
    app = Gtk.Application.new("org.scarlettconf.app",0)
    app.connect("activate", app_activate)
    app.run()

gui = """
<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated with glade 3.22.1 -->
<interface>
  <requires lib="gtk+" version="3.20"/>
  <object class="GtkFileChooserDialog" id="FileSaver">
    <property name="can_focus">False</property>
    <property name="title" translatable="yes">save config</property>
    <property name="resizable">False</property>
    <property name="destroy_with_parent">True</property>
    <property name="type_hint">dialog</property>
    <property name="urgency_hint">True</property>
    <property name="deletable">False</property>
    <property name="action">save</property>
    <property name="do_overwrite_confirmation">True</property>
    <child>
      <placeholder/>
    </child>
    <child internal-child="vbox">
      <object class="GtkBox">
        <property name="can_focus">False</property>
        <property name="orientation">vertical</property>
        <property name="spacing">2</property>
        <child internal-child="action_area">
          <object class="GtkButtonBox">
            <property name="can_focus">False</property>
            <property name="layout_style">end</property>
            <child>
              <object class="GtkButton" id="FileSaverCancel">
                <property name="label" translatable="yes">cancel</property>
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="receives_default">True</property>
                <signal name="clicked" handler="on_FileSaverCancel_clicked" swapped="no"/>
              </object>
              <packing>
                <property name="expand">True</property>
                <property name="fill">True</property>
                <property name="position">0</property>
              </packing>
            </child>
            <child>
              <object class="GtkButton" id="FileSaverSave">
                <property name="label" translatable="yes">save</property>
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="receives_default">True</property>
                <signal name="clicked" handler="on_FileSaverSave_clicked" swapped="no"/>
              </object>
              <packing>
                <property name="expand">True</property>
                <property name="fill">True</property>
                <property name="position">1</property>
              </packing>
            </child>
          </object>
          <packing>
            <property name="expand">False</property>
            <property name="fill">False</property>
            <property name="position">0</property>
          </packing>
        </child>
        <child>
          <placeholder/>
        </child>
      </object>
    </child>
  </object>
  <object class="GtkApplicationWindow" id="MainWindow">
    <property name="can_focus">False</property>
    <property name="title" translatable="yes">scarlettConf</property>
    <property name="resizable">False</property>
    <property name="default_width">400</property>
    <property name="default_height">100</property>
    <property name="show_menubar">False</property>
    <child>
      <placeholder/>
    </child>
    <child>
      <object class="GtkBox">
        <property name="visible">True</property>
        <property name="can_focus">False</property>
        <property name="orientation">vertical</property>
        <property name="spacing">10</property>
        <child>
          <object class="GtkBox">
            <property name="visible">True</property>
            <property name="can_focus">False</property>
            <property name="homogeneous">True</property>
            <child>
              <object class="GtkButton" id="PrefButton">
                <property name="label">gtk-preferences</property>
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="receives_default">True</property>
                <property name="use_stock">True</property>
                <property name="always_show_image">True</property>
                <signal name="clicked" handler="on_PrefButton_clicked" swapped="no"/>
              </object>
              <packing>
                <property name="expand">False</property>
                <property name="fill">True</property>
                <property name="padding">10</property>
                <property name="position">0</property>
              </packing>
            </child>
            <child>
              <object class="GtkFileChooserButton" id="FileButton">
                <property name="visible">True</property>
                <property name="can_focus">False</property>
                <property name="do_overwrite_confirmation">True</property>
                <property name="use_preview_label">False</property>
                <property name="title" translatable="yes">load config</property>
                <signal name="file-set" handler="on_FileButton_file_set" swapped="no"/>
              </object>
              <packing>
                <property name="expand">False</property>
                <property name="fill">True</property>
                <property name="padding">5</property>
                <property name="position">1</property>
              </packing>
            </child>
            <child>
              <object class="GtkButton" id="SaveButton">
                <property name="label">gtk-save</property>
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="receives_default">True</property>
                <property name="margin_left">15</property>
                <property name="margin_right">15</property>
                <property name="use_stock">True</property>
                <signal name="clicked" handler="on_SaveButton_clicked" swapped="no"/>
              </object>
              <packing>
                <property name="expand">False</property>
                <property name="fill">True</property>
                <property name="padding">5</property>
                <property name="position">2</property>
              </packing>
            </child>
          </object>
          <packing>
            <property name="expand">False</property>
            <property name="fill">True</property>
            <property name="padding">10</property>
            <property name="position">1</property>
          </packing>
        </child>
        <child>
          <object class="GtkButton" id="MixerButton">
            <property name="label" translatable="yes">open Mixer</property>
            <property name="visible">True</property>
            <property name="can_focus">True</property>
            <property name="receives_default">True</property>
            <property name="margin_left">40</property>
            <property name="margin_right">40</property>
            <signal name="clicked" handler="on_MixerButton_clicked" swapped="no"/>
          </object>
          <packing>
            <property name="expand">False</property>
            <property name="fill">True</property>
            <property name="padding">10</property>
            <property name="position">2</property>
          </packing>
        </child>
      </object>
    </child>
  </object>
  <object class="GtkWindow" id="PrefWindow">
    <property name="can_focus">False</property>
    <property name="resizable">False</property>
    <property name="destroy_with_parent">True</property>
    <property name="urgency_hint">True</property>
    <property name="deletable">False</property>
    <child type="titlebar">
      <placeholder/>
    </child>
    <child>
      <object class="GtkBox">
        <property name="visible">True</property>
        <property name="can_focus">False</property>
        <property name="orientation">vertical</property>
        <property name="spacing">5</property>
        <child>
          <object class="GtkCheckButton" id="PrefMixButton">
            <property name="label" translatable="yes">open mixer on startup</property>
            <property name="visible">True</property>
            <property name="can_focus">True</property>
            <property name="receives_default">False</property>
            <property name="draw_indicator">True</property>
            <signal name="toggled" handler="on_PrefMixButton_toggled" swapped="no"/>
          </object>
          <packing>
            <property name="expand">False</property>
            <property name="fill">True</property>
            <property name="padding">10</property>
            <property name="position">1</property>
          </packing>
        </child>
        <child>
          <object class="GtkBox" id="P">
            <property name="visible">True</property>
            <property name="can_focus">False</property>
            <property name="spacing">5</property>
            <child>
              <object class="GtkLabel">
                <property name="visible">True</property>
                <property name="can_focus">False</property>
                <property name="margin_left">5</property>
                <property name="label" translatable="yes">Mixer command : </property>
              </object>
              <packing>
                <property name="expand">False</property>
                <property name="fill">True</property>
                <property name="position">0</property>
              </packing>
            </child>
            <child>
              <object class="GtkEntry" id="PrefMixerEntry">
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="margin_right">5</property>
                <signal name="focus-out-event" handler="on_PrefMixerEntry_focus_out_event" swapped="no"/>
              </object>
              <packing>
                <property name="expand">False</property>
                <property name="fill">True</property>
                <property name="position">1</property>
              </packing>
            </child>
          </object>
          <packing>
            <property name="expand">False</property>
            <property name="fill">True</property>
            <property name="position">2</property>
          </packing>
        </child>
        <child>
          <object class="GtkBox">
            <property name="visible">True</property>
            <property name="can_focus">False</property>
            <property name="spacing">17</property>
            <child>
              <object class="GtkLabel">
                <property name="visible">True</property>
                <property name="can_focus">False</property>
                <property name="margin_left">5</property>
                <property name="label" translatable="yes">Path to alsactl : </property>
              </object>
              <packing>
                <property name="expand">False</property>
                <property name="fill">True</property>
                <property name="position">0</property>
              </packing>
            </child>
            <child>
              <object class="GtkEntry" id="PrefAlsactlEntry">
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="margin_left">3</property>
                <property name="margin_right">5</property>
                <signal name="focus-out-event" handler="on_PrefAlsactlEntry_focus_out_event" swapped="no"/>
              </object>
              <packing>
                <property name="expand">False</property>
                <property name="fill">True</property>
                <property name="position">1</property>
              </packing>
            </child>
          </object>
          <packing>
            <property name="expand">False</property>
            <property name="fill">True</property>
            <property name="padding">5</property>
            <property name="position">3</property>
          </packing>
        </child>
        <child>
          <object class="GtkButton" id="PrefCloseButton">
            <property name="label" translatable="yes">close</property>
            <property name="visible">True</property>
            <property name="can_focus">True</property>
            <property name="receives_default">True</property>
            <property name="margin_left">20</property>
            <property name="margin_right">20</property>
            <property name="margin_top">10</property>
            <property name="margin_bottom">10</property>
            <signal name="clicked" handler="on_PrefCloseButton_clicked" swapped="no"/>
          </object>
          <packing>
            <property name="expand">False</property>
            <property name="fill">True</property>
            <property name="position">4</property>
          </packing>
        </child>
      </object>
    </child>
  </object>
</interface>
"""

if __name__ == "__main__" :
    main()

