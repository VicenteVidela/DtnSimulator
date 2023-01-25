import igraph as ig
import matplotlib.pyplot as plt

class graph:
  """
  A class for representing a simple graph, with a time associated to it
  """

  def __init__(self, t : float, n_vertices : int, edges : list = None, layout : str = 'rt') -> None:
    """
    A class for representing a time evolving graph of satellite
    nodes, as they change over time. This is only for one instance of time

    Parameters
    ----------
    t : float
      To what time this graph corresponds
    n_vertices : int
      Number of vertices of the graphs, which is the number of satellites
    edges : list
      List that contains the edges of the graph, the connections between
      satellites in time=t
    layour : str
      Layout algorithm to use for drawing the graph. Only used if graph is drawn
    """
    self.t = t
    self.n_vertices = n_vertices    # Number of vertices of the graph
    self.graph = ig.Graph(n=n_vertices, edges=edges, directed=True)   # The graph itself is created
    self.layout = self.graph.layout(layout)   # The layour for drawing
    self.visual_style = {}

  def get_t(self):
    return self.t

  def add_vertex_attributes(self, attr_name : str, attr : any) -> None:
    """
    Add a new attribute to the graph vertices
    """
    self.graph.vs[attr_name] = attr

  def add_edge_attributes(self, attr_name : str, attr : any) -> None:
    """
    Add a new attribute to the graph edges
    """
    self.graph.es[attr_name] = attr


class time_evolving_graph:
  """
  A class for representing a time evolving graph of satellite
  nodes, as they change over time. This is the complete list of graphs
  """
  def __init__(self, graphs : list) -> None:
    self.graphs = graphs
    self.T_list = []
    for g in self.graphs:
      self.T_list.append(g.get_t())

  def plot(self) -> None:
    n = len(self.graphs)
    fig, ax = plt.subplots(ncols=n, figsize=(n*7, 7))
    for i in range(n):
      g = self.graphs[i]
      ig.plot(g.graph, target=ax[i], layout=g.layout)
      ax[i].set_title('t=' + str(i))
    plt.show()

# Example
# n=3
# edges = [[0,1]]
# a = graph(0, n, edges)

# edges = [[0,1], [1,2]]
# b = graph(0, n, edges)

# edges = [[0,1], [1,2], [0,2]]
# c = graph(0, n, edges)

# gr = time_evolving_graph([a,b,c])
# gr.plot()