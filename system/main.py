import os
import json
import textwrap
import threading
import time
import shutil
import subprocess

NUM_RUNS_PER_EXP = 5  # how many experiments will be run with each configuration

def set_up_exp_folder(exp_id, max_clock_rate, max_event_num):
    """
    Sets up a logging folder for an experiment.

    :param exp_id: ID of the experiment
    :param max_clock_rate: Maximum clock rate
    :param max_event_num: Maximum number for determining events
    """
    # create log sub directory for the experiment if it doesn't exist
    exp_folder = f"logs/exp_{exp_id}"
    shutil.rmtree(exp_folder, ignore_errors=True)  # Deletes everything inside
    os.makedirs(exp_folder, exist_ok=True)  # Recreate the folder if needed

    # create sub directories for each run
    for i in range(NUM_RUNS_PER_EXP):
        run_folder = f"{exp_folder}/run_{i + 1}"
        os.makedirs(run_folder, exist_ok=True)

    # Write experiment metadata to README.md
    readme_content = textwrap.dedent(f"""\
        # Experiment {exp_id}
        - **Max Clock Rate:** {max_clock_rate}
        - **Max Event Num:** {max_event_num}
    """)

    # create a README file for the run
    with open(f"{exp_folder}/README.md", "w") as f:
        f.write(
            readme_content
        )


def perform_experiment_run(exp_id, run_id, host, port_map, max_clock_rate, max_event_num):
    """
    Runs an experiment with multiple virtual machines.

    :param exp_id: ID of the experiment
    :param run_id: ID of the run
    :param host: Hostname of the machine
    :param port_map: Dictionary of port numbers for each machine
    :param max_clock_rate: Maximum clock rate
    :param max_event_num: Maximum number for determining events
    """
    print(f"\tStarting run {run_id}...")
    log_file_path = f"exp_{exp_id}/run_{run_id}"

    procs = [ subprocess.Popen(['./machine.py', str(i + 1), log_file_path]) for i in range(3) ]
    for p in procs:
        p.wait()

    print(
        f"\tRun {run_id} complete. Log files are stored in logs/exp_{exp_id}/run_{run_id}.")


def run_all_experiments(experiment_configs, host, ports):
    """
    Runs all experiments with different configurations.

    :param experiment_configs: List of dictionaries with max_clock_rate and max_event_num
    :param host: Hostname of the machine
    :param ports: Dictionary of port numbers for each machine
    """
    # Run multiple experiments
    for i, exp_config in enumerate(experiment_configs):
        print(f"\nRunning experiment {i + 1}...")
        max_clock_rate = exp_config["max_clock_rate"]
        max_event_num = exp_config["max_event_num"]
        set_up_exp_folder(i + 1, max_clock_rate, max_event_num)

        for run_id in range(NUM_RUNS_PER_EXP):
            perform_experiment_run(i + 1, run_id + 1, host, ports,
                                   max_clock_rate, max_event_num)
        print(f"Experiment {i + 1} complete.")
    print("\nAll experiments complete.")


def main():
    # Make sure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Load configuration
    with open("../config.json") as f:
        config = json.load(f)
    host = config["HOST"]
    ports = config["PORTS"]
    config_max_clock_rate = config["MAX_CLOCK_RATE"]
    config_max_event_num = config["MAX_EVENT_NUM"]

    # Set up experiment configurations
    experiment_configs = [{
        "max_clock_rate": config_max_clock_rate,
        "max_event_num": config_max_event_num
    }, {
        "max_clock_rate": 3,
        "max_event_num": config_max_event_num
    }, {
        "max_clock_rate": config_max_clock_rate,
        "max_event_num": 5
    }]

    # Run experiments with each configuration
    run_all_experiments(experiment_configs, host, ports)


if __name__ == '__main__':
    main()
