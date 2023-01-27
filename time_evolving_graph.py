import igraph as ig
import matplotlib.pyplot as plt
from contact_graph import contact_graph

class time_evolving_graph:
  """
  A class for representing a time evolving graph of satellite
  nodes, as they change over time
  """
  def __init__(self, labels: dict, edges: dict, start_time: int, end_time: int, layout: str = 'rt'):
    """
    A class for representing a time evolving graph of satellite
  nodes, as they change over time

    Parameters
    ----------
    n_vertices : int
      Number of vertices of the graph, which translates into number of
      contacts in the contact plan plus the root and terminal contact
    edges : list
      Dictionary that contains the edges of the graph. The key is the pair
      [start_node, end_node] and the values are the starting time and ending time
    start_time : int
      The start time for the graph
    end_time : int
      The end time for the graph
    layour : str
      Layout algorithm to use for drawing the graph. Only used if graph is drawn
    """
    self.labels = labels              # Label for each node number
    self.n_vertices = len(labels)     # Number of vertices of the graph
    self.graph = ig.Graph(n=self.n_vertices, edges=[d['contact'] for d in edges], directed=True)   # The graph itself is created
    self.graph.es['contact']=[d['contact'] for d in edges]
    self.graph.es['start_time'] = [d['start_time'] for d in edges]
    self.graph.es['end_time'] = [d['end_time'] for d in edges]
    self.graph.es['distance'] = [d['distance'] for d in edges]
    self.graph.es['rate'] = [d['rate'] for d in edges]
    self.start_time = start_time
    self.end_time = end_time
    self.layout = self.graph.layout(layout)   # The layour for drawing
    self.visual_style = {}          # Dictionary for storing the visual style options for drawing

  def plot(self, curved_edges : bool | list = False) -> None:
    """
    Plot the graph with the layout defined at the start.
    It needs a list of the edges that need to be curved, for avoiding others
    """
    fig, ax = plt.subplots(figsize=(7, 7))
    ig.plot(self.graph, target=ax, layout=self.layout, edge_curved=curved_edges,
      edge_label=['[{start},{end}]'.format(start=d['start_time'], end=d['end_time']) for d in edges],
      vertex_label=self.labels.values())
    plt.show()

  def to_contact_graph(self, origin: int, destination: int) -> contact_graph:
    """
    Transforms this graph into a contact graph from the desired origin to destination
    """
    if (origin == destination):
      raise ValueError("Origin same as destination")
    # Gets all paths from origin node to destination
    paths = self.graph.get_all_simple_paths(origin, destination)
    if (not paths):
      print('No paths from origin to destination')
      return None
    contacts = {}   # Dictionary for storing all contacts for each node
    # Goes through all the paths found
    for p in paths:
      n = len(p)
      # For each path, go through each node it visits
      for i in range(n-1):
        node = p[i]
        # And for each node, get all edges from it to the next node on the path
        edges = self.graph.es.select(_source_eq = node, _target_eq = p[i+1])
        # Get the array of contacts for this node
        try:
          c = contacts[node]
        except KeyError:
          c = []  # If it doesn't exists, create it
        for e in edges:
          # Append all edges, which are the contacts between this and the next node in the path
          c.append(e.attributes())
        contacts[node] = c

    ## First, the vertices for the contact graph are calculated

    # Start the variables for the contact graph,
    # with the values for the origin node
    n_vertices = 0
    contact_nodes = {n_vertices : [origin, origin]}
    start_times = [self.start_time]
    end_times = [self.end_time]
    distances = [0]
    labels = [self.labels[origin] + '-' + self.labels[origin]]
    rates = [100000]  # Big number for rate for first contact, in theory is infinite from A to A
    # Go through all nodes
    for node in contacts:
      # For each node, go through all contacts of it
      for c in contacts[node]:
        n_vertices += 1                         # Add to the number of vertices for the contact graph
        contact = c['contact']
        contact_nodes[n_vertices] = (contact)   # Assign the next index of the graph to this contact
        start_times.append(c['start_time'])     # Add the properties
        end_times.append(c['end_time'])
        distances.append(c['distance'])
        labels.append(self.labels[contact[0]] + '-' + self.labels[contact[1]])
        rates.append(c['rate'])
    # In the end, add the final contact destination-destination
    n_vertices += 1
    contact_nodes[n_vertices] = ([destination, destination])
    start_times.append(self.start_time)
    end_times.append(self.end_time)
    distances.append(0)
    labels.append(self.labels[destination] + '-' + self.labels[destination])
    rates.append(100000)

    ## Next, we get the edges connecting each vertex
    edges = []
    for c in contact_nodes:
      destination_node = contact_nodes[c][1]
      # Check all other vertices that should be connected to this contact
      connections = [k for k,v in contact_nodes.items() if v[0]==destination_node]
      for next_node in connections:
        if c!=next_node:
          edges.append([c, next_node])

    # With edges and vertices calculated,
    # and each with its properties,
    # Create the contact graph
    g = contact_graph(n_vertices+1, edges) # Since we used n_vertices as an index starting from 0, we need to add one more to the count
    g.add_attributes('start', start_times)
    g.add_attributes('end', end_times)
    g.add_attributes('distance', distances)
    g.add_attributes('label', labels)
    g.add_attributes('rate', rates)

    # Returns the contact graph calculated
    return g


## Example
# Nodes
labels = {0: 'A', 1: 'B', 2: 'C'}
# Connections
edges = [
  {'contact': [0,1], 'start_time': 0, 'end_time': 1, 'distance': 1, 'rate': 2},
  {'contact': [0,1], 'start_time': 2, 'end_time': 3, 'distance': 2, 'rate': 3},
  {'contact': [1,2], 'start_time': 1, 'end_time': 3, 'distance': 1, 'rate': 1},
  {'contact': [0,2], 'start_time': 2, 'end_time': 3, 'distance': 1, 'rate': 1},
  {'contact': [2,0], 'start_time': 0, 'end_time': 3, 'distance': 1, 'rate': 2},
]

# Create time graph
a = time_evolving_graph(labels, edges, 0, 3)
# Plot it
a.plot(curved_edges=[False, True, False, False, True])

# Convert to contact graph
g = a.to_contact_graph(2,0)
# Get the routes and plot the graph
print(g.get_routes())
g.plot()
