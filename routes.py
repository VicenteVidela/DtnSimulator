from graph import contact_graph

# A-A:0, A-B:1, A-C:2, A-E:3,
# B-C:4, C-D:5
# D-E:6, D-E:7, D-E:8
# E-E: 9

class routesA_E:
  def __init__(self) -> None:
    n_vertices = 10
    start_time = 0
    end_time = 60

    # Create the edges connecting the plan
    plan_edges = [
      [0,1], [0,2], [0,3],
      [1,4], [2,5], [4,5],
      [5,6], [5,7], [5,8],
      [3,9], [6,9], [7,9], [8,9]
    ]

    self.g = contact_graph(n_vertices, plan_edges)

    self.g.layout_delete(9)
    self.g.layout_append([0.0, 4.0])

    self.g.add_attributes('label', ['A-A', 'A-B', 'A-C', 'A-E', 'B-C', 'C-D', 'D-E', 'D-E', 'D-E', 'E-E'])
    self.g.add_attributes('rate', [1000, 1, 2, 1, 1, 3, 1, 2, 5, 1000])
    self.g.add_attributes('distance', [0, 1, 1, 1, 1, 1, 1, 1, 1, 0])
    self.g.add_attributes('start', [start_time, 0,  0, 10,  0,  0,  0, 30, 50, start_time])
    self.g.add_attributes('end',   [end_time,  60, 60, 20, 60, 30, 10, 40, 60, end_time])

    ## Visual stuff, not important for routes
    # self.g.add_visual_style('vertex_label', self.g.graph.vs['label'])
    # self.g.add_visual_style('vertex_size', 0.5)
    # self.g.graph.es[9]['curved'] = -1

    # self.g.plot()

    # Gets all routes from A to E in this plan
    # ordered by number of hops

addresses = {
  "A": 8881,
  "B": 8882,
  "C": 8883,
  "D": 8884,
  "E": 8885,
}