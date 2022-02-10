#!/usr/bin/python3
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <phk@FreeBSD.ORG> wrote this file.  As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return.   Poul-Henning Kamp
# ----------------------------------------------------------------------------
#
# Modified for Domotics at first and single request.
#
# Modified by Ronald van der Meer, Frank Reijn and Paul Bonnemaijers for the
# Kamstrup Multical 402
# Later modified by Hans van Schoot for easier usage
#
# Cleaned up and modified by RobinS-S for Home Assistant and use without MQTT/Domoticz/HA

from __future__ import print_function

# You need pySerial
import serial
import math
import sys
import datetime
import json
import codecs
import json
import paho.mqtt.client as mqtt

# Variables
reader = codecs.getreader("utf-8")

kamstrup_402_var = {                # Decimal Number in Command
    0x003C: "Heat Energy (E1)",  # 60
    0x0050: "Power",  # 80
    0x0056: "Temp1",  # 86
    0x0057: "Temp2",  # 87
    0x0059: "Tempdiff",  # 89
    0x004A: "Flow",  # 74
    0x0044: "Volume",  # 68
    0x008D: "MinFlow_M",  # 141
    0x008B: "MaxFlow_M",  # 139
    0x008C: "MinFlowDate_M",  # 140
    0x008A: "MaxFlowDate_M",  # 138
    0x0091: "MinPower_M",  # 145
    0x008F: "MaxPower_M",  # 143
    0x0095: "AvgTemp1_M",  # 149
    0x0096: "AvgTemp2_M",  # 150
    0x0090: "MinPowerDate_M",  # 144
    0x008E: "MaxPowerDate_M",  # 142
    0x007E: "MinFlow_Y",  # 126
    0x007C: "MaxFlow_Y",  # 124
    0x007D: "MinFlowDate_Y",  # 125
    0x007B: "MaxFlowDate_Y",  # 123
    0x0082: "MinPower_Y",  # 130
    0x0080: "MaxPower_Y",  # 128
    0x0092: "AvgTemp1_Y",  # 146
    0x0093: "AvgTemp2_Y",  # 147
    0x0081: "MinPowerDate_Y",  # 129
    0x007F: "MaxPowerDate_Y",  # 127
    0x0061: "Temp1xm3",  # 97
    0x006E: "Temp2xm3",  # 110
    0x0071: "Infoevent",  # 113
    0x03EC: "HourCounter",  # 1004
}

multical_var_si = {                # Decimal Number in Command for Kamstrup Multical
    # source data already in Joule - "Heat Energy (E1)",         #60
    0x003C: 1E+0,
    0x0050: 1E-3,       # source data in milliWatt - "Power",                   #80
    0x0056: 1E-9,       # source data in nanoCelcius - "Temp1",                   #86
    0x0057: 1E-9,       # source data in nanoCelcius - "Temp2",                   #87
    0x0059: 1E-9,       # source data in nanoCelcius - "Tempdiff",                #89
    0x004A: 1E-12/3600,  # source data nanoliter/hour - "Flow",                    #74
    0x0044: 1E+0,       # source data TBD - "Volume",                  #68
    0x008D: 1E+0,       # source data TBD - "MinFlow_M",               #141
    0x008B: 1E+0,       # source data TBD - "MaxFlow_M",               #139
    0x008C: 1E+0,       # source data TBD - "MinFlowDate_M",           #140
    0x008A: 1E+0,       # source data TBD - "MaxFlowDate_M",           #138
    0x0091: 1E+0,       # source data TBD - "MinPower_M",              #145
    0x008F: 1E+0,       # source data TBD - "MaxPower_M",              #143
    0x0095: 1E+0,       # source data TBD - "AvgTemp1_M",              #149
    0x0096: 1E+0,       # source data TBD - "AvgTemp2_M",              #150
    0x0090: 1E+0,       # source data TBD - "MinPowerDate_M",          #144
    0x008E: 1E+0,       # source data TBD - "MaxPowerDate_M",          #142
    0x007E: 1E+0,       # source data TBD - "MinFlow_Y",               #126
    0x007C: 1E+0,       # source data TBD - "MaxFlow_Y",               #124
    0x007D: 1E+0,       # source data TBD - "MinFlowDate_Y",           #125
    0x007B: 1E+0,       # source data TBD - "MaxFlowDate_Y",           #123
    0x0082: 1E+0,       # source data TBD - "MinPower_Y",              #130
    0x0080: 1E+0,       # source data TBD - "MaxPower_Y",              #128
    0x0092: 1E+0,       # source data TBD - "AvgTemp1_Y",              #146
    0x0093: 1E+0,       # source data TBD - "AvgTemp2_Y",              #147
    0x0081: 1E+0,       # source data TBD - "MinPowerDate_Y",          #129
    0x007F: 1E+0,       # source data TBD - "MaxPowerDate_Y",          #127
    0x0061: 1E+0,       # source data TBD - "Temp1xm3",                #97
    0x006E: 1E+0,       # source data TBD - "Temp2xm3",                #110
    0x0071: 1E+0,       # source data TBD - "Infoevent",               #113
    0x03EC: 1E+0,       # source data TBD - "HourCounter",             #1004
}

#######################################################################
# Units, provided by Erik Jensen

units = {
    0: '', 1: 'Wh', 2: 'kWh', 3: 'MWh', 4: 'GWh', 5: 'j', 6: 'kj', 7: 'Mj',
    8: 'Gj', 9: 'Cal', 10: 'kCal', 11: 'Mcal', 12: 'Gcal', 13: 'varh',
    14: 'kvarh', 15: 'Mvarh', 16: 'Gvarh', 17: 'VAh', 18: 'kVAh',
    19: 'MVAh', 20: 'GVAh', 21: 'kW', 22: 'kW', 23: 'MW', 24: 'GW',
    25: 'kvar', 26: 'kvar', 27: 'Mvar', 28: 'Gvar', 29: 'VA', 30: 'kVA',
    31: 'MVA', 32: 'GVA', 33: 'V', 34: 'A', 35: 'kV', 36: 'kA', 37: 'C',
    38: 'K', 39: 'l', 40: 'm3', 41: 'l/h', 42: 'm3/h', 43: 'm3xC',
    44: 'ton', 45: 'ton/h', 46: 'h', 47: 'hh:mm:ss', 48: 'yy:mm:dd',
    49: 'yyyy:mm:dd', 50: 'mm:dd', 51: '', 52: 'bar', 53: 'RTC',
    54: 'ASCII', 55: 'm3 x 10', 56: 'ton x 10', 57: 'GJ x 10',
    58: 'minutes', 59: 'Bitfield', 60: 's', 61: 'ms', 62: 'days',
    63: 'RTC-Q', 64: 'Datetime'
}

#######################################################################
# Kamstrup uses the "true" CCITT CRC-16
#


def crc_1021(message):
    poly = 0x1021
    reg = 0x0000
    for byte in message:
        mask = 0x80
        while(mask > 0):
            reg <<= 1
            if byte & mask:
                reg |= 1
            mask >>= 1
            if reg & 0x10000:
                reg &= 0xffff
                reg ^= poly
    return reg


#######################################################################
# Byte values which must be escaped before transmission
#
escapes = {
    0x06: True,
    0x0d: True,
    0x1b: True,
    0x40: True,
    0x80: True,
}

#######################################################################
# And here we go....
#


class kamstrup(object):
    def __init__(self, serial_port):
        self.debug_fd = open("/tmp/_kamstrup", "a")
        self.debug_fd.write("\n\nStart\n")
        self.debug_id = None

        self.ser = serial.Serial(
            port=serial_port,
            baudrate=1200,
            timeout=5.0,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_TWO)
#            xonxoff = 0,
#            rtscts = 0)
#           timeout = 20

    def debug(self, dir, b):
        for i in b:
            if dir != self.debug_id:
                if self.debug_id != None:
                    self.debug_fd.write("\n")
                self.debug_fd.write(dir + "\t")
                self.debug_id = dir
            self.debug_fd.write(" %02x " % i)
        self.debug_fd.flush()

    def debug_msg(self, msg):
        if self.debug_id != None:
            self.debug_fd.write("\n")
        self.debug_id = "Msg"
        self.debug_fd.write("Msg\t" + msg)
        self.debug_fd.flush()

    def wr(self, b):
        b = bytearray(b)
        self.debug("Wr", b)
        self.ser.write(b)

    def rd(self):
        a = self.ser.read(1)
        if len(a) == 0:
            self.debug_msg("Rx Timeout")
            return None
        b = bytearray(a)[0]
        self.debug("Rd", bytearray((b,)))
        return b

    def send(self, pfx, msg):
        b = bytearray(msg)

        b.append(0)
        b.append(0)
        c = crc_1021(b)
        b[-2] = c >> 8
        b[-1] = c & 0xff

        c = bytearray()
        c.append(pfx)
        for i in b:
            if i in escapes:
                c.append(0x1b)
                c.append(i ^ 0xff)
            else:
                c.append(i)
        c.append(0x0d)
        self.wr(c)

    def recv(self):
        b = bytearray()
        while True:
            d = self.rd()
            if d == None:
                return None
            if d == 0x40:
                b = bytearray()
            b.append(d)
            if d == 0x0d:
                break
        c = bytearray()
        i = 1
        while i < len(b) - 1:
            if b[i] == 0x1b:
                v = b[i + 1] ^ 0xff
                if v not in escapes:
                    self.debug_msg(
                        "Missing Escape %02x" % v)
                c.append(v)
                i += 2
            else:
                c.append(b[i])
                i += 1
        if crc_1021(c):
            self.debug_msg("CRC error")
        return c[:-2]

    def readvar(self, nbr):
        # I wouldn't be surprised if you can ask for more than
        # one variable at the time, given that the length is
        # encoded in the response.  Havn't tried.

        self.send(0x80, (0x3f, 0x10, 0x01, nbr >> 8, nbr & 0xff))

        b = self.recv()
        if b == None:
            return (None, None)
        if b[0] != 0x3f or b[1] != 0x10:
            return (None, None)

        if b[2] != nbr >> 8 or b[3] != nbr & 0xff:
            return (None, None)

        if b[4] in units:
            u = units[b[4]]
        else:
            u = None

        # Decode the mantissa
        x = 0
        for i in range(0, b[5]):
            x <<= 8
            x |= b[i + 7]

        # Decode the exponent
        i = b[6] & 0x3f
        if b[6] & 0x40:
            i = -i
        i = math.pow(10, i)
        if b[6] & 0x80:
            i = -i
        x *= i

        if False:
            # Debug print
            s = ""
            for i in b[:4]:
                s += " %02x" % i
            s += " |"
            for i in b[4:7]:
                s += " %02x" % i
            s += " |"
            for i in b[7:]:
                s += " %02x" % i

            print(s, "=", x, units[b[4]])

        return (x, u)


if __name__ == "__main__":

    import time
    import argparse
    import os
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""Values are expected in the format:
   "CommandNr"
"""
                                     )
    parser.add_argument("-d", "--device", type=str,
                        help="Device to use. Example: /dev/ttyUSB0", required=True)
    # MQTT
    parser.add_argument(
        "--mqtt_ip", type=str, help="MQTT ip address.")
    parser.add_argument(
        "--mqtt_user", type=str, help="MQTT username. Defaults empty.", default="")
    parser.add_argument(
        "--mqtt_pass", type=str, help="MQTT password. Defaults empty.", default="")
    parser.add_argument(
        "--mqtt_topic", type=str, help="MQTT topic. Defaults to multical.", default="multical")
    parser.add_argument("--mqtt_port", type=int,
                        help="MQTT port. Defaults to 1883", default=1883)
    parser.add_argument(
        "--test_mqtt", help="Test the IR-MQTT interface", action="store_true")
    parser.add_argument(
        "--add_sensors_to_ha", help="Add E1 sensors to MQTT for discovery by Home Assistant, ALWAYS do this the first time you use this script", action="store_true")
    parser.add_argument(
        "--test_kamstrup", help="Test the IR interface of the Kamstrup and exit", action="store_true")
    parser.add_argument(
        "--mqtt", help="Test the MQTT connection and exit ", action="store_true")
    parser.add_argument(
        "values", type=str, help="CommandNr", nargs='*')

    args = parser.parse_args()

    # some sanity checks
    if not os.path.exists(args.device):
        print("Error! Failed to locate specified device: %s, example: /dev/ttyUSB0" %
              (args.device))
        sys.exit(1)
    for value in args.values:
        if not value.isnumeric():
            print(
                "Error! Your values are not in numeric format. Example: 60 80. Find these in the script.")
            sys.exit(1)
    if not (args.test_kamstrup or args.test_mqtt or args.add_sensors_to_ha) and len(args.values) == 0:
        print("This script needs values to do something! Check --help to see how it works!")
        sys.exit()

    print("=======================================================================================")
    if args.add_sensors_to_ha:
        mqttclient = mqtt.Client(client_id="multical")
        mqttclient.username_pw_set(args.mqtt_user, args.mqtt_pass)

        try:
            mqttclient.connect(args.mqtt_ip, int(args.mqtt_port))
        except:
            print('Error! Could not connect to MQTT broker')
        try:
            mqttclient.publish('homeassistant/sensor/E1HeatEnergy/config',
                               json.dumps({
                                   "state_topic": args.mqtt_topic + "/HeatEnergy(E1)",
                                   "name": "Heat Energy (E1)",
                                   "icon": "mdi:water-boiler",
                                   "unique_id": "pi_e1_heat",
                                   "value_template": "{{ value_json.value | round(5) }}",
                                   "unit_of_measurement": "Gj",
                                   "state_class": "total",
                                   "schema": "json"
                               })
                               )
            mqttclient.publish('homeassistant/sensor/E1Power/config',
                               json.dumps({
                                   "state_topic": args.mqtt_topic + "/Power",
                                   "name": "Power (E1)",
                                   "device_class": "energy",
                                   "unique_id": "pi_e1_power",
                                   "value_template": "{{ value_json.value | round(5) }}",
                                   "unit_of_measurement": "kW",
                                   "state_class": "measurement",
                                   "schema": "json"
                               })
                               )
            mqttclient.publish('homeassistant/sensor/E1Temp1/config',
                               json.dumps({
                                   "state_topic": args.mqtt_topic + "/Temp1",
                                   "name": "Temp 1 (E1)",
                                   "device_class": "temperature",
                                   "unique_id": "pi_e1_temp1",
                                   "value_template": "{{ value_json.value | round(3) }}",
                                   "unit_of_measurement": "C",
                                   "state_class": "measurement",
                                   "schema": "json"
                               })
                               )
            mqttclient.publish('homeassistant/sensor/E1Temp2/config',
                               json.dumps({
                                   "state_topic": args.mqtt_topic + "/Temp2",
                                   "name": "Temp 2 (E1)",
                                   "device_class": "temperature",
                                   "unique_id": "pi_e1_temp2",
                                   "value_template": "{{ value_json.value | round(3) }}",
                                   "unit_of_measurement": "C",
                                   "state_class": "measurement",
                                   "schema": "json"
                               })
                               )
            mqttclient.publish('homeassistant/sensor/E1Flow/config',
                               json.dumps({
                                   "state_topic": args.mqtt_topic + "/Flow",
                                   "name": "Flow (E1)",
                                   "icon": "mdi:waves-arrow-right",
                                   "unique_id": "pi_e1_flow",
                                   "value_template": "{{ value_json.value | round(2) }}",
                                   "unit_of_measurement": "l/h",
                                   "state_class": "measurement",
                                   "schema": "json"
                               })
                               )
            mqttclient.publish('homeassistant/sensor/E1Volume/config',
                               json.dumps({
                                   "state_topic": args.mqtt_topic + "/Volume",
                                   "name": "Volume (E1)",
                                   "icon": "mdi:radiator",
                                   "unique_id": "pi_e1_volume",
                                   "value_template": "{{ value_json.value | round(5) }}",
                                   "unit_of_measurement": "m3",
                                   "state_class": "total",
                                   "schema": "json"
                               })
                               )
            print(
                "Added sensors to Home Assistant MQTT topics! Autodetection should occur.")
        except:
            print(
                'Error! Could not publish device configuration to homeassistant/sensor, check ACL!')

    else:
        device = kamstrup(args.device)
        heat_timestamp = datetime.datetime.strftime(
            datetime.datetime.today(), "%Y-%m-%d %H:%M:%S")

        print("Kamstrup Multical 402/403 serial optical data received: %s" %
              heat_timestamp)
        print("Meter vendor/type: Kamstrup M402/403")

        if args.test_mqtt:
            mqttclient = mqtt.Client(client_id="multical")
            mqttclient.username_pw_set(args.mqtt_user, args.mqtt_pass)

            try:
                mqttclient.connect(args.mqtt_ip, int(args.mqtt_port))
            except:
                print('Error! Could not connect to MQTT broker')
            for i in kamstrup_402_var:
                x, u = device.readvar(i)
                print("CommandNr %4i: %-25s" % (i, kamstrup_402_var[i]), x, u)
                try:
                    mqttclient.publish(
                        args.mqtt_topic + '/' + kamstrup_402_var[i].replace(" ", ""), json.dumps({"value": x, "unit": u}))
                except:
                    print('Error! Could not publish MQTTT value')
            sys.exit()

        if args.test_kamstrup:
            for i in kamstrup_402_var:
                x, u = device.readvar(i)
                print("CommandNr %4i: %-25s" % (i, kamstrup_402_var[i]), x, u)
            sys.exit()

if args.mqtt_ip:
    results = {}
    mqttclient = mqtt.Client(client_id="multical")
    mqttclient.username_pw_set(args.mqtt_user, args.mqtt_pass)

    try:
        mqttclient.connect(args.mqtt_ip, int(args.mqtt_port))
    except:
        print('Error! Could not connect to MQTT broker')

if args.values:
    print("---------------------------------------------------------------------------------------")
    for i in kamstrup_402_var:
        r = 0

        for y in args.values:
            dcNr = int(y, 0)

            if i == dcNr:
                x, u = device.readvar(i)

                # Convert to SI units
                xsi = x * multical_var_si[i]

                print("%-25s" % kamstrup_402_var[i], x, u)

                value = round(x, 2)

                if args.mqtt_ip:
                    try:
                        mqttclient.publish(
                            args.mqtt_topic + '/' + kamstrup_402_var[i].replace(" ", ""), json.dumps({"value": x, "unit": u}))
                    except:
                        print('Error! Could not publish MQTT value')
    if args.mqtt_ip:
        print("Sensor values published to MQTT %s/#" % args.mqtt_topic)
    print("---------------------------------------------------------------------------------------")
    print("End data received: %s" % datetime.datetime.strftime(
        datetime.datetime.today(), "%Y-%m-%d %H:%M:%S"))
print("=======================================================================================")
