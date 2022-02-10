# multical402-4-home-assistant
  
This script is developed for use with a Kamstrup Multical 402 (city heating) and optionally Home Assistant
  
Dependency:
 * Software: linux, python3 and python3-serial  
 * Hardware: IR Optical Probe IEC1107 IEC61107  
  
```
usage: multical402-4-homeassistant.py [-h] -d DEVICE [--mqtt_ip MQTT_IP] [--mqtt_user MQTT_USER] [--mqtt_pass MQTT_PASS] [--mqtt_topic MQTT_TOPIC] [--mqtt_port MQTT_PORT] [--test_mqtt] [--add_sensors_to_ha] [--test_kamstrup] [--mqtt] [values ...]

positional arguments:
  values                CommandNr

optional arguments:
  -h, --help            show this help message and exit
  -d DEVICE, --device DEVICE
                        Device to use. Example: /dev/ttyUSB0
  --mqtt_ip MQTT_IP     MQTT ip address.
  --mqtt_user MQTT_USER
                        MQTT username. Defaults empty.
  --mqtt_pass MQTT_PASS
                        MQTT password. Defaults empty.
  --mqtt_topic MQTT_TOPIC
                        MQTT topic. Defaults to multical.
  --mqtt_port MQTT_PORT
                        MQTT port. Defaults to 1883
  --test_mqtt           Test the IR-MQTT interface
  --add_sensors_to_ha   Add E1 sensors to MQTT for discovery by Home Assistant, ALWAYS do this the first time you use this script
  --test_kamstrup       Test the IR interface of the Kamstrup and exit

Values are expected in the format: 'CommandNr'
```

You must atleast execute this script once every 30 minutes or else the IR port on the Kamstrup will be disabled until you press a physical button on the device itself. The does not have effect on all Kamstrup meters. This can be archieved with cron: `crontab -e` and then add something like:

`*/20 *  * * * /usr/bin/python3 /path/to/your/script/multical402-4-homeassistant.py -d /dev/ttyUSB1 60 80` where 20 means 20 minutes.

Example to run: `./multical402-4-homeassistant.py -d /dev/ttyUSB0 60 80`
Output:
```
=======================================================================================
Kamstrup Multical 402/403 serial optical data received: 2022-02-10 xx:xx:xx
Meter vendor/type: Kamstrup M402/403
---------------------------------------------------------------------------------------
Heat Energy (E1)          xx.xx Gj
Power                     x.xxx kW
---------------------------------------------------------------------------------------
End data received: 2022-02-10 xx:xx:xx
=======================================================================================
```

To setup on Home Assistant, run it with the `--add_sensors_to_ha` argument first, then set up your crontab with the values you'd like to report. For example:
`*/5 * * * * /usr/bin/python3 /home/kamstrup/multical402-4-domoticz/multical402-4-homeassistant.py -d /dev/ttyUSB0 --mqtt_ip="10.0.0.1" --mqtt_port=1883 --mqtt_topic="kamstrup" --mqtt_user="kamstrup" --mqtt_pass="password" 60 80 86 87 74 68`

*Be careful reading out your meters! If they're drained, you'll be charged for the time the meter does not work as there is no way for the company to know how much energy you've used. Do not drain your meter by reading it out too fast.*
