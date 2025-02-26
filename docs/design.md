# Implementation Design Notes

## Sockets

All messages are sent over sockets. The port numbers to use are established in a configuration file. The process code is identical; each process is started with one command-line argument establishing its number (1, 2, or 3). From this, it can determine what port number to open a socket on by indexing into the list of port numbers.

## Socket Protocol

Each message is a 4-byte integer containing the sending process's logical clock value.

## Logging

All logged messages are prefixed with the process's number, taken from the command line argument passed at startup, e.g. `1> [log message]`

## Clock Rate

Clock rates (between 1 and 6 operations per second) are randomly generated at startup time and logged at that time.

## Threads

Each process runs a listening thread (which listens for messages on the sockets and then adds them to an internal queue) and a processing thread (which follows the message processing specification from the assignment description and then sleeps for `1/[clock rate]` seconds).

## Synchronization

The message queue must not allow simultaneous access from multiple threads.
