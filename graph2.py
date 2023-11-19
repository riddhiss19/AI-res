import networkx as nx

from heapq import heappush, heappop

# Function for best-first search 
def best_first_search(data, goal, start):
    
  # Create directed graph 
  graph = nx.DiGraph()

  # Add applicant nodes
  graph.add_node(start)


  for d in data:
    graph.add_node(d[0])
    graph.add_edge(start, d[0])
    graph[start][d]["weight"] = d[1]  

  

  # Print graph 
  print(graph.nodes())
  print(graph.edges())

  
  frontier = [(0, start)] # frontier is a priority queue
  explored = set()
  costs = {start: 0} # cost from start node
  
  while frontier:
    cost, node = heappop(frontier)
    
    if node in explored:
      continue

    explored.add(node)

    if node == goal:
      return cost

    for neighbor, edge_cost in graph[node].items():
      new_cost = cost + edge_cost['weight']
      
      if neighbor not in costs or new_cost < costs[neighbor]:
        costs[neighbor] = new_cost
        heappush(frontier, (new_cost, neighbor))
        
  return None # No path found
graph=''
start=''
best_first_search(graph, start, "Software Engineer")

