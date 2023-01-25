import igraph as ig
import matplotlib.pyplot as plt

class contact_graph:
  """
  A class for representing a contact graph, which is a model
  that visualizes the contacts between two nodes in a DTN and
  the routes between them.
  """

  def __init__(self, n_vertices : int, edges : list = None, layout : str = 'rt'):
    """
    A class for representing a contact graph, which is a model
    that visualizes the contacts between two nodes in a DTN and
    the routes between them.

    Parameters
    ----------
    n_vertices : int
      Number of vertices of the graph, which translates into number of
      contacts in the contact plan plus the root and terminal contact
    edges : list
      List that contains the edges of the graph. These represent the time
      between two contacts
    layour : str
      Layout algorithm to use for drawing the graph. Only used if graph is drawn
    """
    self.n_vertices = n_vertices    # Number of vertices of the graph
    self.graph = ig.Graph(n=n_vertices, edges=edges, directed=True)   # The graph itself is created
    self.layout = self.graph.layout(layout)   # The layour for drawing
    self.visual_style = {}          # Dictionary for storing the visual style options for drawing

  def layout_delete(self, idx : int) -> None:
    """
    For deleting and item from the layout by its index
    """
    self.layout.__delitem__(idx)

  def layout_append(self, node : list) -> None:
    """
    Append a new item to the layout at the end of the list
    """
    self.layout.append(node)

  def add_attributes(self, attr_name : str, attr : any) -> None:
    """
    Add a new attribute to the graph vertices
    str | int | float | list
    """
    self.graph.vs[attr_name] = attr

  def add_visual_style(self, attr_name : str, attr : any) -> None:
    """
    Add a new attribute to the visual style of the graph
    Only used when plotting
    """
    self.visual_style[attr_name] = attr

  def plot(self) -> None:
    """
    Plot the graph with the layout and visual style given
    """
    fig, ax = plt.subplots(figsize=(7, 7))
    self.visual_style['layout'] = self.layout
    self.visual_style['target'] = ax
    ig.plot(self.graph, **self.visual_style)
    plt.show()

  def get_all_routes(self) -> list:
    """
    Find all routes from root node to terminal.
    It gets all possible paths from the starting node to the
    finishing one, sorts them by length and calculates all
    their corresponding attributes
    """
    # Get all paths from start to finish
    paths = self.graph.get_all_simple_paths(0, self.n_vertices-1)
    # Sort them by length (number of hops)
    paths.sort(key=len)

    routes = []

    # Go through all paths and create the routes from it
    for p in paths:
      distance = 0
      rate = 10000
      route = {}
      # The route will be a dictionary of each contact with it's time window
      for node_idx in p[1:-1]:
        # Add to the total distance
        distance += self.graph.vs[node_idx]['distance']
        # The rate is the minimum rate of all the contacts
        rate = min(rate, self.graph.vs[node_idx]['rate'] * (self.graph.vs[node_idx]['end'] - self.graph.vs[node_idx]['start']))
        # Add to route dictionary
        route[self.graph.vs[node_idx]['label']] = [self.graph.vs[node_idx]['start'], self.graph.vs[node_idx]['end']]
      # if it is a plausible route, add to list
      if (rate > 0):
        dict = {'route': route, 'distance': distance,'rate': rate}
        routes.append(dict)

    return routes



