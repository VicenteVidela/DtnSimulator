from graph import contact_graph

# A-A:0, A-B:1, A-C:2, A-E:3,
# B-C:4, C-D:5
# D-E:6, D-E:7, D-E:8
# E-E: 9

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

g = contact_graph(n_vertices, plan_edges)

g.layout_delete(9)
g.layout_append([0.0, 4.0])

g.add_attributes('label', ['A-A', 'A-B', 'A-C', 'A-E', 'B-C', 'C-D', 'D-E', 'D-E', 'D-E', 'E-E'])
g.add_attributes('rate', [1000, 1, 2, 1, 1, 3, 1, 2, 5, 1000])
g.add_attributes('distance', [0, 1, 1, 1, 1, 1, 1, 1, 1, 0])
g.add_attributes('start', [start_time, 0,  0, 10,  0,  0,  0, 30, 50, start_time])
g.add_attributes('end',   [end_time,  60, 60, 20, 60, 30, 10, 40, 60, end_time])

## Visual stuff, not important for routes
# g.add_visual_style('vertex_label', g.graph.vs['label'])
# g.add_visual_style('vertex_size', 0.5)
# g.graph.es[9]['curved'] = -1

# g.plot()

# Gets all routes from A to E in this plan
# ordered by number of hops
routes = g.get_routes()

print(routes)