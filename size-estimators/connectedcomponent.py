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

import numpy
from consensus import *

CONSENSUS_STEPS = ('single','inf')
_CONSENSUS_OPS = ('min','max','avg','avg-use-fractions')

class ConnectedComponent():
    def __init__(self, consensus_step, consensus_op, agent_ids, edges):
        assert len(agent_ids)
        assert consensus_step in CONSENSUS_STEPS
        assert consensus_op in _CONSENSUS_OPS
 
        if consensus_step == 'inf':
            if consensus_op == 'min':
                self._consensus_func = lambda agents, ids : consensus_component_min(agents, ids)
            elif consensus_op == 'max':
                self._consensus_func = lambda agents, ids : consensus_component_max(agents, ids)
            elif consensus_op == 'avg':
                self._consensus_func = lambda agents, ids : consensus_component_avg(agents, ids)
            elif consensus_op == 'avg-use-fractions':
                self._consensus_func = lambda agents, ids : consensus_component_avg_use_fractions(agents, ids)
        elif consensus_step == 'single':
            if consensus_op == 'min':
                self._consensus_func = lambda agents_data, node_ids, graph_edges : consensus_min(agents_data, node_ids, graph_edges)
            elif consensus_op == 'max':
                self._consensus_func = lambda agents_data, node_ids, graph_edges : consensus_max(agents_data, node_ids, graph_edges)
            elif consensus_op == 'avg':
                self._consensus_func = lambda agents_data, node_ids, graph_edges : consensus_avg(agents_data, node_ids, graph_edges)
            elif consensus_op == 'avg-use-fractions':
#                self._consensus_func = lambda agents_data, node_ids, graph_edges : consensus_avg_use_fractions(agents_data, node_ids, graph_edges)
                self._consensus_func = lambda agents_data, node_ids, graph_edges : consensus_avg(agents_data, node_ids, graph_edges)
            else:
                assert 0
        
        self._consensus_step = consensus_step
        self._data = None
        
        self.update_topology(agent_ids, edges)
        
    def size(self):
        return len(self._ids)

    def _check_topology(self, ids, edges):
        print "\n --- warning, check_topology overridden ---\n"
        return

        assert ids
        assert len(ids)
        assert edges

	if len(edges) ==0:
	    assert len(ids)==1
	else:
            # the set of agents must contain all the ids
            # the set of edges is pointing to
            for e in edges:
                assert len(e)==2
                assert e[0] in ids
                assert e[1] in ids

            # all agents must have at least one edge on them
            for a in ids:
                found = False
                for e in edges:
                    if a == e[0] or a == e[1]:
                        found = True
                        continue
                assert found            
            
    def update_topology(self, ids, edges):
        self._check_topology(ids, edges)

        self._ids = ids
        self._edges = edges

    def get_agent_ids(self):
        return self._ids
        
    def get_edges(self):
        return self._edges

    def intersect(self, other_component):
        assert isinstance(other_component, ConnectedComponent)
        size = 0
        intersection = []
        for _id in other_component.get_agent_ids():
            if _id in self._ids:
                intersection.append(_id)
        return intersection

    def step(self, agents, time):
        assert agents
        assert len(agents)
        assert isinstance(time, int) and time > 0
        
	# do_consensus
        if self._consensus_step == 'inf':
            self._consensus_func(agents, self._ids)
        else:
            self._consensus_func(agents, self._ids, self._edges)

	# syncronize agents
        for agent_id in self._ids:
            agents[agent_id].tick_epoch(time)

        if 1:
            # compute per component aggregate info
            component_estims = []
            for _id in self._ids:
                agent = agents[_id]
                component_estims.append(agent.get_size_estimate())
            
            _max = numpy.max(component_estims)
            _min = numpy.min(component_estims)
            _mean = numpy.mean(component_estims)
            
            print '     component aggregate estim. (min, mean, max):   %.2f   %.2f   %.2f' % (_min, _mean, _max)
	    self._info = (_min, _mean, _max)
       


    def get_info(self):
        return self._info

#        return self._data

