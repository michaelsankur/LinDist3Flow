# Elaine Laguerta (github: @elaguerta)
# LBNL GIG
# File created: 20 August 2020
# Implement FBS to solve Power Flow for a radial distribution network.
import sys
from typing import Iterable, List, Dict
from . utils import init_from_dss
from . network import *

def fbs(dss_fp) -> None:
    network = init_from_dss(dss_fp)
    topo_order = topo_sort(network)
    solution = Solution()
    # while not converged
        # for node in topo_order:
            # forward sweep
        # check convergence
        # for node in reverse topo_order:
            # backward sweep
    # return Solution
    pass

def update(network: Network, source_node: Node, target_node: Node) -> None:
    pass

def topo_sort(network: Network) -> List:
    """
    Returns a list of Nodes in a topological order.
    Raises error if it finds a cycle
    Adapted from 'Algorithms' by Jeff Erickson, 1st ed 2019, Ch. 6.3, Figure 6.9,
    'Explicit topological sort': http://jeffe.cs.illinois.edu/teaching/algorithms/book/06-dfs.pdf
    """
    # store each node's status. 'New' means it has not been traversed,
    # 'Active' means it is being explored.
    clock = len(network.nodes) # countdown from total number of nodes.
    # clock will be used as an index to topo_order. the strategy is to insert
    # nodes in the topo_order array in reverse order of dfs finishing times.
    topo_order = [None] * clock # array to store topo order
    nodes = { node_name: 'new' for node_name in network.nodes.keys()} # initialize all nodes' statuses to 'New'

    # top level call to _topo_sort_dfs for each node
    #TODO: also return a list of connected commponents, in case we need to know
    #about isolated nodes or the network is a forest of trees
    for node_name,status in nodes.items():
        if status is 'new':
            clock = topo_sort_dfs(node_name, nodes, network.adj, clock, topo_order)
    return topo_order

def topo_sort_dfs(start_node:str, node_status: Dict[str,str], adj_matrix: Iterable, clock: int, topo_order: List) -> int:
    node_status[start_node] = 'active'
    for child in adj_matrix[start_node]:
        if node_status[child] is 'new':
            clock = topo_sort_dfs(child, node_status, adj_matrix, clock, topo_order)
        elif node_status[child] is 'active':
            raise ValueError('Network contains a cycle.')
    node_status[start_node] = 'finished'
    topo_order[clock-1] = start_node
    return clock - 1







