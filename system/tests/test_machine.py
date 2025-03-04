import re
import shutil
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

# Load config
with open("../../config.json") as f:
    config = json.load(f)
host = config["HOST"]
ports = config["PORTS"]

# Create a folder for the test logs
folder = "test"
# Deletes everything inside
shutil.rmtree("logs/" + folder, ignore_errors=True)
os.makedirs("logs/" + folder, exist_ok=True)


def create_machine(id):
    """
    Create a machine with the given ID.

    :param id: ID of the machine
    :return: Machine
    """
    config_max_clock_rate = config["MAX_CLOCK_RATE"]
    config_max_event_num = config["MAX_EVENT_NUM"]
    config_duration = config["EXPERIMENT_DURATION"]
    return Machine(id, folder, host, ports,
                   config_max_clock_rate, config_max_event_num, config_duration)


@pytest.fixture(scope="session")
def machine():
    """
    Create a machine for testing.
    """
    machine = create_machine(1)
    yield machine
    machine.socket.close()


def test_machine_running(machine):
    """
    Test that the machine is initialized correctly.

    :param machine: Machine
    """
    assert machine.running == True, "Machine should be running"
    assert machine.logical_clock == 0, "Logical clock should be 0"
    assert machine.queue.empty(), "Message queue should be empty"
    assert machine.socket is not None, "Socket should be initialized"
    assert machine.connections != {}, "Connections should be initialized"


def test_machine_process(machine):
    """
    Test that the machine handles incoming messages correctly.

    :param machine: Machine
    """

    # Send message
    s = socket.socket(
        socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((host, ports['1']))
    s.sendall(struct.pack('i', 99))
    time.sleep(0.5)

    # Ensure it's received
    assert not machine.queue.empty(), "Machine should have received a message"
    machine.run()
    assert machine.queue.empty(), "Machine should have processed the message"
    assert machine.logical_clock == 100, "Logical clock should have been updated"


def test_machine_send(machine):
    """
    Test that the machine sends messages correctly.

    :param machine: Machine
    """

    machine2 = create_machine(2)
    machine3 = create_machine(3)

    # Run the machine 100 times
    for i in range(100):
        machine.run()

    # Ensure it sent messages some (but not all) of the time
    assert machine.logical_clock > 100, "Machine should have sent messages"
    assert not machine2.queue.empty(), "Machine 2 should have received messages"
    assert not machine3.queue.empty(), "Machine 3 should have received messages"
    assert machine2.queue.qsize() + \
        machine3.queue.qsize() < 100, "Total messages received should be less than 100"

    machine2.socket.close()
    machine3.socket.close()


def test_stop(machine):
    """
    Test that the machine stops running correctly.

    :param machine: Machine
    """
    with pytest.raises(SystemExit) as e:
        machine.stop()

    assert e.type == SystemExit, "Machine should have exited"


def test_logging():
    """
    Test that the machine logs events correctly.
    """
    log_file_path = "test"
    process_id = 1
    port = ports[str(process_id)]

    # Define the expected log format using regex
    log_pattern = re.compile(
        r"^\d+> Event: .+ \| System Time: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \| Logical Clock: \d+ \| Queue Length: \d+$"
    )

    with open(f"logs/{log_file_path}/process_{process_id}.log", "r") as f:
        lines = f.readlines()
        assert len(lines) > 3, "Log file should have at least 3 lines"
        # check for different event types: processed message, sent message, internal event
        counts = {
            "Processed message": 0,
            "Sent message": 0,
            "Internal event": 0
        }
        for line in lines:
            assert log_pattern.match(
                line.strip()) is not None, "Log line does not match expected format"
            if "Processed message" in line:
                counts["Processed message"] += 1
            elif "Sent message" in line:
                counts["Sent message"] += 1
            elif "Internal event" in line:
                counts["Internal event"] += 1

        # check if first line has right port
        assert f"Initialized on {port}" in lines[
            0], "First line should have initialized event and right port"
        # check if second line has right connection
        assert f"Connected to machine 2 on port {ports['2']}" in lines[
            1], "Second line should have connected event and right port"
        # check if third line has right connection
        assert f"Connected to machine 3 on port {ports['3']}" in lines[
            2], "Third line should have connected event and right port"
        # check if "stopped" event is in the last line
        assert "Stopped" in lines[-1], "Last line should have stopped event"
        # check if all event types are present
        assert counts["Processed message"] > 0, "At least one processed message should be logged"
        assert counts["Sent message"] > 0, "At least one sent message should be logged"
        assert counts["Internal event"] > 0, "At least one internal event should be logged"
