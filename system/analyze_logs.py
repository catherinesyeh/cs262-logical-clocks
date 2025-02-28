from datetime import datetime
import os
import re
import pandas as pd
import matplotlib.pyplot as plt

LOG_DIR = "logs"

# Regular expression pattern for parsing log files
LOG_PATTERN = re.compile(
    r"(\d+)> Event: (.+?) \| System Time: ([\d-]+ [\d:]+) \| Logical Clock: (\d+) \| Queue Length: (\d+)"
)


def plot_statistics(summary_df):
    """
    Plots the statistics for each process.

    :param summary_df: DataFrame containing the computed statistics
    :param folder: Name of the experiment
    """
    # Create figure folder if it doesn't exist
    os.makedirs(f"figures", exist_ok=True)

    # Plot min, mean, and max drift for each process and show the plot
    summary_df[["Min Drift", "Mean Drift", "Max Drift"]].plot(
        kind="line", title=f"Drift vs. Clock Rate", xlabel="Clock Rate", ylabel="Drift (seconds)")
    # Save the plot to a file
    plt.savefig(f"figures/drift.png")

    # Plot mean, max logical clock jump for each process and show the plot
    summary_df[["Mean Logical Clock Jump", "Max Logical Clock Jump"]].plot(
        kind="line", title=f"Logical Clock Jump vs. Clock Rate", xlabel="Clock Rate", ylabel="Logical Clock Jump")
    # Save the plot to a file
    plt.savefig(f"figures/logical_clock_jump.png")

    # Plot mean, max queue length for each process and show the plot
    summary_df[["Mean Queue Length", "Max Queue Length"]].plot(
        kind="line", title=f"Queue Length vs. Clock Rate", xlabel="Clock Rate", ylabel="Queue Length")
    # Save the plot to a file
    plt.savefig(f"figures/queue_length.png")

    # Plot mean, max queue length change for each process and show the plot
    summary_df[["Mean Queue Length Change", "Max Queue Length Change"]].plot(
        kind="line", title=f"Queue Length Change vs. Clock Rate", xlabel="Clock Rate", ylabel="Queue Length Change")
    # Save the plot to a file
    plt.savefig(f"figures/queue_length_change.png")

    # Plot sent and received events as a percentage of total events for each process and show the plot
    summary_df[["Sent Events", "Received Events", "Internal Events"]].div(summary_df["Total Events"], axis=0).plot(
        kind="bar", stacked=True, title=f"Event Distribution vs. Clock Rate", xlabel="Clock Rate", ylabel="% of Events")
    # Save the plot to a file
    plt.savefig(f"figures/events.png")


def compute_statistics(df):
    """
    Computes statistics from the log data.

    :param df: DataFrame containing the log data
    :return: DataFrame containing the computed statistics
    """
    # Group by process ID
    group = df.groupby(["Clock Rate"])

    # Calculate min drift for each process
    min_drift = group["Drift"].min()

    # Calculate mean drift for each process
    mean_drift = group["Drift"].mean()

    # Calculate max drift for each process
    max_drift = group["Drift"].max()

    # Calculate mean logical clock jump for each process
    mean_logical_clock_jump = group["Logical Clock Jump"].mean()

    # Calculate mean queue length for each process
    mean_queue_length = group["Queue Length"].mean()

    # Calculate max queue length for each process
    max_queue_length = group["Queue Length"].max()

    # Calculate max logical clock jump for each process
    max_logical_clock_jump = group["Logical Clock Jump"].max()

    # Calculate mean queue length change for each process
    mean_queue_length_change = group["Queue Length Change"].mean()

    # Calculate max queue length change for each process
    max_queue_length_change = group["Queue Length Change"].max()

    # Calculate total number of Sent events
    sent_events = group.apply(lambda x: x["Event"].str.contains(
        "Sent").sum(), include_groups=False)

    # Calculate total number of Received events
    received_events = group.apply(lambda x: x["Event"].str.contains(
        "Received").sum(), include_groups=False)

    # Calculate total number of Internal events
    internal_events = group.apply(lambda x: x["Event"].str.contains(
        "Internal").sum(), include_groups=False)

    # Calculate total number of events for each process
    total_events = group.size()

    # Create a summary DataFrame
    summary_df = pd.DataFrame({
        "Min Drift": min_drift,
        "Mean Drift": mean_drift,
        "Max Drift": max_drift,
        "Mean Logical Clock Jump": mean_logical_clock_jump,
        "Max Logical Clock Jump": max_logical_clock_jump,
        "Mean Queue Length": mean_queue_length,
        "Max Queue Length": max_queue_length,
        "Mean Queue Length Change": mean_queue_length_change,
        "Max Queue Length Change": max_queue_length_change,
        "Sent Events": sent_events,
        "Received Events": received_events,
        "Internal Events": internal_events,
        "Total Events": total_events
    })

    return summary_df


def parse_log_files(folder_path):
    """
    Parses all log files in a folder and returns a DataFrame.

    :param folder_path: Path to the log files
    :return: DataFrame containing the log data
    """
    data = []

    # Loop through each run_x folder inside the experiment folder
    for run_folder in sorted(os.listdir(f"{folder_path}")):
        run_path = os.path.join(folder_path, run_folder)

        # ensure run_path is a directory
        if not os.path.isdir(run_path):
            continue

        print(f"Processing {run_path}...")
        run_number = int(run_folder.split("_")[-1])

        # Loop through log files inside the run folder
        for log_file in sorted(os.listdir(run_path)):
            if log_file.endswith(".log"):
                log_path = os.path.join(run_path, log_file)

                with open(log_path, "r") as file:
                    last_logical_clock = 0
                    last_queue_length = 0
                    for line in file:
                        match = LOG_PATTERN.match(line)
                        if match:
                            process_id, event, system_time_str, logical_clock, queue_length = match.groups()

                            # convert system time to timestamp
                            system_time = datetime.strptime(
                                system_time_str, "%Y-%m-%d %H:%M:%S")

                            if "Initialized" in event:
                                # extract clock rate
                                clock_rate = int(event.split()[-1])
                                start_time = system_time
                                continue
                            if "Connected" in event or "Stopped" in event:
                                # skip connection and stop events
                                continue

                            # calculate elapsed time in seconds
                            elapsed_time = (
                                system_time - start_time).total_seconds()

                            # calculate jump in logical clock
                            logical_clock = int(logical_clock)
                            logical_clock_jump = logical_clock - last_logical_clock
                            last_logical_clock = logical_clock

                            # calculate change in queue length
                            queue_length = int(queue_length)
                            queue_length_change = queue_length - last_queue_length
                            last_queue_length = queue_length

                            data.append({
                                "Run": run_number,
                                "Process ID": int(process_id),
                                "Event": event,
                                "System Time": system_time,
                                "Elapsed Seconds": elapsed_time,
                                "Logical Clock": logical_clock,
                                "Logical Clock Jump": logical_clock_jump,
                                "Queue Length": queue_length,
                                "Queue Length Change": queue_length_change,
                                "Clock Rate": clock_rate
                            })
    
    # Calculate drift
    df = pd.DataFrame(data)
    df["Max Clock"] = df.groupby(["Run", "System Time"])["Logical Clock"].transform('max')
    df["Drift"] = df["Max Clock"] - df["Logical Clock"]
    return df


def main():
    # Process all log files in the logs directory
    df = parse_log_files(LOG_DIR)
    summary_df = compute_statistics(df)
    plot_statistics(summary_df)

    print("Analysis complete.")


if __name__ == "__main__":
    main()
