import sys
sys.path.append('reporter')

import socket
import atexit

from statsReporter import StatsReporter
from indiClientReporter import IndiClientReporter
from influxFormatter import format_measurement_to_str_influx

verbose = True

telegraf_ip = 'localhost'
telegraf_udp_port = 8094

indi_ip = 'localhost'
indi_tcp_port = 7624

report_interval = 10


reporter = StatsReporter((socket.AF_INET, socket.SOCK_DGRAM), (telegraf_ip, telegraf_udp_port),
                         formatter=format_measurement_to_str_influx, verbose=verbose)
atexit.register(reporter.close_socket)

indiclient = IndiClientReporter(reporter)
indiclient.setServer(indi_ip, indi_tcp_port)
indiclient.connectServer()
indiclient.reportAllIndiProps(report_interval)

