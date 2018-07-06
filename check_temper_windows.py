#!/usr/bin/env python3

import sys, usb
import argparse
import logging
VENDOR_ID = 0x0c45
PRODUCT_ID = 0x7401

TIMEOUT = 5000
OFFSET = 0

INTERFACE = 1
REQ_INT_LEN = 8
ENDPOINT = 0x82

COMMANDS = {
    'temp': b'\x01\x80\x33\x01\x00\x00\x00\x00',
    'ini1': b'\x01\x82\x77\x01\x00\x00\x00\x00',
    'ini2': b'\x01\x86\xff\x01\x00\x00\x00\x00',
}

class TemperDevice(object):
	def __init__(self, device):
		self._device = device
		
	def get_temperature(self):
		if self._device is None:
			return "Device not ready"
		else:
			try:
				self._device.set_configuration()
				ret = self._device.ctrl_transfer(bmRequestType=0x21, bRequest=0x09, wValue=0x0201, wIndex=0x00, data_or_wLength=b'\x01\x01', timeout=TIMEOUT)
				
				self._control_transfer(COMMANDS['temp'])
				self._interrupt_read()
				self._control_transfer(COMMANDS['ini1'])
				self._interrupt_read()
				self._control_transfer(COMMANDS['ini2'])
				self._interrupt_read()
				self._interrupt_read()
				self._control_transfer(COMMANDS['temp'])
				data = self._interrupt_read()
				self._device.reset()

				temp = (data[3] & 0xFF) + (data[2] << 8)
				temp_c = temp * (125.0 / 32000.0)
				temp_c = temp_c + OFFSET
				
				return temp_c
			except usb.USBError as err:
				if "not permitted" in str(err):
					return "Permission problem accessing USB."
				else:
					return err
			except:
				return "Unexpected error:", sys.exc_info()[0]
				raise
			
	def _control_transfer(self, data):
		ret = self._device.ctrl_transfer(bmRequestType=0x21, bRequest=0x09, wValue=0x0200, wIndex=0x01, data_or_wLength=data, timeout=TIMEOUT)
		
	def _interrupt_read(self):
		data = self._device.read(ENDPOINT, REQ_INT_LEN, interface=INTERFACE, timeout=TIMEOUT)
		return data

# PARSING ARGS
parser = argparse.ArgumentParser(description='This script get the temperature of a Temper2 USB dongle for being used with Nagios and perfdata')
parser.add_argument('-w', '--warning-threshold', required=True, type=float, help='The value above which an warning state is raised (exit code = 1)')
parser.add_argument('-c', '--critical-threshold', required=True, type=float, help='The value above which an critical state is raised (exit code = 2)')
parser.add_argument('-v', '--verbose', '--debug', action='store_true')
parser.add_argument('-p', '--perf-data', action='store_true', help='Adds performance data to be used for graphs (nagiosgraph for example)')
parser.add_argument('--vendor-id', help='Use this if the vendor id is not the default one (0x0c45)')
parser.add_argument('--product-id', help='Use this if the product id is not the default one (0x7401)')
parser.add_argument('--interface', help='Use this if the interface is not the default one (1)')
args = parser.parse_args()

if args.vendor_id:
	VENDOR_ID = int(args.vendor_id, 0)
if args.product_id:
	PRODUCT_ID = int(args.product_id, 0)
if args.vendor_id:
	INTERFACE = int(args.interface, 0)

# DEFINE LOGGER
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)
consoleHandler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

if args.verbose:
    logger.setLevel(logging.DEBUG)

logger.debug('Warning value is {}'.format(args.warning_threshold))
logger.debug('Critical value is {}'.format(args.critical_threshold))
logger.debug('Vendor ID is {}'.format(VENDOR_ID))
logger.debug('Product ID is {}'.format(PRODUCT_ID))
logger.debug('Interface is {}'.format(INTERFACE))



dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
TDev = TemperDevice(dev)
value = float(TDev.get_temperature())

exit_code = 0

if value >= args.critical_threshold:
	exit_code = 2
	msg = '{} is over {} ! Critical !'.format(value, args.critical_threshold)
elif value >= args.warning_threshold:
	exit_code = 1
	msg = '{} is over {} ! Warning !'.format(value, args.warning_threshold)
else:
	msg = 'Current temp is {}. Ok'.format(value)

if args.perf_data:
	print('{}|temperature={};{};{}'.format(msg,value,args.warning_threshold,args.critical_threshold))
else:
	print(msg)
exit(exit_code)
