import igraph as ig
import matplotlib.pyplot as plt

class graph:
  """
  A class for representing a simple graph, with a time associated to it
  """

  def __init__(self, t : int, n_vertices : int, edges : list = None, layout : str = 'rt') -> None:
    """
    A class for representing a time evolving graph of satellite
    nodes, as they change over time. This is only for one instance of time

    Parameters
    ----------
    t : int
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
  def __init__(self, graphs : list, end_time : int) -> None:
    self.graphs = graphs
    self.T_list = []
    for g in self.graphs:
      self.T_list.append(g.get_t())
    self.T_list.append(end_time)

  def plot(self) -> None:
    n = len(self.graphs)
    fig, ax = plt.subplots(ncols=n, figsize=(n*7, 7))
    for i in range(n):
      g = self.graphs[i]
      ig.plot(g.graph, target=ax[i], layout=g.layout)
      ax[i].set_title('t=' + str(i))
    plt.show()

  def to_contact_graph(self) -> None:
    vertices = self.graphs[0].graph.vs
    contact_nodes = {}
    for v in range(len(vertices)):
      contacts = {}
      for g in self.graphs:
        contacts[g.t] = g.graph.get_all_simple_paths(v, cutoff=1)
      nodes = {}
      for t in contacts:
        for c in contacts[t]:
          to = c[-1]
          now_index = self.T_list.index(t)
          try:
            t_prev = nodes[to]['t_final']
            prev_index = self.T_list.index(t_prev)
            if (now_index==prev_index):
              nodes[to]['t_final'] = self.T_list[now_index+1]
            else:
              raise KeyError
          except KeyError:
            nodes[to] = {'t_ini': t, 't_final': self.T_list[now_index+1]}
      contact_nodes[v] = nodes

    print(contact_nodes)


# Example
n=3
edges = [[0,1]]
a = graph(0, n, edges)

edges = [[0,1], [1,2]]
b = graph(1, n, edges)

edges = [[0,1], [1,2], [0,2]]
c = graph(2, n, edges)

gr = time_evolving_graph([a,b,c], 3)
gr.to_contact_graph()