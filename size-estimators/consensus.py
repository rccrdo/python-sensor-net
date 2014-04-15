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

import copy
import random
import numpy


def consensus_asymptotic_avg(agents, ids):
    #print 'consensus component avg'
    assert agents
    assert ids
    assert len(agents)
    assert len(ids)

    if len(ids) == 1:
        agent = agents[ids[0]]
        return agent.get_estimator_state()
    else:
        stacked = None

        for _id in ids:
            if agents[_id].active():
                state = agents[_id].get_estimator_state()
                #print "agent %s state %s" %(repr(_id),repr(state))
                if stacked is None:
                    stacked = state
                else:
                    stacked = numpy.vstack((stacked, state))

        if stacked is not None:
            comp_mean = numpy.mean(stacked, 0)
    
            return comp_mean

        return None


def consensus_component_min(agents, ids):
    #print 'consensus component min'
    assert agents
    assert ids
    assert len(agents)
    assert len(ids)

    if len(ids) == 1:
        agent = agents[ids[0]]
        if agent.active():
            state = agent.get_estimator_state().copy()
            agent.set_estimator_state(state)
    else:
        stacked = None

        for _id in ids:
            if agents[_id].active():
                if stacked is None:
                    stacked = agents[ids[0]].get_estimator_state()
                else: 
                    stacked = numpy.vstack((stacked, agents[_id].get_estimator_state()))

        if stacked is not None:
            comp_min = numpy.min(stacked, 0)
    
            for _id in ids:
                if agents[_id].active():
                    agents[_id].set_estimator_state(comp_min)


def consensus_component_max(agents, ids):
    #print 'consensus component max'
    assert agents
    assert ids
    assert len(agents)
    assert len(ids)

    if len(ids) == 1:
        agent = agents[ids[0]]
        if agent.active():
            state = agent.get_estimator_state().copy()
            agent.set_estimator_state(state)
    else:
        stacked = None
        for _id in ids:
            if agents[_id].active():
                if stacked is None:
                    stacked = agents[_id].get_estimator_state()                
                else:
                    stacked = numpy.vstack((stacked, agents[_id].get_estimator_state()))

        if stacked is not None:
            comp_max = numpy.max(stacked, 0)
    
            for _id in ids:
                if agents(_id).active():
                    agents[_id].set_estimator_state(comp_max)


def consensus_component_avg(agents, ids):
    #print 'consensus component avg'
    assert agents
    assert ids
    assert len(agents)
    assert len(ids)

    if len(ids) == 1:
        agent = agents[ids[0]]
        if agent.active():
            state = agent.get_estimator_state().copy()
            agent.set_estimator_state(state)
    else:
        stacked = None

        for _id in ids:
            if agents[_id].active():
                if stacked is None:
                    stacked = agents[_id].get_estimator_state()                
                else:
                    stacked = numpy.vstack((stacked, agents[_id].get_estimator_state()))

        assert stacked is not None
        if stacked is not None:
            comp_mean = numpy.mean(stacked, 0)
    
            for _id in ids:
                if agents[_id].active():
                    agents[_id].set_estimator_state(comp_mean)



def consensus_component_avg_use_fractions(agents, ids):
    #print 'consensus component avg use fractions'
    assert agents
    assert ids
    assert len(agents)
    assert len(ids)

    if len(ids) == 1:
        agent = agents[ids[0]]
        if agent.active():
            state = agent.get_estimator_state().copy()
            agent.set_estimator_state(state)
    else:
        stacked = None
        
        for _id in ids:
            if agents[_id].active():
                if stacked is None:
                    stacked = agents[_id].get_estimator_state()
                else:
                    stacked = numpy.vstack((stacked, agents[_id].get_estimator_state()))

        if stacked is not None:
            comp_mean = numpy.sum(stacked, 0)/int(stacked.shape[0])
    
            for _id in ids:
                if agents[_id].active():
                    agents[_id].set_estimator_state(comp_mean)


def copy_list_with_randomized_order(l):
    shuffled = copy.copy(l)
    random.shuffle(shuffled)
    return shuffled
    

def consensus_max(agents, ids, edges):
    #print 'consensus max'
    assert agents
    assert len(agents)

    if len(ids) == 1:
        agent = agents[ids[0]]
        state = agent.get_estimator_state().copy()
        agent.set_estimator_state(state)
    else:
        assert edges
        assert len(edges)

        edges = copy_list_with_randomized_order(edges)
        for e in edges:
            i = e[0]
            j = e[1]
            
            if not agents[i].active() or not agents[j].active():
                continue
            
            istate = agents[i].get_estimator_state()
            jstate = agents[j].get_estimator_state()
            
            stacked = istate
            stacked = numpy.vstack((istate, jstate))
            comp_max = numpy.max(stacked, 0)

            #print 'edge ', str(e), ' istate=', istate, ' jstate=', jstate, ' stacked ', stacked, ' comp_max=', comp_max

            agents[i].set_estimator_state(comp_max)
            agents[j].set_estimator_state(comp_max)
            
            #print '\n\n\n\n'

def consensus_min(agents, ids, edges):
    #print 'consensus max'
    assert agents
    assert edges
    assert len(agents)
    assert len(edges)

    if len(ids) == 1:
        agent = agents[ids[0]]
        state = agent.get_estimator_state().copy()
        agent.set_estimator_state(state)
    else:
        edges = copy_list_with_randomized_order(edges)
        for e in edges:
            i = e[0]
            j = e[1]
            
            if not agents[i].active() or not agents[j].active():
                continue

            istate = agents[i].get_estimator_state()
            jstate = agents[j].get_estimator_state()
            
            stacked = istate
            stacked = numpy.vstack((istate, jstate))
            comp_min = numpy.min(stacked, 0)

            #print 'edge ', str(e), ' istate=', istate, ' jstate=', jstate, ' stacked ', stacked, ' comp_max=', comp_max

            agents[i].set_estimator_state(comp_min)
            agents[j].set_estimator_state(comp_min)
            
            #print '\n\n\n\n'
            
def consensus_avg(agents, ids, edges):
    #print 'consensus max'
    assert agents
    assert len(agents)

    if len(ids) == 1:
        agent = agents[ids[0]]
        state = agent.get_estimator_state()
        agent.set_estimator_state(state)
    else:
        assert edges
        assert len(edges)
        edges = copy_list_with_randomized_order(edges)
        for e in edges:
            i = e[0]
            j = e[1]
            
            if not agents[i].active() or not agents[j].active():
                assert 0
                continue
            
            istate = agents[i].get_estimator_state()
            jstate = agents[j].get_estimator_state()
            
            comp_avg = 0.5*(istate+jstate)

            #print 'edge ', str(e), ' istate=', istate, ' jstate=', jstate, ' comp_avg=', comp_avg

            agents[i].set_estimator_state(comp_avg)
            agents[j].set_estimator_state(comp_avg)
            
            #print '\n\n'


def consensus_avg_use_fractions(agents, ids, edges):
    #print 'consensus max'
    assert agents
    assert edges
    assert len(agents)
    assert len(edges)

    if len(ids) == 1:
        agent = agents[ids[0]]
        state = agent.get_estimator_state().copy()
        agent.set_estimator_state(state)
    else:
        edges = copy_list_with_randomized_order(edges)
        for e in edges:
            i = e[0]
            j = e[1]
            
            if not agents[i].active() or not agents[j].active():
                continue

            istate = agents[i].get_estimator_state()
            jstate = agents[j].get_estimator_state()
            
            stacked = istate
            stacked = numpy.vstack((istate, jstate))
            comp_avg = (istate+jstate)/2
            
#            for k in range(0,len(comp_avg)):
 #               f = comp_avg[k]
  #              f.limit_denominator(1000000)
   #             comp_avg[k] = f

            #print 'edge ', str(e), ' istate=', istate, ' jstate=', jstate, ' stacked ', stacked, ' comp_max=', comp_max

            agents[i].set_estimator_state(comp_avg)
            agents[j].set_estimator_state(comp_avg)
            
            #print '\n\n\n\n'

