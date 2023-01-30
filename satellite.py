import sys, time, os
from DTNnode import DTNnode

# For example: python3 satellite.py A 3 time_graphs/graph1.json

# Get variables from console
args = sys.argv

if len(args)==4:
  id = args[1]
  priorities_amount = int(args[2])
  time_graph = args[3]
else:
  raise ValueError('ValueError: 3 values needed from console: id, priorities_amout, time_graph')

# Create the node
satellite = DTNnode(id, priorities_amount)

# Create and assign the time graph from the file
time_graph = os.path.dirname(os.path.realpath(__file__)) + '/time_graphs/' + time_graph
satellite.assign_time_graph(time_graph)

# Get the address of it and bind it
address = satellite.get_address(satellite.id)
satellite.bind(address)
# Set the timeout for the receiving socket
satellite.settimeout(1)

for addr in satellite.address_list:
  if (satellite.id != addr):
    satellite.create_route_list(addr, 0)

start_time = time.time()
current_time = 0

alarm_on = False
send_queue_timer = 0

# Main loop
try:
  while True:
    # Listen for messages
    send_queue_timer = satellite.recv(1024, current_time, alarm_on=alarm_on, timer=send_queue_timer)

    # For keeping track of how much time has passed
    current_time = time.time() - start_time

    # If it has to wait for the route to be available
    if (send_queue_timer > 0 and not alarm_on):
      alarm_on = True
    # If timer expired, start sending
    if (alarm_on and send_queue_timer==-1):
      alarm_on = False
      satellite.send_bundles_in_queue(current_time)


except KeyboardInterrupt:
  print('Program finished.')