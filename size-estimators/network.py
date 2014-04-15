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

import os
import types
import numpy
import networkx
import fractions
from agent import Agent
from util import *
from connectedcomponent import *
from consensus import *
from estimators import *

_DISTRIBUTIONS = ('uniform', 'normal', 'exponential', 'bernoulli')
_GRAPH_BASETYPES = ('grid2d:2x2', 'grid2d:5x5')


class Network():
    def __init__(self, graph_basetype='grid2d:5x5', graph_history_src=None, consensus_step='inf', distribution='uniform', M=5, resampling_steps=0, Smax=0):
#        assert graph_basetype in _GRAPH_BASETYPES
        assert consensus_step in CONSENSUS_STEPS
        assert distribution in _DISTRIBUTIONS
        assert isinstance(M, int) and M > 0
        assert isinstance(resampling_steps, int) and resampling_steps >= 0

        if distribution == 'uniform':
            print 'Distribution ~Uniform[0,1]'
	    self._sample_func = lambda : numpy.random.uniform(1., 0., M)
            self._estimator_func = lambda local_maxs : size_estimator_max_uniform(local_maxs, M)
            self._consensus_op = 'max'
        elif distribution == 'normal':
            print 'Distribution ~Normal(0,1)'
	    self._sample_func = lambda : numpy.random.normal(0., 1., M)
            self._estimator_func = lambda local_avgs : size_estimator_avg_normal(local_avgs, M)
            self._consensus_op = 'avg'
        elif distribution == 'bernoulli':
            print 'Distribution ~Bernoulli(1/2)'
	    #self._sample_func = lambda : random_vector_bernoulli_use_fractions(M, 0.5)
	    self._sample_func = lambda : random_vector_bernoulli(M, 0.5)
            self._estimator_func = lambda local_avgs : size_estimator_avg_bernoulli3(local_avgs)
            self._consensus_op = 'avg-use-fractions'
        elif distribution == 'exponential':
            print 'Distribution ~Exponential(1)'
	    self._sample_func = lambda : numpy.random.exponential(1., M)
            self._estimator_func = lambda local_mins : size_estimator_min_exponential(local_mins, M)
            self._consensus_op = 'min'
            
        self._consensus_step = consensus_step
        self._resampling_steps = resampling_steps
        self._time = 0

        # init graph state
	self._graph = None
        self._graph_components = []
	self._graph_history = []
        self._active_agents = {}
        self._sleeping_agents = {}
        self._dead_agents = {}

        # create the graph from a history file or a base-type
	if graph_history_src:
            self._load_graph_history(graph_history_src)
        else:
            self._graph_from_basetype(graph_basetype)

        # no history or base-type where specified: default to a static 'grid2d:5x5'
        if not self._graph:
            self._graph = self._graph_from_basetype('grid2d:5x5')

    def _load_graph_history(self, src):
        print 'Loading network history from \'%s\'' % src
        #if not os.path.isfile(srcfile):
        # 	return
        
        # create an empty graph
	self._graph = networkx.Graph()
	
        # sort history by time
        simple_history = [(10, {'add_nodes' : (6,7), 'add_edges' : ((6,5),) }), (0, { 'add_nodes' : (0,1,2,3,4,5), 'add_edges' : ((0,1),(1,2)) }), (11, {'add_edges' : ((6,7),) })]
        self._graph_history = sorted(simple_history, key = lambda entry : entry[0])
        self._update_from_history()

    def _graph_from_basetype(self, basetype):
        print 'Loading network from basetype \'%s\'' % basetype
        if basetype == 'grid2d:5x5':
            self._graph = networkx.generators.classic.grid_2d_graph(5,5)
        elif basetype == 'grid2d:2x2':
            self._graph = networkx.generators.classic.grid_2d_graph(2,2)
        elif basetype[0:7] == 'grid2d:':
            side = int(basetype[7:])
            self._graph = networkx.generators.classic.grid_2d_graph(side,side)            
            
	# init each node local state
        if self._graph:
            for _id in self._graph.nodes():
                self._init_agent(_id)
            
	    # init the list of (connected) components
            self._graph_components = self._graph_connected_components(self._graph)

    def _init_agent(self, _id):
        assert _id is not None
        assert not self._active_agents.has_key(_id)
        assert not self._dead_agents.has_key(_id)
        self._active_agents[_id] = Agent(_id, self._time, self._sample_func, self._estimator_func)

    def _graph_connected_components(self, graph):
        assert graph
        components = []
        for subgraph in networkx.algorithms.components.connected.connected_component_subgraphs(graph):
            components.append(ConnectedComponent(self._consensus_step, self._consensus_op, subgraph.nodes(), subgraph.edges()))
        return components

    def step(self):
	self._time += 1
        print ' step', self._time

        # update network topology
        self._update_from_history()

	# resample every `resampling_steps`
	if self._resampling_steps > 0:
            epoch_vanished = (self._time % self._resampling_steps == 0)
	    if epoch_vanished:
                print '   resampling !'
                for agent in self._active_agents.values():
                    agent.resample()

	# do consensus for each connected component
        for component in self._graph_components:
            component.step(self._active_agents, self._time)
            
    def step_until(self, time):
        assert isinstance(time, int) and time >= 0

        while self._time < time:
            self.step()

    def get_component_info(self):
        info = [self._time]
        for component in self._graph_components:
            info.extend(component.get_info())
        
        return info

    def get_asymptotic_estimate(self):
        assert len(self._graph_components) == 1
        
        comp = self._graph_components[0]
        assert len(comp.get_agent_ids()) == len(self._active_agents)
        
        asyn_state = consensus_asymptotic_avg(self._active_agents, self._graph_components[0].get_agent_ids())
        #print "asyn state = ", asyn_state
        return self._estimator_func(asyn_state)


    def _update_from_history(self):
        if not len(self._graph_history):
            return

	update_entry = self._graph_history[0]
	update_time = update_entry[0]
	update_data = update_entry[1]
        if update_time <= self._time:
            self._graph_history.pop(0)
            del_nodes_data = None
            del_edges_data = None
	    add_nodes_data = None
            add_edges_data = None
            
            if update_data.has_key('del_nodes'):
                del_nodes_data = update_data['del_nodes']
            if update_data.has_key('del_edges'):
                del_edges_data = update_data['del_edges']
            if update_data.has_key('add_nodes'):
                add_nodes_data = update_data['add_nodes']
            if update_data.has_key('add_edges'):
                add_edges_data = update_data['add_edges']

            if del_nodes_data or del_edges_data:
                comps = self._graph_components
        
                # delete edges
                if del_edges_data is not None:
                    for edge in del_edges_data:
                        self._graph.remove_edge(*edge) 
                # delete nodes
                if del_nodes_data is not None:
                    for _id in del_nodes_data:
                        self._graph.remove_node(_id) 
                        assert not self._dead_agents.has_key(_id)
                        self._dead_agents[_id] = self._active_agents.pop(_id)

                new_comps = self._graph_connected_components(self._graph)
                new_comps_done = [False]*len(new_comps)

                pending_new_comps = []
                comps_to_be_discarded_by_idx = []
                for i in range(0,len(comps)):
                    candidates = []	# for split
                    old_comp = comps[i]
                    for j in range(0,len(new_comps)):
                        if not new_comps_done[j]:
                            new_comp = new_comps[j]
                            intersection_size = len(old_comp.intersect(new_comp))
                            if intersection_size > 0:
                                candidates.append((j, intersection_size))
    
                    if len(candidates):
                        selected = 0
                        selected_size = candidates[selected][1]
                        for (j,size) in candidates[1:]:
                            if selected_size < size:
                                selected = j
                                selected_size = size
                
                        # select continuation
                        old_comp.update_agent_ids(new_comps[candidates[selected][0]].get_agent_ids())
                        new_comps_done[selected] = True
                
                        # create new components to be appended
                        for (j,size) in candidates:
                            if j != candidates[selected][0]:
                                pending_new_comps.append(ConnectedComponent(self._consensus_step, self._consensus_op, new_comps[j].get_agent_ids(), new_comps[j].get_agent_ids()))
                    else:
                        # all nodes died
                        comps_to_be_discarded_by_idx.append(i)

                # pop comps that disappeared
                for i in reversed(comps_to_be_discarded_by_idx):
                    comps.pop(i)

                # append split componentes that were not selected as continuations
                if len(pending_new_comps):
                    comps.extend(pending_new_comps)

                self._graph_components = comps

            if add_nodes_data or add_edges_data:
                comps = self._graph_components
        
                # add nodes
                if add_nodes_data is not None:
                    for _id in add_nodes_data:
                        assert not self._graph.node.has_key(_id)
                        self._graph.add_node(_id) 
                        #print 'adding node to graph with id', _id
	                self._init_agent(_id)

                # add edges
                if add_edges_data is not None:
                    for edge in add_edges_data:
                        self._graph.add_edge(*edge) 
        
                new_comps = self._graph_connected_components(self._graph)
                comps_done = [False]*len(comps)
                pending_new_comps = []
                comps_to_be_discarded_by_idx = []
                for i in range(0, len(new_comps)):
                    candidates = []	# for merge
                    new_comp = new_comps[i]
                    #print '  i', i
                    #print '    new_comps[i]', new_comp.get_agent_ids()
                    for j in range(0, len(comps)):
                        old_comp = comps[j]
                        #print '    j', j
                        #print '      comps[j]', old_comp.get_agent_ids()
                        if not comps_done[j]:
                            if len(old_comp.intersect(new_comp)) > 0:
                                candidates.append(j)
                          #      print '        intersection!'
                        #else:
                         #       print '        skipping j-th old_comp'
                

                    if len(candidates) > 0:
                        #print "    candidates", candidates
                        selected = 0
                        selected_size = comps[selected].size()
                        for k in candidates[1:]:
                            candidate_size = comps[k].size()
                            if selected_size < candidate_size:
                                selected = k
                                selected_size = candidate_size

                        # select continuation
                        comps[candidates[selected]].update_agent_ids(new_comp.get_agent_ids())
                
                        for k in candidates:
                            comps_done[k] = True
                            if k != candidates[selected]:
                                #print '        dicarding', k
                                comps_to_be_discarded_by_idx.append(k)
                                # release the subgraph relative to these candidates and their time trajectory
                                # save it somewhere to plot it later
                    else:
                        # all new nodes
                        # create a new subgraph relative to new_ids and a new time trajectory
                        pending_new_comps.append(new_comp)
                        #print '        appending', new_comp.get_agent_ids()

                        
                # pop comps that were merged but were not selected as continuations
	        for i in reversed(comps_to_be_discarded_by_idx):
                    #print '      popping', i
	            comps.pop(i)

                # append split componentes that were not selected as continuations
                comps.extend(pending_new_comps)
        
                self._graph_components = comps
            
            
            # consistency check
            size = 0
            print '   graph has been updated:'
            for comp in self._graph_components:
                print '     component of size %d' % comp.size(), 'contains', comp.get_agent_ids()
                size += comp.size()
            #print '    nr nodes', len(self._graph.nodes())
            #print '    components size', size
            assert len(self._active_agents) == len(self._graph.nodes())
            assert size == len(self._graph.nodes())

       
#    def get_trajectories(self):
#        traj = self._active_agents.copy()
#        traj.update(self._dead_agents)
#        return traj

