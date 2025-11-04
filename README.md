# qmx-cat
Send arbitrary commands to QRP-Labs QMX radio

This is a crude tool with almost no guard-rails. Use with caution, and at your own risk. 

## Getting Started: 
qmx-cat -h: Get help
```
usage: qmx-cat [-h] [-p PORT] {get,set,show,load,type,mm?,ml,cat} ...

Send CAT commands to a serial port and receive responses. 
Includes special utilities for the QRP-Labs QMX radios.

positional arguments:
  {get,set,show,load,type,mm?,ml,cat}
    get                 PATH: get a menu value
    set                 PATH VALUE: set a menu value
    show                [PATH] [--recursive]: display (nearly) all settings
    load                FILE or - for STDIN: set multiple menu values (input
                        format same as 'show' format)
    type                PATH: get the type of a menu item
    mm?                 PATH: query a menu entry
    ml                  PATH: show a menu list
    cat                 CMD [-n --no_wait for response]: send a cat command
                        (semi-colon optional)

options:
  -h, --help            show this help message and exit
  -p, --port PORT       the port connected to the QMX (default=/dev/ttyACM0)

Notes: 
- The "show" command will bypass the "Band config." and "Advanced config!" menus.
 
USE AT YOUR OWN RISK! Changing settings unthoughtfully can damage your radio.
 
This software has no connection to QRP-Labs or its principals, except that I am a grateful user of their products. 
Refer to the "CAT Programming Manual" to understand what's going on here.
 
Copyright © 2025  Todd Foster, W2TEF  
License: MIT/X11 License <https://opensource.org/license/MIT>  
This  is free software: you are free to change and redistribute it.  
There is NO WARRANTY, to the extent permitted by law.
```

qmx-cat /command/ -h: Get help with a specific command



## Examples:

To generate a report of nearly all the settings in a qmx:
```
qmx-cat show -r
```

To generate a report of your messages:
```
qmx-cat show Messages
```

To upload a new set of messages:
```
qmx-cat load messages.txt
```

## Examples on Windows

With thanks to Stan Dye:


> I just confirmed this works in Windows with python 3.11 installed.  Note the special notation required for com port numbers 10 and above.  Low com port numbers can be specified just as "COM6", etc.  And you must quote the menu paths so the "|" character isn't interpreted by the shell.
``` 
D:\Stan\Downloads>py qmx-cat.py -p \\.\COM12 cat IF;
IF00003887000     +00000000001100000 ;
 
D:\Stan\Downloads>py qmx-cat.py -p \\.\COM12 show "0|1"
Audio|Volume step=1dB
 
D:\Stan\Downloads>py qmx-cat.py -p \\.\COM12 show -r SSB
```
