#!/usr/bin/python

import serial
import argparse

# qmx-cat by W2TEF begun 1 Nov 2025

# TODO: ¿Tidy up output of discover, mm?
# TODO: Implement batch setter
# TODO: Note that setting a string to an empty string doesn't change it

parser = argparse.ArgumentParser(
formatter_class = argparse.RawDescriptionHelpFormatter,
description = """
Send CAT commands to a serial port and receive responses. 
Includes special utilities for the QRP-Labs QMX radios.
""",
epilog = """
Notes: 
- The "dump" command will bypass the "Band config." and "Advanced config!" menus.
 
USE AT YOUR OWN RISK! Changing settings unthoughtfully can damage your radio.
 
This software has no connection to QRP-Labs or its principals, except that I am a grateful user of their products. 
Refer to the "CAT Programming Manual" to understand what's going on here.
 
Copyright © 2025  Todd Foster, W2TEF  
License: MIT/X11 License <https://opensource.org/license/MIT>  
This  is free software: you are free to change and redistribute it.  
There is NO WARRANTY, to the extent permitted by law.
""")

parser.add_argument("-p", "--port", 
                    default="/dev/ttyACM0",
                    help="the port connected to the QMX (default=/dev/ttyACM0)") 
command_parser = parser.add_subparsers(dest='command')

dump_p = command_parser.add_parser('dump', help='[PATH]: display (nearly) all settings')
dump_p.add_argument('path', default="", nargs='?')

cat_p = command_parser.add_parser('cat', help='CMD [-n --no_wait for response]: send a cat command (semi-colon optional)')
cat_p.add_argument('cat_command')
cat_p.add_argument('-n', "--no_wait",
                   action='store_true',
                   help="don't wait for a response")

mm_p = command_parser.add_parser('mm', help='PATH: get a menu value')
mm_p.add_argument('path')

mmset_p = command_parser.add_parser('mm_set', help='PATH VALUE: set a menu value')
mmset_p.add_argument('path')
mmset_p.add_argument('value')

report_p = command_parser.add_parser('report', help='PATH: report a path and value')
report_p.add_argument('path')

mmq_p = command_parser.add_parser('mm?', help='PATH: query a menu entry')
mmq_p.add_argument('path')

ml_p = command_parser.add_parser('ml', help='PATH: show a menu list')
ml_p.add_argument('list_number')

discover_p = command_parser.add_parser('discover', 
                                       help='[PATH]: discover a menu')
discover_p.add_argument('path', default="", nargs='?')


args = parser.parse_args()



# NOTE: Band config is a table; not handled here
# NOTE: Advanced config! I don't want to entrust to an automated tool
MENUS_TO_AVOID = ["Band config.[16]", "System config|Advanced config!"] 

NON_VALUE_TYPES = ["0", "1", "6"]

def cat(qmx, command):
    qmx.write(command.encode("utf-8"))

def cat_with_response(qmx, command):
    cat(qmx, command)
    return qmx.read_until(b';').decode('utf-8').strip()

def strip_menu_response(t):
    # TODO: Verify correct response: MM.*;
    return t[2:-1]

def menu_get(qmx, path):
    return strip_menu_response(cat_with_response(qmx, f"MM{path};"))

def menu_set(qmx, path, value):
    return cat(qmx, f"MM{path}={value};")

def menu_list(qmx, listRef):
    return strip_menu_response(cat_with_response(qmx, f"ML{listRef};"))

def menu_query(qmx, path):
    response = cat_with_response(qmx, f"MM{path}?;")
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

if args.command == "dump":
    recurse(qmx, args.path)
elif args.command == "cat":
    command = args.cat_command
    # Sugar: my shell interprets the semicolon instead of passing it
    if command[-1] != ';':
        command = command + ";"
    if args.no_wait:
        cat(qmx, command)
    else:
        print(cat_with_response(qmx, command))
elif args.command == "mm":
    print(menu_get(qmx, args.path))
elif args.command == "mm_set":
    menu_set(qmx, args.path, args.value)
elif args.command == "report":
    print(menu_report(qmx, args.path))
elif args.command == "mm?":
    print(menu_query(qmx, args.path))
elif args.command == "ml":
    print(menu_list(qmx, args.list_number))
elif args.command == "discover":
    for i in discover(qmx, args.path):
        print(i)

qmx.close()
