import serial

# qmx-cat by W2TEF begun 1 Nov 2025

# TODO: Provide a decent CLI, including specifying port


PORT="/dev/ttyACM0"

NON_VALUE_TYPES = ["0", "1", "6", "7"]
# TODO: Learn how to handle mask type values

def query(qmx, command):
    qmx.write(command.encode("utf-8"))
    return qmx.read_until(b';').decode('utf-8').strip()

def strip_mm_response(t):
    # TODO: Verify correct response: MM*;
    return t[2:-1]

def query_item(qmx, item):
    response = query(qmx, f"MM{item}?;")
    if response == "?;":
        return None
    response = strip_mm_response(response)
    response = response.split("|")
    typeid=response[0]
    listid=response[1]
    path = item.split("|")
    path[-1] = response[2]
    descriptor = "|".join(str(e) for e in path)
    value = None
    if typeid not in NON_VALUE_TYPES:
        value = query_value(qmx, item)
    return {"typeid":typeid, "listid":listid, "item":descriptor, "value":value}

def query_value(qmx, item):
    return strip_mm_response(query(qmx, f"MM{item};"))

def query_list(qmx, listRef):
    return strip_mm_response(query(qmx, f"ML{listRef};"))

def show_setting(qmx, item):
    return f"{item}={query_value(qmx,item)}"

def discover(ser, root):
    result=[]
    if len(root) > 1 and root[-1] != "|":
        root = root + "|"
    for i in range(100):
        response = query_item(ser, f"{root}{i}")
        if response == None:
            break
        result.append(response)
    return result

def recurse(ser, root):
    if root != "":
        print("-------------")
        print(f"MENU: {root}")
    submenus = []
    items = discover(ser, root)
    for i in items:
        item=i["item"]
        typeid=i["typeid"]
        # TODO replace magic numbers
        if typeid in NON_VALUE_TYPES:
            print(f"({item})")
        else:
            print(f"{item}={i["value"]}")
        if typeid == "0":
            submenus.append(item)
    for s in submenus:
        recurse(ser, s)



ser = serial.Serial(PORT)  # open serial port
# print(discover(ser, ""))
# print()
# print(discover(ser, "CW"))
# print(query_item(ser,"CW"))
# print(query_value(ser,"CW")) # blank result; no value
# print(query_item(ser,"CW|CW offset"))
# print(query_value(ser,"CW|CW offset"))
# print(show_setting(ser,"CW|CW offset"))
# print(query_list(ser,"3"))
# print()
# recurse(ser, "CW")
# print(query_item(ser,"CW|Choose filters"))
# # NOTE: Menus with numeric titles can't be accessed by title
# # NOTE: e.g, print(query_item(ser,"CW|Choose filters|50"))
# print(query_item(ser,"CW|Choose filters|0"))
# print(show_setting(ser,"CW|Choose filters|0"))
# print()
# print(query_item(ser,"VFO"))
# print(query_item(ser,"VFO|VFO tune rates"))
# print(query_item(ser,"VFO|VFO tune rates|0"))
# print()
recurse(ser, "")
ser.close()
