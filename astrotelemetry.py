import sys
sys.path.append('reporter')
sys.path.append('interceptor')

import time

import socket
import atexit
import threading

from interceptor import interceptor
from statsReporter import StatsReporter
from indiClientReporter import IndiClientReporter
from influxFormatter import format_measurement_to_str_influx


verbose = False

telegraf_ip = 'localhost'
telegraf_udp_port = 8094
indi_ip = 'localhost'
indi_tcp_port = 7624
report_interval = 10

def interceptorWorker():
    """thread worker function"""
    print ('interceptorWorker')
    interceptor.process()
    return

def indiReporterWorker():
    """thread worker function"""
    print ('indiPropsWorker')
    indiReporter.process(report_interval)
    return


reporter = StatsReporter((socket.AF_INET, socket.SOCK_DGRAM), (telegraf_ip, telegraf_udp_port),
                         formatter=format_measurement_to_str_influx, verbose=verbose)
atexit.register(reporter.close_socket)

indiReporter = IndiReporter(reporter)
indiReporter.setServer(indi_ip, indi_tcp_port)
interceptor = interceptor()
interceptor.setServer(indi_ip, indi_tcp_port)

while(indiclient.isServerConnected() == False):    
    print("indiReporter: Trying to connect ...")
    indiReporter.connectServer()
    time.sleep(1)
print("indiReporter.connectServer(): OK")

while(interceptor.isServerConnected() == False):    
    print("interceptor: Trying to connect ...")
    interceptor.connectServer()
    time.sleep(1)
print("interceptor.connectServer(): OK")

t1 = threading.Thread(target = interceptorWorker)
t2 = threading.Thread(target = indiReporterWorker)

t1.start()
t2.start()











