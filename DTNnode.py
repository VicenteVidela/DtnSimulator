import socket, time, json, ast

class DTNnode:
  # initialize the variables for the dtn node
  def __init__(self, id):
    self.id = id              # Id for identifying the satellite
    self.socketRecv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # sockets for receiving and
    self.socketSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # sending messages
    self.address = None       # Satellite address
    self.contact_plan = None  # Contact plan
    self.address_list = {}  # Dictionary of the different addresses of the other nodes
    self.route_list = None    # List of route lists for the other nodes
    self.send_queue = []      # List for storing all the messages that have to be sent when available

  # Sets the timeout of the receiving socket
  def settimeout(self, timeout):
    self.socketRecv.settimeout(timeout)

  # Bind receiving socket to the address
  def bind(self, address):
    self.address = address
    self.socketRecv.bind(self.address)

  # Get address corresponding to node id
  def get_address(self, id):
    return ('127.0.0.1', self.address_list[id])

  # Update contact plan with new one and copmute the route lists if necessary
  def update_contact_plan(self, new_plan_dir, compute_routes=False):
    # Open file and read it
    with open(new_plan_dir) as f:
      # Check file extension
      if (new_plan_dir.split('.')[-1] != 'txt'):
        raise TypeError('File is not .txt')
      contactsString = f.read()
    f.close()

    # Create contacts array and add valid contacts
    contacts = []
    for c in contactsString.splitlines():
      if (c.startswith('address')):
        _, node, address = c.split()
        self.address_list[node] = int(address)
      elif (len(c) > 0 and c[0] != '#'):
        contacts.append(c)

    # Update contact plan
    self.contact_plan = contacts
    # Create route list
    if compute_routes:
      self.route_list = self.create_route_list(contacts)
      # TODO: Update other nodes

  # TODO: Create routes based on contact plan
  def create_route_list(self, plan, current_time):
    # Create route list based on contact plan
    # Iterate through the plan
    for c in plan:
      origin, receiver, start_time, end_time, rate, distance = c.split()
      # We are interested only in the ones that start on this node
      # and also any that has already ended are discarded
      if (origin != self.id or current_time >= (end_time + distance)):
        continue

  # Update route list with a new one
  def update_route_list(self, new_list_dir):
    # Open file and read it
    with open(new_list_dir) as f:
      # Check file extension
      if (new_list_dir.split('.')[-1] != 'json'):
        raise TypeError('File is not .json')
      data = json.load(f)
      self.route_list = data
    f.close()

  # Check possible routes for a bundle
  def check_routes(self, bundle, current_time):
    # Get bundle destination
    dest = bundle.get_dest()

    # If no route has been assigned, search one for it
    if (bundle.get_route() is None):
      all_routes = self.route_list[dest] # Get list of all routes (dictionaries) to the destination
      candidate_routes = []   # Where all candidate routes will be stored
      for r in all_routes:
        # If route expired or the bundle can't make it in time or the bundle is bigger than what the route can handle
        if ((current_time > int(r['endTime'])) or (int(r['startTime']) + int(r['distance'])) > bundle.get_deadline()) \
            or (bundle.get_size() > (int(r['rate']) * (int(r['endTime']) - int(r['startTime'])))): continue # discard it
        # else, add it to the list
        candidate_routes.append(r)

      # TODO get best route
      try:
        best_route = candidate_routes[0]
        bundle.set_route(best_route)
      except IndexError:
        print('No possible route found, putting bundle in limbo.')

    else:
      # Check the route and get next hop
      route_splitted = bundle.get_route()['route'].split()
      try:
        i = route_splitted.index(self.id)
      except ValueError:
        print('Current node not in route, something happened.')
        return
      # Set the next hop for the bundle
      bundle.set_next_hop(route_splitted[i-1])

    return bundle

  # Add a bundle to send queue
  def add_to_queue(self, bundle, current_time):
    # If deadline already passed, discard it
    if (0 < bundle.get_deadline() <= current_time):
      print("Bundle deadline already passed, discarding.")
      return

    # Check routes for the bundle and return updated bundle
    updated_bundle = self.check_routes(bundle, current_time)

    # If a route was found, add it to queue
    if (updated_bundle.get_route() is not None):
      self.send_queue.append(updated_bundle)
      self.send_first_in_queue(current_time)
    else:
      #TODO Add to limbo
      pass

  # Get the first bundle in queue and try to send
  def send_first_in_queue(self, current_time):
    # If list is empty, do nothing
    if (not self.send_queue):
      print("Queue list is empty.")
      return -1

    # Retrieve bundle from list
    bundle_to_send = self.send_queue[0]
    # Check deadline and discard it if it passed
    if (0 < bundle_to_send.get_deadline() <= current_time):
      print("Bundle deadline already passed, discarding.")
      return -1

    route_start_time = bundle_to_send.get_route()['startTime']
    delta_time = route_start_time-current_time
    # Route not yet available, have to wait
    if (delta_time > 0):
      print('Route not yet available, have to wait', str(delta_time)+'s')
      time.sleep(delta_time)

    # Passed all checks, delete it from the list and send
    bundle_to_send = self.send_queue.pop(0)
    self.send(bundle_to_send)
    return 0

  # Send a bundle forward to the next hop
  def send(self, bundle):
    dest = self.get_address(bundle.get_next_hop())
    self.socketSend.sendto(str(bundle).encode(), dest)
    print('Bundle forwarded to node:', bundle.get_next_hop())

  # Receive a bundle, print if it was its destination, or forward it
  def recv(self, buff_size, current_time):
    # For counting how many seconds have passed since the call of the function
    start_time = time.time()

    print('Node', self.id, 'waiting for message. Elapsed time: 0s')
    # Main cycle of receiving
    while True:
      try:
          recv_bundle, _ = self.socketRecv.recvfrom(buff_size)
          break
      except TimeoutError:
          print ("\033[A\033[A")
          print('Node', self.id, 'waiting for message. Elapsed time:', str(round(time.time()-start_time)) + 's')
          continue

    # Transform to bundle structure
    recv_bundle = bundle.to_bundle(recv_bundle.decode())

    # Check destination
    if (recv_bundle.get_dest() == self.id):
      # If it is for this node, print message
      print('Mensaje recibido:', recv_bundle.get_message())
      return 0

    # Calculate how many seconds have passed since the start of the function
    # specially because of the while True loop
    end_time = time.time()
    current_time += (end_time - start_time)

    # If it is for other node, forward it
    return self.add_to_queue(recv_bundle, current_time)



class bundle:
  # initialize bundle with all its contents
  def __init__(self, message, src, dest, size='00000000',p=0, crit=False, cust=False, frag=True, deadline=0):
    self.message = message    # The message contained in this bundle
    self.source = src         # Source node of the bundle
    self.destination = dest   # Destination node of the bundle
    self.size = size          # Size will always be 8 bytes, for simplicity
    self.priority = p         # The priority of the bundle
    self.critical = crit      # Whether it is critical (must transmit to all possible nodes)
    self.custody = cust       # Custody request flag (if custody of the bundle was requested)
    self.fragment = frag      # Fragmentation authorized flag
    self.deadline = deadline  # TTL in sec (0 means infinite)
    self.route = None         # For checking if it has an assigned route
    self.next_hop = None      # For using the route assigned

    if (self.size == '00000000'): self.compute_size() # Size of the bundle in bytes

  # Pass to string
  def __str__(self):
    crit = '1' if self.critical else '0'
    cust = '1' if self.custody else '0'
    frag = '1' if self.fragment else '0'
    return self.source + '|||' + self.destination + '|||' + self.size + '|||' + str(self.priority) + '|||' + crit + '|||' \
      + cust + '|||' + frag + '|||' + str(self.deadline) + '|||' + self.message + '|||' + str(self.route) + '|||' + str(self.next_hop)

  # Back from string to bundle
  @staticmethod
  def to_bundle(string):
    str_splitted = string.split('|||')
    source, destination, size, priority, critical, custody, fragment, deadline, message = str_splitted[0:9]
    new_bundle = bundle(message, source, destination, size=size, p=priority, crit=critical, cust=custody, frag=fragment, deadline=deadline)
    if (len(str_splitted) >= 10):
      new_bundle.set_route(ast.literal_eval(str_splitted[9]))
    return new_bundle

  # Get message of the bundle
  def get_message(self):
    return self.message

  # Get destination of the bundle
  def get_dest(self):
    return self.destination

  # Get route of the bundle
  def get_route(self):
    return self.route

  # Get next_hop of the bundle
  def get_next_hop(self):
    return self.next_hop

  # Get size of the bundle
  def get_size(self):
    return int(self.size)

  # Get deadline of the bundle
  def get_deadline(self):
    return int(self.deadline)

  # Calculate the total size of the bundle in bytes
  def compute_size(self):
    new_size = str(len(str(self).encode()))
    while len(new_size) < 8:
      new_size = '0' + new_size
    self.size = new_size

  # Set a new route for the bundle
  def set_route(self, route):
    # A route dict is passed
    self.route = route
    self.set_next_hop(route['nextHop'])

  # Set the next hop for the route
  def set_next_hop(self, hop):
    self.next_hop = hop

  # TODO
  def fragment_message(self, max_size):
    pass