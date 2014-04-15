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
import copy

AGENT_STATE_STARTINGUP = 0
AGENT_STATE_SS = 1
AGENT_STATE_SLEEPING = 2

class Agent():
    _log_lambdas_dict = {
      # M, alpha_0
      (500, 0.01) : (-2.6504, -3.6234, -4.2976, -4.9290, -5.5099, -6.0429, -6.5757, -6.9775, -7.5614, -7.9999, -8.4281, -8.8972, -9.3321, -9.7284, -10.1285, -10.5038, -10.9178, -11.3490, -11.7826, -12.1649, -12.5418, -12.9319, -13.2346, -13.6331, -14.0614, -14.4196, -14.7488, -15.1706, -15.5105, -15.8710, -16.2194, -16.5897, -17.0407, -17.3084, -17.7102, -17.9961, -18.4059, -18.7022, -19.1284, -19.4054, -19.7766, -20.0641, -20.4635, -20.8670, -21.0645),
      (500, 0.05) : (-1.3353, -2.1028, -2.6698, -3.2095, -3.6878, -4.1250, -4.5792, -5.0044, -5.4067, -5.7801, -6.1900, -6.5751, -6.9296, -7.3154, -7.7293, -8.0456, -8.4299, -8.7852, -9.1387, -9.4546, -9.8086, -10.1532, -10.4947, -10.8385, -11.1745, -11.5012, -11.8291, -12.1715, -12.5267, -12.8411, -13.1438, -13.4719, -13.7954, -14.1720, -14.4848, -14.7751, -15.0818, -15.4344, -15.7517, -16.0880, -16.3897, -16.7092, -16.9842, -17.3143, -17.6279),
      (100, 0.01) : (-2.6281, -3.5352, -4.2691, -4.8135, -5.4607, -5.9277, -6.4615, -6.9446, -7.3462, -7.8565, -8.3408, -8.7262, -9.1157, -9.4856, -9.9376, -10.3351, -10.7137, -11.0715, -11.5118, -11.8877, -12.2451, -12.6005, -13.0207, -13.4071, -13.7110, -14.1408, -14.4646, -14.8051, -15.2533, -15.4879, -15.9610, -16.3159, -16.6717, -16.9199, -17.2950, -17.6596, -17.9332, -18.3563, -18.5853, -18.9606, -19.3234, -19.7389, -20.0948, -20.2710, -20.7182),
      (100, 0.05) : (-1.3017, -2.0300, -2.6257, -3.1430, -3.6166, -4.0265, -4.4747, -4.8707, -5.2945, -5.6645, -6.0665, -6.4173, -6.7932, -7.1844, -7.5122, -7.8681, -8.2139, -8.5729, -8.9107, -9.2642, -9.5958, -9.9377, -10.2647, -10.6106, -10.9299, -11.2385, -11.5807, -11.8931, -12.1992, -12.5368, -12.8596, -13.1546, -13.4979, -13.7966, -14.1156, -14.4016, -14.7516, -15.0426, -15.3615, -15.6613, -15.9601, -16.3065, -16.6045, -16.9138, -17.2020),
      (50,0.01) : (-2.5771, -3.4889, -4.1979, -4.8285, -5.3300, -5.8381, -6.3518, -6.8376, -7.2610, -7.7090, -8.1500, -8.5712, -8.9667, -9.3936, -9.8237, -10.2738, -10.5618, -10.9052, -11.3376, -11.6982, -12.0512, -12.4544, -12.8300, -13.1436, -13.5439, -13.9202, -14.2774, -14.5703, -14.9666, -15.3226, -15.6311, -16.0204, -16.3657, -16.6253, -16.9531, -17.3763, -17.6466, -18.0764, -18.3800, -18.7494, -18.9519, -19.3746, -19.6124, -20.0182, -20.4390),
      (50, 0.05) : (-1.2704, -2.0016, -2.5753, -3.0916, -3.5540, -3.9869, -4.4003, -4.8128, -5.2163, -5.6160, -5.9588, -6.3524, -6.7083, -7.0194, -7.3843, -7.7206, -8.1068, -8.4173, -8.7564, -9.0936, -9.4432, -9.7914, -10.0662, -10.4666, -10.7379, -11.0513, -11.3435, -11.6904, -12.0084, -12.3080, -12.6399, -12.9290, -13.2691, -13.5290, -13.8847, -14.1689, -14.4879, -14.7850, -15.1033, -15.3961, -15.6525, -15.9912, -16.2659, -16.5944, -16.8643)
      }

    def __init__(self, nodeid, M, D, N, barN, alpha_0, sigma, track_exact_size=False):
        assert nodeid is not None
        assert isinstance(M, int) and M > 0
        assert isinstance(D, int) and D > 0
        assert isinstance(N, int) and N > 0
        assert isinstance(barN, int) and barN >= 1 and barN < N
        assert alpha_0 > 0. and alpha_0 < 1.
        assert sigma > 0. and sigma <= 1.

        #print "New agent with id ", nodeid

        assert (M, alpha_0) in self._log_lambdas_dict.keys()
        self._log_lambdas = self._log_lambdas_dict[(M,alpha_0)]
        assert len(self._log_lambdas) > N

        self._id = nodeid
        self._active = True
        self._test_enabled = True
        self._sleepable = True

        self._M = M
        self._M__1_minus_logM__ = M*(1. -numpy.log(M))
        
        self._D = D
        self._N = N
        self._barN = barN
        self._sigma = sigma

        # init state
        self._size_estimates = None
        self._traj = []
        self._x_traj = []
        self._M_log_x_traj = []
        self._S_traj = []
        for k in xrange(0,D):
            self._x_traj.append([])
            self._M_log_x_traj.append([])
            self._S_traj.append([])

        self._track_exact_size = track_exact_size
        self._seen_nodes = None
        self._exact_sizes = None
        if self._track_exact_size:
            self._seen_nodes = []
            for k in xrange(0,D):
                self._seen_nodes.append(set())
        
        
        self._F_at_epoch_start = None
        self._F = None
        self._test_info = None
        
        self._init_state()
        self._state = AGENT_STATE_STARTINGUP

    def get_id(self):
        return self._id
        

    def _compute_X_S(self, F):
        assert isinstance(F, numpy.ndarray)
        assert F.shape == (self._D, self._M)
        X = -numpy.sum(numpy.log(F),1)
        S = float(self._M)/X
        return (X,S)


    def _init_state(self):
        F = numpy.random.uniform(1., 0., (self._D, self._M))
        
	self._F_at_epoch_start = F
        self._F = F
        self._test_info = None
        
        
        self._seen_nodes_at_epoch_start = None
        if self._track_exact_size:
            for k in xrange(0,self._D):
                assert len(self._seen_nodes[k]) == 0
                self._seen_nodes[k].add(self._id)
            
            self._seen_nodes_at_epoch_start = copy.deepcopy(self._seen_nodes)
            

#    @profile
    def tick_epoch(self, time):
        assert isinstance(time, int) and time > 0
        assert self._F_at_epoch_start is not None
        assert self._F is not None
        assert len(self._traj) <= self._N + 1

        #assert self._active
        if not self._active:
            return

        self._test_info = None

        assert len(self._x_traj) == self._D
        assert len(self._M_log_x_traj) == self._D
        assert len(self._S_traj) == self._D

        X, S = self._compute_X_S(self._F)
        self._traj.append((time, self._F, X, S))
        print S

        for k in xrange(0,self._D):
            self._x_traj[k].append(X[k])
            self._M_log_x_traj[k].append(self._M*numpy.log(X[k]))
            self._S_traj[k].append(S[k])
        

        #print "len(self._x_traj)", len(self._x_traj)
        #print "len(self._S_traj)", len(self._S_traj)

        if len(self._traj) > self._N + 1:
            assert len(self._traj) == self._N+2

            # track only F(t-N),...,F(t)
            self._traj.pop(0)
            for k in xrange(0,self._D):
                #if k == 0:
                #    print 'k',k 
                #    print "len(self._x_traj[k])", len(self._x_traj[k])
                #    print "len(self._S_traj[k])", len(self._S_traj[k])
                assert len(self._x_traj[k]) == self._N+2
                assert len(self._M_log_x_traj[k]) == self._N+2
                assert len(self._S_traj[k]) == self._N+2
                self._x_traj[k].pop(0)
                self._M_log_x_traj[k].pop(0)
                self._S_traj[k].pop(0)
        else:
            if len(self._traj) < self._N + 1:
                assert self._state == AGENT_STATE_STARTINGUP

        if len(self._traj) == self._N+1 and self._test_enabled:
            if not self._state == AGENT_STATE_SS:
                assert self._state == AGENT_STATE_STARTINGUP
                self._state = AGENT_STATE_SS

            # GLR test
            change_time = []
            pre_change_size = []
            loglambda = []
            alarm = []
            
            for k in xrange(0,self._D):
#                for k in range(10,11):
                x_traj = numpy.array(self._x_traj[k], dtype = float)
                M_log_x_traj = numpy.array(self._M_log_x_traj[k], dtype = float)
                S_traj = numpy.array(self._S_traj[k], dtype = float)
                x_traj_cumsum = numpy.cumsum(x_traj)
                
                # find the optimal change time
                argminT = 1
                minLogLambda = 0.
                argminbarS = 0.
#                for T in xrange(1,self._N+1-self._barN):
                for T in xrange(self._N-self._barN + 1, 0, -1):
                    barS = float(self._M*(self._N+1-T))/x_traj_cumsum[self._N-T]
                    sigma_barS = self._sigma*barS

                    M_log_sigma_barS_over_M_plus_1 = self._M*(numpy.log(sigma_barS)) + self._M__1_minus_logM__

                    # compute the GLR using f_k(t-T+1),...,f_k(t)
                    LogLambda = 0.
                    for idx in xrange(self._N-T+1,self._N+1):
                        if S_traj[idx] < sigma_barS:
                            LogLambda +=  M_log_sigma_barS_over_M_plus_1 - sigma_barS*x_traj[idx] + M_log_x_traj[idx]

                    if LogLambda <= minLogLambda:
                        minLogLambda = LogLambda
                        argminT = T
                        argminbarS = barS

                #if self._id == (1,1) and k==4:
                #    print "Agent barS=%f, T=%d, LogLambda=%f" % (argminbarS, argminT, minLogLambda)

                change_time.append(argminT)
                pre_change_size.append(argminbarS)
                loglambda.append(minLogLambda)

                if minLogLambda < self._log_lambdas[argminT-1]:
                    alarm.append(1)
                else:
                    alarm.append(0)

            self._test_info = (change_time, pre_change_size, loglambda, alarm)
        
        # resample and generate F(t+1) by shifting F(t)
        self._F_at_epoch_start = numpy.vstack((numpy.random.uniform(1., 0., (1, self._M)), self._F[0:(self._D-1),]))

        self._F = self._F_at_epoch_start


        if self._track_exact_size:
#            if self._id == (1,1):
#                print self._seen_nodes
#                for i in range(0, self._D):
#                    print "Agent pre S_k %d = %d" % ( i+1, len(self._seen_nodes[i]))

            self._exact_sizes = []
            for i in xrange(0,self._D):
                self._exact_sizes.append(len(self._seen_nodes[i]))

            self._seen_nodes.pop(self._D-1)
            self._seen_nodes.insert(0, set())
            self._seen_nodes[0].add(self._id)
 
 #           if self._id == (1,1):
#                print self._seen_nodes
#                print self._exact_sizes
#                for i in range(0, self._D):
#                    print "Agent post S_k %d = %d" % ( i+1, len(self._seen_nodes[i]))
#                print "\n"
      
            self._seen_nodes_at_epoch_start = copy.deepcopy(self._seen_nodes)


    def get_state_at_epoch_start(self):
        return self._F_at_epoch_start


    def do_pair_consensus(self, other_state):
        assert self._active
        assert isinstance(other_state, numpy.ndarray)
        assert other_state.shape == (self._D, self._M)

        self._F = numpy.maximum(self._F, other_state)


    def get_seen_nodes_at_epoch_start(self):
        return self._seen_nodes_at_epoch_start

    def get_exact_sizes(self):
        return self._exact_sizes

    def do_pair_seen_nodes_consensus(self, other_nodes):
        assert self._active
        assert self._track_exact_size
        assert len(other_nodes) == self._D
        for k in xrange(0,self._D):
#            other_set = other_nodes[k]
#            for nodeid in other_set:
 #               self._seen_nodes[k].add(nodeid)
#            self._seen_nodes[k] = self._seen_nodes[k].union(other_set)
            self._seen_nodes[k].update(other_nodes[k])
         
    def traj(self):
        return self._traj


    def state(self):
        return self._traj[len(self._traj)-1]

    def state2(self):
        return self._state

    def disable_change_detection(self):
        self._test_enabled = False

    def set_sleepable(self, sleepable):
        assert isinstance(sleepable, bool)
        self._sleepable = sleepable

    def sleep(self):
        if not self._active or not self._sleepable:
            return

        self._active = False
        self._state = AGENT_STATE_SLEEPING
        self._test_info = None
        self._traj = []
        self._x_traj = []
        self._M_log_x_traj = []
        self._S_traj = []
        for k in xrange(0,self._D):
            self._x_traj.append([])
            self._M_log_x_traj.append([])
            self._S_traj.append([])

        self._seen_nodes = None
        if self._track_exact_size:
            self._seen_nodes = []
            for k in xrange(0,self._D):
                self._seen_nodes.append(set())

    def wake(self):
        assert not self._active
        self._active = True
        self._init_state()
        self._state = AGENT_STATE_STARTINGUP

    def active(self):
        return self._active
    
    
    def get_estimates_traj(self, k):
        assert isinstance(k, int) and k >= 1 and k <= self._D
        return self._S_traj[k-1]
    
    def test_info(self):
        return self._test_info
