import sys
sys.path.append('reporter')
sys.path.append('interceptor')
from influxFormatter import format_measurement_to_str_influx
from indiReporter import IndiReporter
from statsReporter import StatsReporter
from interceptor import Interceptor
import logging
import threading
import atexit
import socket
import time



verbose = False
telegraf_ip = 'localhost'
telegraf_udp_port = 8094
indi_ip = 'localhost'
indi_tcp_port = 7624
report_interval = 10

logging.basicConfig(
    format='%(asctime)s [%(filename)s %(module)s %(funcName)s] %(message)s', level=logging.INFO)
logger = logging.getLogger('astrotelemetry')


def interceptorWorker():
    logger.info("running interceptorWorker...")
    interceptor.process()
    return


def indiReporterWorker():
    logger.info("running indiReporterWorker...")
    indiReporter.process(report_interval)
    return


reporter = StatsReporter((socket.AF_INET, socket.SOCK_DGRAM), (telegraf_ip, telegraf_udp_port),
                         formatter=format_measurement_to_str_influx, verbose=verbose)
atexit.register(reporter.close_socket)

indiReporter = IndiReporter(reporter)
indiReporter.setServer(indi_ip, indi_tcp_port)
interceptor = Interceptor()
interceptor.setServer(indi_ip, indi_tcp_port)

while(indiReporter.isServerConnected() == False):
    logger.info("indiReporter: Trying to connect ...")
    indiReporter.connectServer()
    time.sleep(1)
logger.info("indiReporter.connectServer(): OK")

while(interceptor.isServerConnected() == False):
    logger.info("interceptor: Trying to connect ...")
    interceptor.connectServer()
    time.sleep(1)
logger.info("interceptor.connectServer(): OK")

t1 = threading.Thread(target=interceptorWorker)
t2 = threading.Thread(target=indiReporterWorker)

t1.start()
t2.start()
