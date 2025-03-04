import pytest
import os
import sys
import json
import socket
import struct
import time

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

from machine import Machine

with open("../config.json") as f:
    config = json.load(f)
host = config["HOST"]
ports = config["PORTS"]

def create_machine(id):
    config_max_clock_rate = config["MAX_CLOCK_RATE"]
    config_max_event_num = config["MAX_EVENT_NUM"]
    config_duration = config["EXPERIMENT_DURATION"]
    folder = "test"
    os.makedirs("logs/" + folder, exist_ok=True)
    return Machine(id, folder, host, ports,
        config_max_clock_rate, config_max_event_num, config_duration)

@pytest.fixture(scope="session")
def machine():
    machine = create_machine(1)
    yield machine
    machine.socket.close()

def test_machine_running(machine):
    """
    Test that the machine is initialized correctly.
    """
    assert machine.running == True, "Machine should be running"

def test_machine_process(machine):
    """
    Test that the machine handles incoming messages correctly.
    """

    # Send message
    s = socket.socket(
        socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((host, ports['1']))
    s.sendall(struct.pack('i', 99))
    time.sleep(0.5)

    # Ensure it's received
    assert not machine.queue.empty()
    machine.run()
    assert machine.queue.empty()
    assert machine.logical_clock == 100

def test_machine_send(machine):
    """
    Test that the machine sends messages correctly.
    """

    machine2 = create_machine(2)
    machine3 = create_machine(3)

    # Run the machine 100 times
    for i in range(100):
        machine.run()

    # Ensure it sent messages some (but not all) of the time
    assert machine.logical_clock > 100
    assert not machine2.queue.empty()
    assert not machine3.queue.empty()
    assert machine2.queue.qsize() + machine3.queue.qsize() < 100

    machine2.socket.close()
    machine3.socket.close()