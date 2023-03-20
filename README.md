# DtnSimulator

Project for simulating Delay-Tolerant Networks, specifically satellite communication. It is fully implemented with Python3 using the sockets class that it provides.
It reads JSON files for creating the schemas of how messages must be sent through the network, transforming them into time evolving graphs and later into contact graphs between each pair of nodes.
To simulating the delay between sending and receiving a message, a file called `space.py` is used, which takes the messages that want to go from one node to another, stores it the time that is "traveling",
and when the timer hits 0, it sends it to the right receiver.

Also, classes where created for simulating the behavior of DTN nodes and the bundles that they send.

## Files
- `bundle.py`: A class that implements basic functionality of a bundle to be sent through the network. It carries a message and all necessary information the satellites need for sending and forwarding it.
- `contact_graph.py`: Class for representing a contact graph between two satellites. It has all the possible routes between them, with all of their parameters and variables associated.
- `DTNnode.py`: Class which implements a node, or satellite in this project. It has the parameters and functions for modelling how a node would behave.
- `ground_station.py`: Idea for a ground station from where all messages would start from. It is not currently used.
- `satellite.py`: One of the files which creates a DTNnode and uses it to communicate with other satellites. It must be run from console with the Id of the satellite, the number of priority queues it will have, and which time graph to use.
  -  `python3 satellite.py Id N_priority_queues graph_file`
- `space.py`: The other file that is run in parallel (ideally before) to all the other satellites. It receives all messages that must travel through space-time when going from one node to another, and stores them for the amount of time necessary to simulate the delay of traveling. It must be run from console, with an optional parameter of a loss probability, between 0 and 1
  - `python3 space.py loss_prob`
- `time_evolving_graph.py`: Class for representing a time evolving graph with the cocnnections between the satellites as the change over time.
- *time_graphs*: Folder with the time graphs to be used, along with a file with the address of the space socket. The time graphs contain the addresses of the nodes, with the contacts between them, the duration of each one and when all contacts have finished.

## How to run
The project is fairly simple, everything is executed from console. One console instance must be used per node, plus the one for running space. Also, for sending messages it is recommended to use the `netcat` command, also from another console
When running, it is recommended to try to run all files as simultaneous as possible, because their timers are not synced right now, they each start when the program starts.

When running `space.py`, it is possible to add a loss probability, between 0 and 1, which translates into how likely it is for each message to be lost due to external causes. If no value is passed, it will default to 0.

For each `satellite.py`, it is necessary to assign an Id (which must correspond to one from the time graph, or else no message will arrive); how many priority queues it will have, which are used when sending messages, it will prioritize the ones with a higher priority (higher is higher number); and which time graph to use, which right now are stored in the time_graphs/ folder.
- Example: `python3 satellite.py A 3 graph1.json`
Note that the graph only needs the name of the file, not the full directory. It will search inmediately inside the folder. When running a test, all satellites must use the same time graph.

## Tests
Right now there are only two tests, with `graph1.json` and `graph2.json`.
1. The first one has three nodes, A, B and C, and each of the contacts between them. The nodes take this information and creates contact graphs between each of the other nodes, detailing the best routes to use each instance.
2. The second one has four, A, B, C and D. The contacts are intrinsically more complicated, which makes apparent that the algorithm for transforming the json files into contact graphs is not perfect, and sometimes it finds the same route multiple times.

After running the files, in another console the `netcat` command is used to send a message from one satellite to another. Example:

    nc -u 127.0.0.1 8880 << EOF
    A|||C|||00000000|||1|||0|||0|||1|||1000|||holii
    EOF

This will send a message to node in address localhost 8880, which is node A in the time graph. The message starts there and its final destination is C, so it will be forwarded until it reaches it.

The message has that structure, which is then transformed into a bundle object from the class in `bundle.py`. The meaning of each, in order, is as follows:
- Origin node: From where the message started (not currently used anywhere, but might be useful in the future)
- Destination node: Where it is headed. When a node receives a bundle not destined to itself, it is forwarded. Else, it is printed to confirm it reached correctly.
- Size: A 8-byte string, which is a number describing the size of the bundle. It is calculated by the origin node, so just passing an placeholder is enough
- Priority: How important is the bundle. Higher number means higher priority. It goes from 1 to the amount of priority queues the satellites were instanced with.
- Critical: If it is critical or not, marked with a 1 or a 0. If it is, it must be sent through all channels possible for amplifying the chances of success in delivering the message.
- Custody: Custody request flag. Sometimes a node can ask its next recipient to store a bundle in case it doesn't have memory left or the queues are too long. This is not currently used, it is there because the protocols for DTN use it and it could be implemented in the future.
- Fragmentation: Flag for authorizing or not the fragmentation of the message. Same as before, not implemented but used in real cases.
- TTL: Time To Live. Number which marks the deadline of a bundle, in seconds. If the time is met before arriving to its destination, no matter where the bundle is, it is discarded.
- Message: The message itself that is wanted to be sent.

## Future
The most important thing is to improve the algorithm for generating contact graphs. These are not perfect, and although in some cases it works as intended, it is not always the case.
On another hand, the way storing messages in space works can be improved upon, probably with threads.
Finally, implement more functionalities, like the custody and fragmentation of bundles.