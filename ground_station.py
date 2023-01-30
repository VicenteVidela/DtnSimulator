import socket, sys, json, os
from bundle import bundle

# Get variables from console
try:
  _, time_graph = sys.argv
except ValueError:
  print('ValueError: 1 value needed from console: time graph file path')
  exit()

time_graph = os.path.dirname(os.path.realpath(__file__)) + '/time_graphs/' + time_graph

with open(time_graph) as f:
  # Check file extension
  if (time_graph.split('.')[-1] != 'json'):
    raise TypeError('File is not .json')
  # Read data and assign it to the satellite
  data = json.load(f)
  address_list = {}
  for address in data['addresses']:
    a = data['addresses'][address]
    address_list[address] = tuple(a)
f.close()

send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # for sending messages

while True:
  try:
    msg = input('Message to send: ')
    origin = input('First node that starts the transmission: ')
    destination = input('Destination node of the message: ')

    bndl = bundle(msg, origin, destination)

    message_to_send = str(bndl)
    print(message_to_send)

    send_socket.sendto(message_to_send.encode(), address_list[origin])

    print('Message:', msg, 'sent to', origin, 'with destination', destination)
  except KeyboardInterrupt:
    print('\nProgram Finished')
    break