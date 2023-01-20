from __future__ import annotations
import ast

class bundle:
  """
  A class that describes a bundle to be sent in the DTN.
  """

  def __init__(self, message: str, src: str, dest: str, size: str ='00000000',p: int =0, crit: bool =False, cust: bool =False, frag: bool =True, deadline: int =0) -> None:
    """
    A class that describes a bundle to be sent in the DTN.

    Parameters
    ----------
    message : str
      The message of the bundle. What needs to be transfered.
    src : str
      Source node of the bundle.
    dest : str
      Destination of the bundle. Where it needs to arrive
    size : str
      Size of the complete bundle parsed as a string, in bytes.
      For simplicity, it always is 8 characters long.
    p : int
      Priority of the bundle. Higher number means better.
    crit : bool
      Critical flag. If true, bundle must be sent through all possible routes.
    cust : bool
      Custody flag. If true, it means the previous node is asking to exchange custody
      of the bundle.
    frag : bool
      Fragmentation flag. Determines whether the bundle can be fragmented or not.
    deadline : int
      TTL of the bundle. If this time is met, discard the bundle.
      0 means infinite.
    """
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

  def __str__(self) -> str:
    """
    Parse the bundle to string. The delimiter ||| was chosen.
    """
    crit = '1' if self.critical else '0'
    cust = '1' if self.custody else '0'
    frag = '1' if self.fragment else '0'
    return self.source + '|||' + self.destination + '|||' + self.size + '|||' + str(self.priority) + '|||' + crit + '|||' \
      + cust + '|||' + frag + '|||' + str(self.deadline) + '|||' + self.message + '|||' + str(self.route) + '|||' + str(self.next_hop)

  @staticmethod
  def to_bundle(string: str) -> bundle:
    """
    Take a bundle parsed as a string and transform it to a bundle.
    """
    str_splitted = string.split('|||')
    source, destination, size, priority, critical, custody, fragment, deadline, message = str_splitted[0:9]
    new_bundle = bundle(message, source, destination, size=size, p=priority, crit=critical, cust=custody, frag=fragment, deadline=deadline)
    if (len(str_splitted) >= 10):
      new_bundle.set_route(ast.literal_eval(str_splitted[9]))
    return new_bundle

  def get_message(self) -> str:
    """
    Message getter
    """
    return self.message

  def get_dest(self) -> str:
    """
    Destination getter
    """
    return self.destination

  def get_route(self) -> dict:
    """
    Route getter
    """
    return self.route

  def get_next_hop(self) -> str:
    """
    Next hop getter
    """
    return self.next_hop

  def get_size(self) -> int:
    """
    Size getter
    """
    return int(self.size)

  def get_deadline(self) -> int:
    """
    Deadline getter
    """
    return int(self.deadline)

  def compute_size(self) -> None:
    """
    Calculate the total size of the bundle, as a string, in bytes
    """
    new_size = str(len(str(self).encode()))
    while len(new_size) < 8:
      new_size = '0' + new_size
    self.size = new_size

  def set_route(self, route: dict) -> None:
    """
    Set a new route for the bundle
    """
    # A route dict is passed
    self.route = route
    self.set_next_hop(route['nextHop'])

  def set_next_hop(self, hop: str) -> None:
    """
    Set the next hop for the route
    """
    self.next_hop = hop

  # TODO
  def fragment_message(self, max_size):
    pass


