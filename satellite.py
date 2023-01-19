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

# Main loop
try:
  while True:
    return_time = satellite.recv(1024, current_time)
    current_time = time.time() - start_time    # For keeping track of how much time has passed
except KeyboardInterrupt:
  print('Program finished.')