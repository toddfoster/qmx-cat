#!/usr/bin/python

import serial
import argparse

# qmx-cat by W2TEF begun 1 Nov 2025

parser = argparse.ArgumentParser(
formatter_class=argparse.RawDescriptionHelpFormatter,
description="""
Send CAT commands to a serial port and receive responses. 
Includes special utilities for the QRP-Labs QMX radios.

Available commands include:

    dump:    Walk the menus and output (nearly) all the settings
            (bypassing "Band config." and "Advanced config!" menus)
""",
epilog="""
USE AT YOUR OWN RISK! Changing settings unthoughtfully can damage your radio.

This software has no connection to QRP-Labs or its principals, except that I am a grateful user of their products.

Copyright © 2025  Todd Foster, W2TEF
License: MIT/X11 License <https://opensource.org/license/MIT>
This  is free software: you are free to change and redistribute it.  
There is NO WARRANTY, to the extent permitted by law.
""")

parser.add_argument("command", help="the command to run")
parser.add_argument("-p", "--port", 
                    default="/dev/ttyACM0",
                    help="the port connected to the QMX (default=/dev/ttyACM0)") 
args = parser.parse_args()
commands = parser.add_subparsers(dest='command')

command_cat = commands.add_parser('cat', help='send a cat command')
command_cat.add_argument('cat_command')

command_dump = commands.add_parser('dump', help='display (nearly) all settings')



# NOTE: Band config is a table; not handled here
# NOTE: Advanced config! I don't want to entrust to an automated tool
MENUS_TO_AVOID = ["Band config.[16]", "System config|Advanced config!"] 

NON_VALUE_TYPES = ["0", "1", "6"]

def cat(qmx, command):
    qmx.write(command.encode("utf-8"))
    return qmx.read_until(b';').decode('utf-8').strip()

def strip_menu_response(t):
    # TODO: Verify correct response: MM.*;
    return t[2:-1]

def menu_get(qmx, path):
    return strip_menu_response(cat(qmx, f"MM{path};"))

def menu_list(qmx, listRef):
    return strip_menu_response(cat(qmx, f"ML{listRef};"))

def menu_query(qmx, path):
    response = cat(qmx, f"MM{path}?;")
    if response == "?;":
        return None
    response = strip_menu_response(response)
    response = response.split("|")
    typeid=response[0]
    listid=response[1]
    descriptor = response[2]
    value = None
    if typeid not in NON_VALUE_TYPES:
        value = menu_get(qmx, path)
    return {"path":path, 
            "typeid":typeid, 
            "listid":listid, 
            "descriptor":descriptor, 
            "value":value}

def menu_path_to_alpha(qmx, path):
    result = []
    path_steps = path.split("|")
    for i in range(len(path_steps)):
        this_path = "|".join(path_steps[0:i+1])
        result.append(menu_query(qmx, this_path)["descriptor"])
    return "|".join(result)

def menu_report(qmx, path):
    return f"{menu_path_to_alpha(qmx,path)}={menu_get(qmx,path)}"

def discover(qmx, root):
    result=[]
    if len(root) > 0 and root[-1] != "|":
        root = root + "|"
    for i in range(100):
        response = menu_query(qmx, f"{root}{i}")
        if response == None:
            break
        result.append(response)
    return result


def recurse_menu(qmx, menu):
    # Recurse using numeric indices to avoid tripping over
    # me_nu entries who being with numerals
    print(f"##############")
    if menu == "":
        print(f"# MENU (root)")
    else:
        print(f"# MENU {menu['path']} : {menu['descriptor']}")
    submenus = []
    for i in discover(qmx, menu["path"]):
        descriptor=i["descriptor"]
        typeid=i["typeid"]
        if typeid in NON_VALUE_TYPES:
            print(f"# ({descriptor})")
        else:
            print(menu_report(qmx, i["path"]))
            # print(f"{descriptor}={i["value"]}")
        if typeid == "0":
            submenus.append(i)
    for s in submenus:
        if menu_path_to_alpha(qmx, s["path"]) not in MENUS_TO_AVOID:
            recurse_menu(qmx, s)


def recurse(qmx, path):
    descriptor = ""
    if path != "":
        descriptor = menu_query(qmx, path)["descriptor"]
    recurse_menu(qmx, {"path":path, "descriptor":descriptor})


qmx = serial.Serial(args.port)  # open serial port
# print(discover(qmx, ""))
# print()
# print(discover(qmx, "CW"))
# print(menu_query(qmx,"CW"))
# print(menu_get(qmx,"CW")) # blank result; no value
# print(menu_query(qmx,"CW|CW offset"))
# print(menu_get(qmx,"CW|CW offset"))
# print(menu_report(qmx,"CW|CW offset"))
# print(menu_list(qmx,"3"))
# print()
# print(menu_query(qmx,"CW|Choose filters"))
# # NOTE: Menus with numeric titles can't be accessed by title
# # NOTE: e.g, print(menu_query(qmx,"CW|Choose filters|50"))
# print(menu_query(qmx,"CW|Choose filters|0"))
# print(menu_report(qmx,"CW|Choose filters|0"))
# print()
# print(menu_query(qmx,"VFO"))
#print(menu_query(qmx,"VFO|VFO tune rates"))
# print(menu_query(qmx,"VFO|VFO tune rates|0"))
# print(menu_path_to_alpha(qmx, "0"))
# print(menu_path_to_alpha(qmx, "1|0"))
# print(menu_path_to_alpha(qmx, "1|0|1"))
# print()
# recurse(qmx, "CW")
# print()
# recurse(qmx, "")
# print(discover(qmx, "11"))
# recurse(qmx, "")

if args.command == "dump":
    recurse(qmx, "")
elif args.command == "cat":
    print(cat(qmx, args.cat_command))


qmx.close()
