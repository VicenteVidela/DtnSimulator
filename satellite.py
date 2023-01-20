import sys, time
from DTNnode import DTNnode

# python3 satellite.py A contactPlans/plan1.txt routes/routesA.json

# Get variables from console
try:
  _, id, contact_plan, route_list = sys.argv
except ValueError:
  print('ValueError: 3 values are needed from console: id, contact_plan_file, route_list_file')
  exit()

# Create the node
satellite = DTNnode(id)

# Add contact plan
try:
  satellite.update_contact_plan(contact_plan)
except (FileNotFoundError,IsADirectoryError, TypeError) as e:
  print(e)
  exit()

# Add routes
try:
  satellite.update_route_list(route_list)
except (FileNotFoundError,IsADirectoryError, TypeError) as e:
  print(e)
  exit()

# Get the address of it and bind it
address = satellite.get_address(satellite.id)
satellite.bind(address)
# Set the timeout for the receiving socket
satellite.settimeout(1)

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