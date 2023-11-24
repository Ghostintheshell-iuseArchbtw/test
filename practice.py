import os
import sys
import time
import subprocess
import logging
import logging.handlers
import socket
import threading
import signal

# Global variables
honeypot1 = None
honeypot2 = None
port1 = 4444
port2 = 8080
honeypot1_thread = None
honeypot2_thread = None
honeypot1_log_file_path = '/var/log/honeypot1.log'
honeypot2_log_file_path = '/var/log/honeypot2.log'

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address='/dev/log')
formatter = logging.Formatter('%(module)s.%(funcName)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Signal handler
def signal_handler(signal, frame):
    logger.info('Exiting...')
    sys.exit(0)

# Honeypot function
def honeypot_func(honeypot, port, log_file_path):
    honeypot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    honeypot.bind(('', port))
    honeypot.listen(5)
    logger.info(f'Honeypot {port} listening on port {port}')

    while True:
        conn, addr = honeypot.accept()
        logger.info(f'Honeypot {port} connection from {addr}')
        threading.Thread(target=log_func, args=(log_file_path, addr)).start()
        conn.close()

# Logging function
def log_func(log_file_path, addr):
    with open(log_file_path, 'a') as log_file:
        log_file.write(f'Honeypot connection from {addr}\n')

# Start honeypot threads
honeypot1_thread = threading.Thread(target=honeypot_func, args=(honeypot1, port1, honeypot1_log_file_path))
honeypot2_thread = threading.Thread(target=honeypot_func, args=(honeypot2, port2, honeypot2_log_file_path))

# Start honeypot threads
honeypot1_thread.start()
honeypot2_thread.start()

# Signal handler
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Main
if __name__ == '__main__':
    while True:
        time.sleep(1)
