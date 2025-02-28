import time


def log_event(log_file_path, process_id, event, msg_queue_length, logical_clock_time):
    """
    Logs event to file for a specific process.

    :param log_file_path: Path to the log file
    :param process_id: ID of the process
    :param event: Event to log
    :param msg_queue_length: Length of the message queue
    :param logical_clock_time: Logical clock time
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(f"logs/{log_file_path}/process_{process_id}.log", "a") as f:
        f.write(
            f"{process_id}> Event: {event} | System Time: {timestamp} | Logical Clock: {logical_clock_time} | Queue Length: {msg_queue_length}\n")
