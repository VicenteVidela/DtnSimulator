import socket, time, json
from bundle import bundle

spaceAddress = ('127.0.0.1', 8080)

class DTNnode:
  """
  A class for creating a Delay-Tolerant Network Node,
  made for satellite networks in mind.
  """

  def __init__(self, id: str) -> None:
    """
    A class for creating a Delay-Tolerant Network Node,
    made for satellite networks in mind.

    Parameters
    ----------
    id : str
      Unique identifier of the node
    """

    self.id = id              # Id for identifying the node
    self.socketRecv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # sockets for receiving and
    self.socketSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # sending messages
    self.address = None       # Satellite node
    self.contact_plan = None  # Contact plan
    self.address_list = {}    # Dictionary of the different addresses of the other nodes
    self.route_list = None    # List of route lists for the other nodes
    self.send_queue = []      # List for storing all the messages that have to be sent when available

  def settimeout(self, timeout: float) -> None:
    """
    Sets the timeout of the receiving socket of the node
    """
    self.socketRecv.settimeout(timeout)

  def bind(self, address: tuple[str, int]) -> None:
    """
    Bind receiving socket to the address
    """
    self.address = address
    self.socketRecv.bind(self.address)

  def get_address(self, id: str) -> tuple[str, int]:
    """
    Get address corresponding to node id
    """
    # Since all is run on localhost for now, only the ports are unique per node
    return ('127.0.0.1', self.address_list[id])

  def update_contact_plan(self, new_plan_directory: str, compute_routes: bool = False) -> None:
    """
    Update contact plan with new one and compute the route lists if necessary.
    Contact plan directory is required.
    """
    # Open file and read it
    with open(new_plan_directory) as f:
      # Check file extension
      if (new_plan_directory.split('.')[-1] != 'txt'):
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

  def update_route_list(self, new_list_directory: str) -> None:
    """
    Update route list with a new one.
    Route list directory is required.
    """
    # Open file and read it
    with open(new_list_directory) as f:
      # Check file extension
      if (new_list_directory.split('.')[-1] != 'json'):
        raise TypeError('File is not .json')
      data = json.load(f)
      self.route_list = data
    f.close()

  def check_routes(self, bundle: bundle, current_time: float) -> bundle:
    """
    Check possible routes for a bundle.
    Returns the bundle with updated route and/or next hop.
    """
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
        return bundle
      # Set the next hop for the bundle
      bundle.set_next_hop(route_splitted[i-1])

    return bundle

  def add_to_queue(self, bundle: bundle, current_time: float) -> None:
    """
    Add a bundle to send queue of the node
    """
    # If deadline already passed, discard it
    if (0 < bundle.get_deadline() <= current_time):
      print("Bundle deadline already passed, discarding.")
      return

    # Check routes for the bundle and return updated bundle
    updated_bundle = self.check_routes(bundle, current_time)

    # If a route was found, add it to queue
    if (updated_bundle.get_route() is not None):
      self.send_queue.append(updated_bundle)
      # Start sending queue
      return self.send_bundles_in_queue(current_time)
    else:
      #TODO Add to limbo
      pass

  def send_bundles_in_queue(self, current_time: float) -> float:
    delta_t = 0
    # When delta_t==0, send was succesful
    while (delta_t == 0):
      delta_t = self.send_first_in_queue(current_time)
      # If route is not yet available
      if (delta_t > 0):
        return delta_t
    return 0

  def send_first_in_queue(self, current_time: float) -> float:
    """
    Get the first bundle in queue and try to send it
    """
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
      return delta_time

    # Passed all checks, delete it from the list and send
    bundle_to_send = self.send_queue.pop(0)
    self.send(bundle_to_send)
    return 0

  def send(self, bundle: bundle) -> None:
    """
    Send a bundle forward to the next hop
    """
    self.send_to_space(bundle)
    print('Bundle forwarded to node:', bundle.get_next_hop())

  def send_to_space(self, bundle: bundle) -> None:
    """
    Send a bundle simulating the delay associated to the distance
    that must be traveled through space
    """
    dest = self.get_address(bundle.get_next_hop())
    self.socketSend.sendto((str(bundle) + '###' + str(dest)).encode(), spaceAddress)

  def recv(self, buff_size: int, current_time: float, alarm_on : bool = False, timer : int = 0) -> int:
    """
    Receives a bundle Then prints if it's destination was this node,
    or forward it through the appropiate route

    Return codes:
    - 0: Arrived to destination correctly or was forwarded to the next hop.
    - -1: Alarm expired, stop receiving and try to send bundles in queue.
    - >0: No route available for bundle, have to wait.
    """
    # For counting how many seconds have passed since the call of the function
    start_time = time.time()

    print('Node', self.id, 'waiting for message. Elapsed time: 0s')
    # Main cycle of receiving
    while True:
      try:
        # Before receiving, check every second if timer expired or not
        # This only applies if alarm_on is True
        if (alarm_on):
          if (timer <= 0):
            return -1
          timer -= self.socketRecv.gettimeout()

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
