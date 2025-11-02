import serial

# qmx-cat by W2TEF begun 1 Nov 2025

# TODO: Provide a decent CLI, including specifying port


PORT="/dev/ttyACM0"

NON_VALUE_TYPES = ["0", "1", "6", "7"]
# TODO: Learn how to handle mask type values

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
    path = path.split("|")
    path[-1] = response[2]
    descriptor = "|".join(str(e) for e in path)
    value = None
    if typeid not in NON_VALUE_TYPES:
        value = menu_get(qmx, path)
    return {"typeid":typeid, "listid":listid, "path":descriptor, "value":value}

def menu_report(qmx, path):
    return f"{path}={menu_get(qmx,path)}"

def discover(ser, root):
    result=[]
    if len(root) > 1 and root[-1] != "|":
        root = root + "|"
    for i in range(100):
        response = menu_query(ser, f"{root}{i}")
        if response == None:
            break
        result.append(response)
    return result

def recurse(ser, root):
    if root != "":
        print(f"##############")
        print(f"# MENU: {root}")
    submenus = []
    paths = discover(ser, root)
    for i in paths:
        path=i["path"]
        typeid=i["typeid"]
        # TODO replace magic numbers
        if typeid in NON_VALUE_TYPES:
            print(f"# ({path})")
        else:
            print(f"{path}={i["value"]}")
        if typeid == "0":
            submenus.append(path)
    for s in submenus:
        recurse(ser, s)



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
# recurse(ser, "CW")
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
recurse(ser, "")
ser.close()
