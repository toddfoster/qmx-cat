# qmx-cat
Read and write all the user setting on a QRP-Labs QMX radio. (There is also a facility to send arbitrary CAT commands.)

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


## About using the _load_ feature:

The format of the file to be loaded is exactly that which is produced by report. Generally "path=value" with one entry per line. "#" at the beginning of a line denotes a line that should be skipped. 

Here's the important thing: a file to be loaded can be only one line long, or many. Get a list of all your messages in a text file with "qmx-cat show Messages > messages.txt". Then I suggest you remove the bottom two lines (configuring Intervals and Repeats). Maybe remove Message 11 and Message 12 if you use a custom init screen. Just change the lines you actually use, and only load those. Delete or use "#" to comment out everything else. 

As of this writing (4 November 2025) I have not tested setting any types other than strings and numerals. Test the changes you want to make carefully until you're sure they're going to do the right thing for you.

Example of my Messages file:
```
Messages|Message 1=CQ CQ CQ POTA DE W2TEF W2TEF W2TEF K
Messages|Message 2=CQ POTA DE W2TEF K
Messages|Message 3=
Messages|Message 4=CQ RG DE W2TEF K
Messages|Message 5=
Messages|Message 6=CQ CQ CQ WWFF 44 DE W2TEF W2TEF W2TEF K
Messages|Message 7=CQ WWFF DE W2TEF K
Messages|Message 8=
Messages|Message 9=CQ CQ CQ DE W2TEF W2TEF W2TEF K
Messages|Message 10=V V V TEST TEST TEST DE W2TEF W2TEF W2TEF
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
