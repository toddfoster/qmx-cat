# qmx-cat
Send arbitrary commands to QRP-Labs QMX radio

This is a crude tool with almost no guard-rails. Use with caution, and at your own risk. 

## Getting Started: 

qmx-cat -h: Get help
qmx-cat /command/ -h: Get help with a specific command

Specify port with -p PORT (defaults to /dev/ttyACM0)

## Commands:
dump: display (nearly) all settings
cat: send a raw cat command
mm: Get a menu value
mm_set: set a menu value
mm_set_many: set multiple menu values, using a file as input
report: report one or many menu values
mm?: query a menu entry
ml?: show a list of options for a defined menu list
discover: discover a menu


## Examples:

To generate a report of nearly all the settings in a qmx:
```
qmx-cat dump > mysettings.txt
```

To generate a report of your messages:
```
qmx-cat report "Messages" > messages.txt
```

To upload a new set of messages:
```
qmx-cat mm_set_many messages.txt
```

