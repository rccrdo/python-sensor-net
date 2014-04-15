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
import time
import signal
import shutil

import numpy
import network
from agent import *

from matplotlib import rc
rc('font', family='serif')
import matplotlib.pyplot as plt


# Simulation and change detection config
STOP_EPOCH = 420
TRACK_EXACT_SIZE = True

grid_side = 10
M = 100
D = 20
N = 25
barN = 5
alpha_0 = 0.01
sigma = 0.9

k = 20


# Create dirs in which frames and video will be saved
simid_base = 'plot_M%d_D%d_N%d_barN%d_alpha%.2f_sigma%.2f_k%d_side%d' % (M,D,N,barN,alpha_0,sigma,k,grid_side)
sim_dir = '%s__%s' % (time.strftime("%Y_%b_%d_%H.%M"), simid_base)
frames_dir = '%s/frames' % sim_dir
video_path = '%s/%s.avi' % (sim_dir, simid_base)
video_cmd = "avconv -y -r 2 -i %s/%%04d.png -b 2000k %s" % (frames_dir, video_path)

if os.path.exists(sim_dir):
    shutil.rmtree(sim_dir)

os.mkdir(sim_dir)
os.mkdir(frames_dir)


# Install SIGINT handler so that a video is produced even
# if the user aborts the current simulation
global simulation_stop
simulation_stop = False

def handler_sig_term(signum, frame):
    print '\nStopping simulation ...'
    global simulation_stop
    simulation_stop = True

signal.signal(signal.SIGINT,handler_sig_term)


# Create the network
net = network.Network(M, D, N, barN, alpha_0, sigma, ''.join(['grid2d:',str(grid_side)]), TRACK_EXACT_SIZE)


# Acquire agent at position (0,0) and make it non-sleepable
agent = net.get_agent((0,0))
agent.set_sleepable(False)


# Speed-up simulation by disabling change detection on nodes we are not tracking
agents = net.get_agents()
for nodeid, a in agents.items():
    if nodeid == agent.get_id():
        continue
    a.disable_change_detection()


# Create the figure
fig = plt.figure(figsize=(7.5,7.5))  
plt.ion()
plt.show() 


# Lists used to track the latest N+1 alarm times and the true sizes S_k
alarms_traj = []
exact_size_k = []


assert k>=1 and k<=D
for h in xrange(1,STOP_EPOCH+1):
    if simulation_stop:
        # user sent us SIGINT, exit simulation loop
        break


    # step the network
    net.step()
    t = net.get_time()
    print 'epoch %d/%d' % (t, STOP_EPOCH)


    # the following code depends on the tacked node being non-sleepable
    assert agent.active()


    # setup figure for this iteration
    fig.clf()
    fig.patch.set_facecolor((1,1,1))
    fig_border_width = 0.15
    ax = fig.add_axes([fig_border_width, fig_border_width, 1-2*fig_border_width, 1-2*fig_border_width])


    # get info tuple from node
    info = agent.test_info()


    # plot the curve with the latest S_k estimates
    S_traj_values = agent.get_estimates_traj(k)
    S_traj_points = numpy.arange(t - len(S_traj_values) +1, t+1)
    if info:
        ax.plot(S_traj_points, S_traj_values, 'k')
    else:
        ax.plot(S_traj_points, S_traj_values, color=(1,0.9,0.))


    # compute the number of active nodes, and other stats ...
    active_nodes = 0
    for nodeid, a in agents.items():
       if a.active():
          active_nodes += 1

    alarm_string = "$\mathrm{active}\, %d/%d,\; \\mathrm{alarms}\, %d \,\\mathrm{in} \, %s \leftrightarrow %s$"
    alarm_string_args = [active_nodes, len(agents), 0, "\\cdot", "\\cdot"]

    if info is not None:
        change_time, pre_change_size, loglambda, alarms = info

        T = change_time[k-1]
        barS = pre_change_size[k-1]
        sigma_barS = sigma*barS

        ths_values = [barS]*(N+1-T)
        ths_points = range(t-N,t-T+1)

	T_cut_point = t-T+0.5

        ths_points.extend([T_cut_point]*2)
        ths_values.extend([ barS, sigma_barS])
        
        ths_values.extend([sigma*barS]*T)
        ths_points.extend(range(t-T+1,t+1))

        ax.plot(ths_points, ths_values, 'r--')

        num_alarms = numpy.sum(alarms)
        if num_alarms > 0:
            if alarms[k-1]:
                alarms_traj.append(t)
        
            alarm_string_args[2] = num_alarms
            alarm_string_args[3] = alarms.index(1)+1
            alarm_string_args[4] = D - alarms[::-1].index(1) 


    # un-track alarms that were fired before t-N
    while len(alarms_traj):
        oldest = alarms_traj[0]
        if oldest >= t-N:
            break
        alarms_traj.pop(0)


    # plot the barN, estimated-change-time and alarms vertical panes
    for i in xrange(t-N,t+1):
        if i in alarms_traj:
            plt.axvspan(i-0.5, i+0.5, facecolor=(1,0.1,0.1), alpha=0.1, lw=0., zorder=-1000)
        if info:
            if i <= t-N+barN -1:
                plt.axvspan(i-0.5, i+0.5, facecolor=(0.066,0.705,0.9176), alpha=0.1, lw=0., zorder=-10000)
            elif i < T_cut_point:
                plt.axvspan(i-0.5, i+0.5, facecolor=(0.75,0.75,0.75), alpha=0.1, lw=0., zorder=-10000)
#    else:
#        for i in xrange(t-N,t-N+barN):
#            if i < t-N+barN+0.5:
#                plt.axvspan(i-0.5, i+0.5, facecolor=(1.,0.9,0.), alpha=0.1, lw=0., zorder=-10000)


    # Plot the exact S_k size
    if TRACK_EXACT_SIZE:
        exact_sizes = agent.get_exact_sizes()
        assert exact_sizes is not None
        assert len(exact_sizes) == D

        exact_size_k.append(exact_sizes[k-1])
         
        # Track only the latest N+1 observations
        if len(exact_size_k) > N +1:
            exact_size_k.pop(0)
    
        ax.plot(range(t+1-len(exact_size_k) ,t+1), exact_size_k, 'k--')


    # Text overlays
    ax.set_xlabel("$\\mathrm{epoch}$", family='serif', size=15)
    ax.set_ylabel("$\\widehat{S}_{%d}(t)$" % k, family='serif', size=15)
    plt.figtext(0.5, 0.925, "$M\,%d,\; \\alpha_0\, %.2f,\; D\, %d,\; N\, %d,\; \\overline{N}\, %d,\; \\sigma \, %.2f,\; k\, %d,\; \\mathrm{node}\,%s$" % (M, alpha_0, D, N, barN, sigma, k, str(agent.get_id())), family='serif', size=15, ha='center')
    plt.figtext(0.05, 0.05, alarm_string % tuple(alarm_string_args), family='serif', size=15)    


    # Axis-limits etc...
    max_S = numpy.max(S_traj_values)
    max_y = (int(max_S/50) +1) *50
    ax.set_ylim(0,max_y)
    ax.set_xlim(max(1,t-N),max(N+1,t))
    ax.grid()
    fig.canvas.draw()
    plt.savefig('%s/%.4d' % (frames_dir,t))


# Call avconv to make a video from the saved frames
os.system(video_cmd)

