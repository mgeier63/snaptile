#!/usr/bin/env python3

from __future__ import print_function

import sys, getopt

import signal
from Xlib import display, X

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
from window import position
from keyutil import get_posmap, initkeys, initkey0

global keymap 
keymap = (
    ['Num_Lock', 'KP_Divide', 'KP_Multiply', 'KP_Subtract'],
    ['KP_7', 'KP_8', 'KP_9', 'KP_Add'],
    ['KP_4', 'KP_5', 'KP_6', 'KP_Delete'],
    ['KP_1', 'KP_2', 'KP_3', 'KP_Enter']
)


def global_inital_states():
    displ = display.Display()
    rt = displ.screen().root
    rt.change_attributes(event_mask=X.KeyPressMask)

    return (
        displ,
        rt,
        {
            'code': 0,
            'pressed': False
        },
        get_posmap(keymap,  displ),
    )

global disp, root, lastkey_state, posmap, posmapLeft;


def run():
    mask = None

    opts, args = getopt.getopt(sys.argv[1:], "hdWk:")
    
    for opt in opts:
        if opt[0] == '-h':
            print ('Snaptile.py')
            print ('-W use Windows key')
            print ('-h this help text')
            sys.exit()
        elif opt[0] == '-d':
            isDualMonitor = True
        elif opt[0] == '-W':
            mask = 'Windows'


    global disp, root, lastkey_state, posmap, posmapLeft
    disp, root, lastkey_state, posmap = global_inital_states()

    initkey0(disp,root)
    initkeys(keymap, disp, root)


    for _ in range(0, root.display.pending_events()):
        root.display.next_event()
    GObject.io_add_watch(root.display, GObject.IO_IN, checkevt)
    print('Snaptile running. Press CTRL+C to quit.')
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Gtk.main()

def checkevt(_, __, handle=None):
    global lastkey_state

    handle = handle or root.display
    for _ in range(0, handle.pending_events()):
        event = handle.next_event()

        if event.type == X.KeyPress:

            scrn = 0
            mod1Pressed =  (event.state | X.Mod1Mask) == event.state
            if (mod1Pressed):
                scrn = 1
            if event.detail not in posmap:
                break

            print("KEY")

            if not lastkey_state['pressed']:
                handleevt(event.detail, event.detail, scrn)

            else:
                handleevt(lastkey_state['code'], event.detail,scrn)

            lastkey_state = {
                'code': event.detail,
                'pressed': True
            }

        if event.type == X.KeyRelease:
            if event.detail == lastkey_state['code']:
                lastkey_state['pressed'] = False

    return True

def handleevt(startkey, endkey, scrn):
    position(
        posmap[startkey],
        posmap[endkey],
        scrn
    )

if __name__ == '__main__':
    run()
