import PyIndi
import time
import sys
import socket
import math
import random
import atexit
from statsReporter import StatsReporter
from indiClientReporter import IndiClientReporter
from formatter import format_measurement_to_str_influx


reporter = StatsReporter((socket.AF_INET, socket.SOCK_DGRAM),('localhost', 8094), formatter=format_measurement_to_str_influx)
atexit.register(reporter.close_socket)

indiclient = IndiClientReporter(reporter)
indiclient.setServer('localhost', 7624)
indiclient.connectServer()
indiclient.reportAllIndiProps(9)




