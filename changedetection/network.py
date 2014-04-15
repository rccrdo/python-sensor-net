# Copyright (c) 2011 Riccardo Lucchese, riccardo.lucchese at gmail.com
#
# This software is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
#    1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
#
#    2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
#
#    3. This notice may not be removed or altered from any source
#    distribution.

#import os
#import types
import numpy
import networkx
from agent import Agent


def find_nearest_node_to_point(G, x, y):
    pos = networkx.get_node_attributes(G, 'pos')
    ret = None
    cur_selection = None
    cur_dist2 = None
    for k, xy in pos.items():
        dist2 = (xy[0]- x)**2 + (xy[1]- y)**2
        
        if cur_selection == None or dist2 <= cur_dist2:
            cur_selection = k
            cur_dist2 = dist2

    return  cur_selection

def shift_graph_position(G, x, y):
    pos = networkx.get_node_attributes(G, 'pos')

    for (k, xy) in pos.items():
        xy[0] += x
        xy[1] += y

def circle_pos(n):
    import math
    radius = 0.4
    pos = {}
    for i in xrange(0,n):
        pos[i] = [radius*(1+math.cos(i*(2*math.pi/n))),radius*(1+math.sin(i*(2*math.pi/n)))]

    return pos


class Network():
    def __init__(self, M, D, N, barN, alpha_0, sigma, graph_basetype='grid2d:5x5', track_exact_size=False):
        assert isinstance(M, int) and M > 0
        assert isinstance(D, int) and D > 0
        assert isinstance(N, int) and N > 0
        assert isinstance(barN, int) and barN >= 1 and barN < N
        assert alpha_0 > 0. and alpha_0 < 1.
        assert sigma > 0. and sigma <= 1.

        print 'Distribution ~Uniform[0,1], M=%d D=%d N=%d, barN=%d, alpha_0=%.3f, sigma=%.2f' % (M, D, N, barN, alpha_0, sigma)
            
        self._time = 0
        self._M = M
        self._D = D
        self._N = N
        self._barN = barN
        self._alpha_0 = alpha_0
        self._sigma = sigma

        self._track_exact_size = track_exact_size

        # init graph state
        self._hubnodes = None
	self._graph = None
        self._agents = {}
        self._init_graph(graph_basetype)


    def _init_graph(self, basetype):
        if basetype[0:7] == 'grid2d:':
            side = int(basetype[7:])
            print 'Loading network graph from basetype grid2d with side', side
            self._graph = networkx.generators.classic.grid_2d_graph(side,side)
        elif basetype[0:9] == 'clusters:':
            cluster_size = int(basetype[9:])
            print 'Loading network graph from basetype clusters with size', cluster_size
            
            #
            #           cluster 1 
            #         /         \
            #   cluster 2 --- cluster3
            #
            conn_radius = 0.3
#            cluster1 = networkx.random_geometric_graph(cluster_size, conn_radius)
            cluster1 = networkx.complete_graph(cluster_size)
#            pos = networkx.spring_layout(cluster1, iterations=1000)
#            pos = networkx.spectral_layout(cluster1)
            pos = circle_pos(cluster_size)
            networkx.set_node_attributes(cluster1,'pos', pos)
            
#            cluster2 = networkx.random_geometric_graph(cluster_size, conn_radius)
            cluster2 = networkx.complete_graph(cluster_size)
#            pos = networkx.spring_layout(cluster2, iterations=1000)
#            pos = networkx.spectral_layout(cluster2)
            pos = circle_pos(cluster_size)
            networkx.set_node_attributes(cluster2,'pos', pos)

            relabel_map = dict(zip(range(0,cluster_size),range(cluster_size, cluster_size*2)))
            cluster2 = networkx.relabel_nodes(cluster2, relabel_map)
            
#            cluster3 = networkx.random_geometric_graph(cluster_size, conn_radius)
            cluster3 = networkx.complete_graph(cluster_size)
#            pos = networkx.spring_layout(cluster3, iterations=1000)
#            pos = networkx.spectral_layout(cluster3)
            pos = circle_pos(cluster_size)
            networkx.set_node_attributes(cluster3,'pos', pos)

            relabel_map = dict(zip(range(0,cluster_size),range(cluster_size*2, cluster_size*3)))
            cluster3 = networkx.relabel_nodes(cluster3, relabel_map)

            hubnode1to2 = find_nearest_node_to_point(cluster1, 0.1, 0.)
            hubnode2to1 = find_nearest_node_to_point(cluster2, 0.9, 1.)
            hubnode2to3 = find_nearest_node_to_point(cluster2, 1., 0.5) 
            hubnode3to2 = find_nearest_node_to_point(cluster3, 0., 0.5) 
            hubnode3to1 = find_nearest_node_to_point(cluster3, 0.35, 1) 
            hubnode1to3 = find_nearest_node_to_point(cluster1, 0.9, 0.) 
            
            shift_graph_position(cluster1, 0.6, 1.)
            shift_graph_position(cluster3, 1.2, 0)

            self._hubnodes = [hubnode1to2, hubnode2to1, hubnode2to3, hubnode3to2, hubnode3to1, hubnode1to3]

            cluster_links = [(hubnode1to2,hubnode2to1), (hubnode2to3,hubnode3to2), (hubnode3to1,hubnode1to3)]

#            cluster1.add_nodes_from(cluster2)
 #           cluster1.add_nodes_from(cluster3)
  #          cluster1.add_edges_from(cluster2.edges())
   #         cluster1.add_edges_from(cluster3.edges())
    #        cluster1.add_edges_from(cluster_links)
            cluster1 = networkx.union(cluster1, cluster2)
            cluster1 = networkx.union(cluster1, cluster3)
            cluster1.add_edges_from(cluster_links)
            self._graph = cluster1

            print "hubnodes : ", self._hubnodes
            print "cluster_links : ", cluster_links
            print "graph diameter : ", networkx.diameter(self._graph)

        if self._graph is None:
            return
            
	# init agents
        for n in self._graph.nodes():
            self._agents[n] = Agent(n, self._M, self._D, self._N, self._barN, self._alpha_0, self._sigma, self._track_exact_size)
            
    def get_time(self):
        return self._time

    def step(self):
        if self._graph is None:
            # empty graph: nothing to do
            return

	self._time += 1
        #print ' step', self._time

        # update network topology
        self._update_nodes_state()

        # do consensus
        # ! result does not depend on randomization of the order in `edges`
        for e in self._graph.edges():
            i = e[0]
            j = e[1]
            
            agent_i = self._agents[i]
            agent_j = self._agents[j]
            
            if not (agent_i.active() and agent_j.active()):
                continue

            istate = agent_i.get_state_at_epoch_start()
            jstate = agent_j.get_state_at_epoch_start()
            assert(istate.shape == jstate.shape)

            #print 'consensus ', e
            #print 'istate ', istate
            #print 'jstate ', jstate

            agent_i.do_pair_consensus(jstate)
            agent_j.do_pair_consensus(istate)

            if self._track_exact_size:
                seennodes_i = agent_i.get_seen_nodes_at_epoch_start()
                seennodes_j = agent_j.get_seen_nodes_at_epoch_start()

                agent_i.do_pair_seen_nodes_consensus(seennodes_j)
                agent_j.do_pair_seen_nodes_consensus(seennodes_i)

        # syncronize agents to `end of epoch`
        for agent in self._agents.values():
            agent.tick_epoch(self._time)



            
    def step_until(self, time):
        assert isinstance(time, int) and time >= 0
        
        while self._time < time:
            self.step()

    def get_component_info(self):
        info = [self._time]
        for component in self._graph_components:
            info.extend(component.get_info())
        
        return info
        
    def get_agent(self, nodeid):
        if nodeid in self._agents:
            return self._agents[nodeid]
        

    def _update_nodes_state(self):
        
        # kill hub
        if self._time == 30:
            self._agents[self._hubnodes[0]].sleep() 

            for e in self._graph.edges():
                n1 = e[0]
                n2 = e[1]
                if n1== self._hubnodes[0] or n2 == self._hubnodes[0]:
                    self._graph.remove_edge(*e)
        
        return


        # kill edges
        if self._time == 30:
            for e in self._graph.edges():
                n1 = e[0]
                n2 = e[1]
                if n1[1] == n2[1] and n1[1] > 1 and \
                   (((n1[0] %2 > 0) and (n1[0] == n2[0] -1)) or ((n2[0] %2 > 0) and (n1[0] == n2[0] +1))):
                    self._graph.remove_edge(*e)
        
        return
    
    
   
        # punch hole 2
        if self._time % 30 == 0:
            idx = self._time / 30
            if idx % 2:
                for key in self._agents.keys():
                    lower_lim = 4- idx /2 
                    upper_lim = 5+ idx /2
                       
	            if key[0] >= lower_lim and key[0] <= upper_lim and key[1] >= lower_lim and key[1] <= upper_lim:
	                self._agents[key].sleep()        
            else:
                for key in self._agents.keys():
                    lower_lim = 4- (idx-1) /2 
                    upper_lim = 5+ (idx-1) /2
                       
	            if key[0] >= lower_lim and key[0] <= upper_lim and key[1] >= lower_lim and key[1] <= upper_lim:
	                self._agents[key].wake()        

        return


        # noise
        if self._time >= 1:
            for key in self._agents.keys():

                if self._agents[key].active():
                    if numpy.random.binomial(1,0.01):
                        self._agents[key].sleep()
                else:
                    if numpy.random.binomial(1,0.04):
                        self._agents[key].wake()

        return

    
        # steps 01: uccidi nodi su fasce (-> epoch 420)
        if self._time % 30 == 0:
            idx = self._time / 30
            if idx % 2:
                for key in self._agents.keys():
                    if key[0] + key[1] >= 14 - idx/2:
                        self._agents[key].sleep()
            else:
                for key in self._agents.keys():
                    if key[0] + key[1] >= 14 - (idx-1)/2:
                        self._agents[key].wake()



        return


        # punch hole 1
        if self._time == 25:
            for key in self._agents.keys():
                if key[0] >= 2 and key[0] < 9 and key[1] >= 2 and key[1] < 9:
                    self._agents[key].sleep()        
        
        return

      

       


    def get_graph(self):
        return self._graph

    def get_agents(self):
        return self._agents

