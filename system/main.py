import os
import json
import textwrap
import threading
import time
import shutil
import subprocess

NUM_RUNS_PER_EXP = 5  # how many experiments will be run with each configuration

def set_up_exp_folder(max_clock_rate, max_event_num):
    """
    Sets up a logging folder for an experiment.

    :param max_clock_rate: Maximum clock rate
    :param max_event_num: Maximum number for determining events
    """
    # create log sub directory for the experiment if it doesn't exist
    exp_folder = f"logs"
    shutil.rmtree(exp_folder, ignore_errors=True)  # Deletes everything inside
    os.makedirs(exp_folder, exist_ok=True)  # Recreate the folder if needed

    # create sub directories for each run
    for i in range(NUM_RUNS_PER_EXP):
        run_folder = f"{exp_folder}/run_{i + 1}"
        os.makedirs(run_folder, exist_ok=True)

    # Write experiment metadata to README.md
    readme_content = textwrap.dedent(f"""\
        # Experiment Logs
        - **Max Clock Rate:** {max_clock_rate}
        - **Max Event Num:** {max_event_num}
    """)

    # create a README file for the run
    with open(f"{exp_folder}/README.md", "w") as f:
        f.write(
            readme_content
        )


def perform_experiment_run(run_id):
    """
    Runs an experiment with multiple virtual machines.

    :param run_id: ID of the run
    """
    print(f"\tStarting run {run_id}...")
    log_file_path = f"run_{run_id}"

    procs = [ subprocess.Popen(['./machine.py', str(i + 1), log_file_path]) for i in range(3) ]
    for p in procs:
        p.wait()

    print(
        f"\tRun {run_id} complete. Log files are stored in logs/run_{run_id}.")


def main():
    """
    Runs a multi-run experiment with the current configuration.

    :param host: Hostname of the machine
    :param ports: Dictionary of port numbers for each machine
    """
    # Run multiple experiments
    print(f"\nRunning experiment...")
    with open("../config.json") as f:
        config = json.load(f)
    max_clock_rate = config["MAX_CLOCK_RATE"]
    max_event_num = config["MAX_EVENT_NUM"]
    set_up_exp_folder(max_clock_rate, max_event_num)

    for run_id in range(NUM_RUNS_PER_EXP):
        perform_experiment_run(run_id + 1)
    print(f"Experiment complete.")


if __name__ == '__main__':
    main()
