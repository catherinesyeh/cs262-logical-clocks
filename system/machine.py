#!/usr/bin/env python3

import time
import random
import socket
import threading
import struct
import queue
import sys
import json

from logger import log_event


class Machine:
    def __init__(self, id, log_file_path, host, port_map, max_clock_rate, max_event_num, timeout):
        """
        Initializes a virtual machine.

        :param id: ID of the machine
        :param log_file_path: Path to log file for this experiment run
        :param host: Hostname of the machine
        :param port_map: Dictionary of port numbers for each machine
        :param max_clock_rate: Maximum clock rate in operations/second (default: 6)
        :param max_event_num: Maximum number for determining what event to perform on each clock cycle (default: 10)
        :param timeout: How long to run the machine before exiting, in seconds (default: 60)
        """

        ## SET UP PROPERTIES
        self.id = id  # process number (1, 2, or 3)
        self.host = host  # hostname of the machine
        self.port_map = port_map  # dictionary of port numbers for each machine
        self.port = self.port_map[str(id)]  # port number for the machine
        self.clock_rate = random.randint(1, max_clock_rate)  # choose a random clock rate between 1 and max_clock_rate
        self.logical_clock = 0  # initialize Lamport clock to 0
        self.max_event_num = max_event_num  # maximum number for determining events

        # Create a socket to send messages
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))

        # Start listening thread
        # Ensure all other processes have open sockets before trying to connect!
        time.sleep(1)
        self.running = True  # flag to indicate if the machine is running
        self.thread = threading.Thread(
            target=self.listen_for_messages, daemon=True).start()
        self.queue = queue.Queue()  # Thread-safe queue to hold incoming messages

        # Log initialization
        self.log_file_path = log_file_path
        log_event(self.log_file_path, self.id, 
            f"Initialized on {self.port} with clock rate {self.clock_rate}", self.queue.qsize(), self.logical_clock)

        # Connect to other machines
        self.connections = {}
        self.connect_to_machines()

        timer = threading.Timer(timeout, self.stop)
        timer.start()

        self.run()

    def listen_for_messages(self):
        """
        Listens for incoming messages on the socket.
        """
        while self.running:
            try:
                # listen for 4 byte messages
                data, _ = self.socket.recvfrom(4)
                message = struct.unpack('i', data)[0]
                self.queue.put(message)
            except Exception as e:
                if not self.running:
                    # if the machine is stopped, exit the loop
                    break
                print(f"ERROR: Can't receive message: {e}")

    def connect_to_machines(self):
        """
        Connects to other machines at startup.
        """
        for machine_id, port in self.port_map.items():
            if machine_id != str(self.id):
                try:
                    s = socket.socket(
                        socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect((self.host, port))
                    self.connections[machine_id] = s
                    log_event(self.log_file_path, self.id, f"Connected to machine {machine_id} on port {port}", self.queue.qsize(
                    ), self.logical_clock)
                except Exception as e:
                    print(f"ERROR: Can't connect to machine {machine_id}: {e}")

    def send_message(self, recipient_id):
        """
        Sends a message to another machine.

        :param recipient_id: ID of the recipient machine
        """
        # check if still running
        if not self.running:
            return

        # check if recipient id is valid
        if recipient_id not in self.connections:
            print(f"ERROR: Invalid recipient ID: {recipient_id}")
            return

        message = struct.pack('i', self.logical_clock)

        # send message to recipient
        try:
            self.connections[recipient_id].sendall(message)
            log_event(self.log_file_path, self.id, f"Sent message to machine {recipient_id}", self.queue.qsize(
            ), self.logical_clock)
        except Exception as e:
            print(f"ERROR: Can't send message to machine {recipient_id}: {e}")

    def process_message(self):
        """
        Receives a message from the queue and processes it.
        """
        if self.queue.empty():
            print(f"ERROR: Queue is empty")
            return

        queue_length = self.queue.qsize()  # get queue length before receiving message
        received_clock = self.queue.get()  # get message from queue
        # update Lamport clock
        self.logical_clock = max(self.logical_clock, received_clock) + 1
        log_event(self.log_file_path, self.id, f"Processed message", queue_length, self.logical_clock)

    def run(self):
        """
        Main loop to run the virtual machine.
        """
        while self.running:
            time.sleep(1 / self.clock_rate)  # simulate clock rate

            if not self.queue.empty():
                # If there are messages in the queue, process one
                self.process_message()
            else:
                # Else, generate a random number between 1 to max_event_num to determine event
                event = random.randint(1, self.max_event_num)
                self.logical_clock += 1  # increment Lamport clock

                # Lookup tables for determining next and previous machine
                next = [None, "2", "3", "1"]
                prev = [None, "3", "1", "2"]

                if event == 1:
                    # Send a message to the next machine
                    recipient_id = next[int(self.id)]
                    self.send_message(recipient_id)
                elif event == 2:
                    # Send a message to the other machine
                    recipient_id = prev[int(self.id)]
                    self.send_message(recipient_id)
                elif event == 3:
                    # Send a message to both other machines
                    recipient_id_1 = next[int(self.id)]
                    recipient_id_2 = prev[int(self.id)]
                    self.send_message(recipient_id_1)
                    self.send_message(recipient_id_2)
                else:
                    # Log an internal event
                    log_event(self.log_file_path, self.id, f"Internal event",
                              self.queue.qsize(), self.logical_clock)

    def stop(self):
        """
        Stops the virtual machine.
        """
        self.running = False
        self.socket.close()
        for connection in self.connections.values():
            connection.close()

        # empty self.connections
        self.connections = {}

        log_event(self.log_file_path, self.id, f"Stopped",
                  self.queue.qsize(), self.logical_clock)

        sys.exit(0)


# Takes 2 command line arguments:
# ID (1, 2, or 3)
# Log file path
if __name__ == '__main__':
    with open("../config.json") as f:
        config = json.load(f)
    host = config["HOST"]
    ports = config["PORTS"]
    config_max_clock_rate = config["MAX_CLOCK_RATE"]
    config_max_event_num = config["MAX_EVENT_NUM"]
    config_duration = config["EXPERIMENT_DURATION"]
    machine = Machine(int(sys.argv[1]), sys.argv[2], host, ports,
        config_max_clock_rate, config_max_event_num, config_duration)
