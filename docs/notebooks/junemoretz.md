# Engineering Notebook - June Moretz

## February 28, 2025

I discussed this assignment after class on Wednesday with Catherine, and started writing up some notes on how it should work. My Wednesdays and Thursdays are quite busy, so today is the first day I've had a chance to work on this - Catherine has put together a lot of the base of the system already. As it was written, the separate "machines" in the system were being created as threads from a root process, rather than independent system-level processes. I started by rewriting this to make the machines logically distinct processes on the operating system level, ensuring that we are following the assignment specification properly, and updated the root coordinator process to start the machines as subprocesses.

I also rewrote the coordinator to simplify it, using just the numbers from the configuration rather than modifying them on the fly to run multiple experiments with different values for the maximum clock rate and maximum event number (the random number generated on each clock cycle to determine what action to perform). The coordinator will now just run a number of runs for a single experiment, with values fixed by the config file. I did some other refactoring as well, ensuring the code was readable, understandable, and followed the specification exactly. It seems to be in good working order now - just a matter of performing our analysis and writing up findings!

Most design notes are in the design.md file, rather than here.

Determining some experimental results is fairly trivial. Transforming a log file into the changes in queue length and logical clock values is fairly simple. Calculating drift is a bit more difficult. Drift must be determined by taking the highest logical clock value of any process at the same system time and then taking the difference.
