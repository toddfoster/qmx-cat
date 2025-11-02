import serial

# qmx-cat by W2TEF begun 1 Nov 2025

# TODO: Provide a decent CLI, including specifying port
# DEBUG: Not reading all band settings
# TODO: report out name of path without numbers


PORT="/dev/ttyACM0"

NON_VALUE_TYPES = ["0", "1", "6"]

discovery_cache = {}

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
    return {"path":path, "typeid":typeid, 
            "listid":listid, "descriptor":descriptor, 
            "value":value}

def menu_report(qmx, path):
    return f"{path}={menu_get(qmx,path)}"

def discover(ser, root):
    result=[]
    if len(root) > 0 and root[-1] != "|":
        root = root + "|"
    for i in range(100):
        response = menu_query(ser, f"{root}{i}")
        if response == None:
            break
        result.append(response)
    return result


def recurse_menu(ser, menu):
    # Recurse using numeric indices to avoid tripping over
    # me_nu entries who being with numerals
    print(f"##############")
    if menu == "":
        print(f"# MENU (root)")
    else:
        print(f"# MENU {menu['path']} : {menu['descriptor']}")
    submenus = []
    for i in discover(ser, menu["path"]):
        descriptor=i["descriptor"]
        typeid=i["typeid"]
        if typeid in NON_VALUE_TYPES:
            print(f"# ({descriptor})")
        else:
            print(f"{descriptor}={i["value"]}")
        if typeid == "0":
            submenus.append(i)
    for s in submenus:
        recurse_menu(ser, s)


def recurse(qmx, path):
    descriptor = ""
    if path != "":
        descriptor = menu_query(qmx, path)["descriptor"]
    recurse_menu(qmx, {"path":path, "descriptor":descriptor})


ser = serial.Serial(PORT)  # open serial port
# print(discover(ser, ""))
# print()
# print(discover(ser, "CW"))
# print(menu_query(ser,"CW"))
# print(menu_get(ser,"CW")) # blank result; no value
# print(menu_query(ser,"CW|CW offset"))
# print(menu_get(ser,"CW|CW offset"))
# print(menu_report(ser,"CW|CW offset"))
# print(menu_list(ser,"3"))
# print()
# print(menu_query(ser,"CW|Choose filters"))
# # NOTE: Menus with numeric titles can't be accessed by title
# # NOTE: e.g, print(menu_query(ser,"CW|Choose filters|50"))
# print(menu_query(ser,"CW|Choose filters|0"))
# print(menu_report(ser,"CW|Choose filters|0"))
# print()
# print(menu_query(ser,"VFO"))
# print(menu_query(ser,"VFO|VFO tune rates"))
# print(menu_query(ser,"VFO|VFO tune rates|0"))
# print()
# recurse(ser, "CW")
# print()
recurse(ser, "")
ser.close()
