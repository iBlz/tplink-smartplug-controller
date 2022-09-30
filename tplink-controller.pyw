from struct import pack
from faulthandler import disable
from tkinter import *
import subprocess
import pymsgbox
import datetime
import getpass
import socket
import time
import json
import sys
import os

user = getpass.getuser()
configfile = ('C:\\Users\\{}\AppData\\Local\\Temp\\tplink-controler-ip.txt' .format(user))

window = Tk()

commands = {'info'     : '{"system":{"get_sysinfo":{}}}',
            'on'       : '{"system":{"set_relay_state":{"state":1}}}',
            'off'      : '{"system":{"set_relay_state":{"state":0}}}',
            'cloudinfo': '{"cnCloud":{"get_info":{}}}'
}

def encrypt(string):
    key = 171
    result = pack(">I", len(string))
    for i in string:
        a = key ^ ord(i)
        key = a
        result += bytes([a])
    return result

def decrypt(string):
    key = 171
    result = ""
    for i in string:
        a = key ^ i
        key = i
        result += chr(a)
    return result

def send_command(ip,cmd):
    global decrypted
    try:
        port = 9999
        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_tcp.settimeout(10)
        sock_tcp.connect((ip, port))
        sock_tcp.settimeout(None)
        sock_tcp.send(encrypt(cmd))
        data = sock_tcp.recv(2048)
        sock_tcp.close()
        decrypted = decrypt(data[4:])
        print("Sent:     ", cmd)
        print("Received: ", decrypted)

    except socket.error:
        print("Could not connect to host %s" % ip)
        pymsgbox.alert("Could not connect to host %s" % ip ,'!')

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

if not os.path.exists(configfile):     # write instructions to devices.txt, opening notepad, and hiding the file
    pymsgbox.alert("Make sure you set your plug's ip before using!", 'First time opening detected!')
    w = open(configfile, "w")
    w.write("Your plug ip here")
    w.close()

def turn_on():
    send_command(ip,commands["on"])
    text_box.configure(state='normal',exportselection=0)
    text_box.insert('end','''
Json Send : {}
Json Received : {}'''.format(commands["on"],decrypted))
    text_box.configure(state='disabled',exportselection=0)

def turn_off():
    send_command(ip,commands["off"])
    text_box.configure(state='normal',exportselection=0)
    text_box.insert('end','''
Json Send : {}
Json Received : {}'''.format(commands["off"],decrypted))
    text_box.configure(state='disabled',exportselection=0)

def info():
    send_command(ip,commands["info"])
    text_box.configure(state='normal',exportselection=0)
    text_box.insert('end','''
Json Send : {}
Json Received : {}'''.format(commands["info"],decrypted))
    text_box.insert('end','\n\nShort version :\n')
    text_box.insert('end','''
Software Version : {}
Hardware Version : {}
Model : {}
Id : {}
Rssi : {}
Alias : {}
Mac : {}
Relay State : {}
    '''.format(json.loads(decrypted)["system"]["get_sysinfo"]["sw_ver"],json.loads(decrypted)["system"]["get_sysinfo"]["hw_ver"],json.loads(decrypted)["system"]["get_sysinfo"]["model"],json.loads(decrypted)["system"]["get_sysinfo"]["deviceId"],json.loads(decrypted)["system"]["get_sysinfo"]["rssi"],json.loads(decrypted)["system"]["get_sysinfo"]["alias"],json.loads(decrypted)["system"]["get_sysinfo"]["mac"],json.loads(decrypted)["system"]["get_sysinfo"]["relay_state"]))
    text_box.configure(state='disabled',exportselection=0)

def cloud_info():
    send_command(ip,commands["cloudinfo"])
    text_box.configure(state='normal',exportselection=0)
    text_box.insert('end','''
Json Send : {}
Json Received : {}'''.format(commands["cloudinfo"],decrypted))
    text_box.insert('end','\n\nShort version :\n')
    text_box.insert('end','''
Username : {}
Server : {}
Binded : {}
    '''.format(json.loads(decrypted)["cnCloud"]["get_info"]["username"],json.loads(decrypted)["cnCloud"]["get_info"]["server"],json.loads(decrypted)["cnCloud"]["get_info"]["binded"]))
    text_box.configure(state='disabled',exportselection=0)

def clear():
    text_box.configure(state='normal',exportselection=0)
    text_box.delete('1.0', END)
    text_box.insert('end','''    >> Tplink smart plug controller terminal <<''')
    text_box.insert("end","""

Started at : {}
Config File : {}
Ip : {}
    """.format(datetime.datetime.now(),configfile,ip))
    text_box.configure(state='disabled',exportselection=0)

def apply_ip():
    global ip
    try:
        socket.gethostbyname(apply_ip_box.get("1.0","end-1c"))
    except socket.error:
        pymsgbox.alert("Ip not valid", '!')
        pass
    else:
        w = open(configfile, "w")
        w.write(apply_ip_box.get("1.0","end-1c"))
        print("Ip {} written to {}".format(apply_ip_box.get("1.0","end-1c"),configfile))
        w.close()
        w = open(configfile)
        ip = w.read()
        w.close()

w = open(configfile)
ip = w.read()
w.close()

window.geometry('800x500')
window.resizable('0', '0')
window.title("Tplink Smart Plug Controller")
icon = PhotoImage(file=resource_path("images\\icon.png"))
window.iconphoto(False, icon)
window.configure(background='#2c394b')

box1_img = PhotoImage(file=resource_path("images\\logo.png"))
box1 = Canvas(window, width = 354, height = 40, highlightthickness=0, bd=0)
box1.create_image(0, 0, anchor=NW, image=box1_img) 
box1.place(x=-5,y=0)

text_box = Text(window,height=31,width=57,background='#0c0c0c',bd=0,fg='#ffffff')
text_box.place(x=347,y=1)
text_box.insert('end','''    >> Tplink smart plug controller terminal <<''')
text_box.insert("end","""

Started at : {}
Config File : {}
Ip : {}
""".format(datetime.datetime.now(),configfile,ip))
text_box.configure(state='disabled',exportselection=0)

on_img=PhotoImage(file=resource_path("images\\button_on.png"))
on_button = Button(window, highlightthickness=0, bd=0, text='', image=on_img, command=lambda: turn_on())
on_button.pack(ipadx=5, ipady=5, expand=True)
on_button.place(x=75, y=50)

off_img=PhotoImage(file=resource_path("images\\button_off.png"))
off_button = Button(window, highlightthickness=0, bd=0, text='', image=off_img, command=lambda: turn_off())
off_button.pack(ipadx=5, ipady=5, expand=True)
off_button.place(x=175, y=50)

cloud_img=PhotoImage(file=resource_path("images\\button_cloud-info.png"))
cloud_button = Button(window, highlightthickness=0, bd=0, text='', image=cloud_img, command=lambda: cloud_info())
cloud_button.pack(ipadx=5, ipady=5, expand=True)
cloud_button.place(x=80, y=120)

info_img=PhotoImage(file=resource_path("images\\button_plug-info.png"))
info_button = Button(window, highlightthickness=0, bd=0, text='', image=info_img, command=lambda: info())
info_button.pack(ipadx=5, ipady=5, expand=True)
info_button.place(x=91, y=190)

apply_ip_img=PhotoImage(file=resource_path("images\\button_apply-ip.png"))
apply_ip_button = Button(window, highlightthickness=0, bd=0, text='', image=apply_ip_img, command=lambda: apply_ip())
apply_ip_button.pack(ipadx=5, ipady=5, expand=True)
apply_ip_button.place(x=15, y=450)

clear_img=PhotoImage(file=resource_path("images\\button_clear-terminal.png"))
clear_button = Button(window, highlightthickness=0, bd=0, text='', image=clear_img, command=lambda: clear())
clear_button.pack(ipadx=5, ipady=5, expand=True)
clear_button.place(x=50, y=260)

apply_ip_box = Text(window,height=1,width=17,background='#0c0c0c',bd=0,fg='#ffffff')
apply_ip_box.place(x=150,y=460)
r = open(configfile)
apply_ip_box.insert("end",'{}'.format(r.read()))
r.close()

window.mainloop()