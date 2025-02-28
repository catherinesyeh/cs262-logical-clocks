import os
import json
import textwrap
import threading
import time

from machine import VirtualMachine

EXPERIMENT_DURATION = 60  # seconds
NUM_EXPERIMENTS = 5


def set_up_run_folder(run_id, max_clock_rate, max_event_num):
    """
    Sets up a logging folder for a run.

    :param run_id: ID of the run
    :param max_clock_rate: Maximum clock rate
    :param max_event_num: Maximum number for determining events
    """
    # create log sub directory for the run if it doesn't exist
    run_folder = f"logs/run_{run_id}"
    os.makedirs(run_folder, exist_ok=True)
    # remove all files in the directory
    files = os.listdir(run_folder)
    for file in files:
        os.remove(f"{run_folder}/{file}")

    # Write experiment metadata to README.md
    readme_content = textwrap.dedent(f"""\
        # Experiment Run {run_id}
        - **Max Clock Rate:** {max_clock_rate}
        - **Max Event Num:** {max_event_num}
    """)

    # create a README file for the run
    with open(f"logs/run_{run_id}/README.md", "w") as f:
        f.write(
            readme_content
        )


def run_experiment(run_id, host, port_map, max_clock_rate, max_event_num):
    """
    Runs an experiment with multiple virtual machines.

    :param run_id: ID of the run
    :param host: Hostname of the machine
    :param port_map: Dictionary of port numbers for each machine
    :param max_clock_rate: Maximum clock rate
    :param max_event_num: Maximum number for determining events
    """
    # Set up logging folder
    set_up_run_folder(run_id, max_clock_rate, max_event_num)

    print(f"Running experiment {run_id}...")

    threads = []
    machines = []
    num_threads = len(port_map)
    for i in range(num_threads):
        # Start a virtual machine
        vm = VirtualMachine(i + 1, host, port_map,
                            max_clock_rate, max_event_num, run_id)
        # Start a thread for each machine
        thread = threading.Thread(
            target=vm.run, daemon=True
        )
        threads.append(thread)
        machines.append(vm)
        thread.start()

    # Let experiment run for EXPERIMENT_DURATION seconds
    time.sleep(EXPERIMENT_DURATION)

    # Stop all machines
    for machine in machines:
        machine.stop()

    for thread in threads:
        thread.join()  # Keep the main thread alive until all threads are done

    print(
        f"Experiment {run_id} complete. Log files are stored in logs/run_{run_id}.")


def main():
    # Make sure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Load configuration
    with open("../config.json") as f:
        config = json.load(f)
    host = config["HOST"]
    ports = config["PORTS"]
    max_clock_rate = config["MAX_CLOCK_RATE"]
    max_event_num = config["MAX_EVENT_NUM"]

    # Run multiple experiments
    for run_id in range(NUM_EXPERIMENTS):
        run_experiment(run_id + 1, host, ports, max_clock_rate, max_event_num)


if __name__ == '__main__':
    main()
