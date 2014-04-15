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

import types
import numpy


class Agent():

    def __init__(self, agentid, time, resample_func, estimator_func):
        assert agentid is not None
        assert isinstance(time, int) and time >= 0
        assert isinstance(resample_func, types.FunctionType)
        assert isinstance(estimator_func, types.FunctionType)

        self._id = agentid
        self._time = time
        self._resample_func = resample_func
        self._estimator_func = estimator_func
        self._active = True

        # init estimator state
        self._resampled_state = None
        self._estimator_state = []
        self._size_estimates = None

        self._working_state = None
        self.resample()
        
        # init filters state
        
        #print '   new Agent with id %s' % str(agentid)

    def sleep(self):
        assert self._active
        self._active = False

    def wake(self):
        assert not self._active
        self._active = True
        
    def active(self):
        return self._active

    def tick_epoch(self, time):
        assert isinstance(time, int) and time > 0
    
        #print 'append_estimator_state', state
        assert self._estimator_state is not None
        assert self._working_state is not None
        
        #print str(self._id), " tick_epoch", 

#        self._estimator_state.append((time, self._working_state))
        self._estimator_state = [(time, self._working_state)]

#        print str(self._id), " tick_epoch ", self._estimator_state


        # update filters
        # update size estimate
        #print 'Agent(id=%s)._update_filters' % self._id
        assert self._estimator_state is not None
        
        estimate = self._estimator_func(self._working_state)

#        if self._size_estimates is None:
#             self._size_estimates = [estimate]
        self._size_estimates = [estimate]
#        else:
#             self._size_estimates.append(estimate)
#             self._size_estimates.pop(0)


    def resample(self):
        self._working_state = self._resample_func()
#        Msample = self._resample_func()
#        if self._estimator_state is None:
#            self._estimator_state = [(0, Msample)]
#        else:
#            last_state = self._estimator_state[len(self._estimator_state) -1]
#            new_state = (last_state[0], Msample)
#            self._estimator_state[len(self._estimator_state) -1] = new_state
        
        #print 'agent %s: resampled_state' % str(self._id), Msample
        
    def get_estimator_state(self):
        assert self._estimator_state is not None

        return self._working_state#.copy()
#        last_state = self._estimator_state[len(self._estimator_state) -1]

 #       state = last_state[1].copy()
        
  #      print str(self._id), " get_estimator_state, all_state=", self._estimator_state, " ret_state=", state
        
   #     return state

    def set_estimator_state(self, new_state):
        assert isinstance(new_state, numpy.ndarray)
        assert self._estimator_state is not None
        
        #print str(self._id), " set_estimator_state", new_state
        
        #new_state = new_state.copy()
        #new_state.shape = (1,len(new_state))
        
        #last_state = self._estimator_state[len(self._estimator_state) -1]

	#self._estimator_state[len(self._estimator_state) -1] = (last_state[0], new_state)
	self._working_state = new_state.copy()
        
    def get_size_estimate(self):
        if self._size_estimates is None:
            return -1.
        return self._size_estimates[-1]


        

