# check_temper_windows

This script get the temperature of a Temper2 USB dongle for being used with Nagios and perfdata

It has been deployed following [this doc](https://habr.com/post/230355/).

This is a very very basic version of the [temper-python](https://github.com/padelt/temper-python) script, with some wrappers to use it with Nagios.

Usage:

```
usage: check_temper.py [-h] -w WARNING_THRESHOLD -c CRITICAL_THRESHOLD [-v]
                       [-p] [--vendor-id VENDOR_ID] [--product-id PRODUCT_ID]
                       [--interface INTERFACE]

This script get the temperature of a Temper2 USB dongle for being used with
Nagios and perfdata

optional arguments:
  -h, --help            show this help message and exit
  -w WARNING_THRESHOLD, --warning-threshold WARNING_THRESHOLD
                        The value above which an warning state is raised (exit
                        code = 1)
  -c CRITICAL_THRESHOLD, --critical-threshold CRITICAL_THRESHOLD
                        The value above which an critical state is raised
                        (exit code = 2)
  -v, --verbose, --debug
  -p, --perf-data       Adds performance data to be used for graphs
                        (nagiosgraph for example)
  --vendor-id VENDOR_ID
                        Use this if the vendor id is not the default one
                        (0x0c45)
  --product-id PRODUCT_ID
                        Use this if the product id is not the default one
                        (0x7401)
  --interface INTERFACE
                        Use this if the interface is not the default one (1)
```

## Installation

You need python3, [pyusb](http://sourceforge.net/projects/pyusb/) and [libusb-win32](http://sourceforge.net/projects/libusb-win32/)

### libusb-win32

Unpack, go to the bin folder and run the file inf-wizard.exe . This program will automatically generate a driver folder for a specific device and install it. 

In the list of devices to install the driver, you must select TEMPerV1.4 (Interface 1). Click Next, agree with everything, and we reach the driver saving window. Here it is better to create a separate folder for temper, where the utility will add all the necessary drivers. Note the VENDOR_ID, PRODUCT_ID as you may need them for the script to work. After that, you will be prompted to install the driver. We do this with the Install Now button.

If everything went well, then "Composite USB device" in Device Manager disappears and appears TEMPerV1.4 (Interface 1) . 

In the folder bin / amd64 distribution libusb-win32 has utility testlibusb-win.exe. Run it to make sure that the right we can see the device system. If everything is fine and the device is visible, it's all good. Remember that with Windows you need to reboot after installing a new driver.
