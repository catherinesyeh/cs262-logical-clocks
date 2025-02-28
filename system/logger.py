import time


def log_event(run_id, process_id, event, msg_queue_length, logical_clock_time):
    """
    Logs event to file for a specific process.

    :param run_id: ID of the run
    :param process_id: ID of the process
    :param event: Event to log
    :param msg_queue_length: Length of the message queue
    :param logical_clock_time: Logical clock time
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(f"logs/run_{run_id}/process_{process_id}.log", "a") as f:
        f.write(
            f"{process_id}> Event: {event} | System Time: {timestamp} | Logical Clock: {logical_clock_time} | Queue Length: {msg_queue_length}\n")
