from bundle import bundle
import socket, time

class travelling_bundle:
  """
  Class that simulates a bundle travelling through space.
  It receives the bundle, sleeps the distance in seconds
  and afterwards sends it to the destionation.
  """
  def __init__(self, bundle: bundle, distance : int, destination: tuple[str, int]) -> None:
    self.bundle = bundle    # The bundle to be sent
    self.timer = distance   # How much time it needs to travel
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # The socket to send the bundle
    self.destination = destination

  def send(self) -> None:
    """
    Send the associated bundle to the next hop
    """
    self.socket.sendto(str(self.bundle).encode(), self.destination)
    print('Bundle arriving to node:', self.bundle.get_next_hop(), '\n')


# Create the socket for space, which will receive the bundles
# and store them before passing on.
# The timeout is used for updating the bundle timers, one second at a time
spaceSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
spaceSocket.settimeout(1)
spaceAddress = ('127.0.0.1', 8080)
spaceSocket.bind(spaceAddress)

# List of bundles that are still waiting
bundle_list = []

start_time = time.time()

try:
  print('Space running. Elapsed time:', str(round(time.time()-start_time)) + 's')
  while True:
    try:
      # Receive bundles
      bundle_recv, _ = spaceSocket.recvfrom(10000)
      bundle_recv, destination = bundle_recv.decode().split('###')
      bundle_recv = bundle.to_bundle(bundle_recv)
      # Get the distance between the nodes
      distance = bundle_recv.route['distance']
      # Get the destination address
      destination_split = destination.split(',')
      destination = (destination_split[0][2:-1], int(destination_split[1][1:-1]))

      # Create a new instance that will wait and add it to the list
      new_bundle = travelling_bundle(bundle_recv, distance, destination)
      bundle_list.append(new_bundle)
    except TimeoutError:
      # Every second, see if bundles must be sent
      for b in bundle_list:
        if (b.timer <= 0):
          # If timer expired, send the bundle and remove from list
          b.send()
          bundle_list.remove(b)
        else:
          # Else, decrease timer in one second
          b.timer -= 1

      print ("\033[A\033[A")
      print('Space running. Elapsed time:', str(round(time.time()-start_time)) + 's')
      continue

except KeyboardInterrupt:
    print('Program finished.')