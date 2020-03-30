"""
This code is can be run using
Matlab (commercial package)
Octave (open source version)

parameters.py for SEIR model

S = susceptible population
E = Exposed (infected, not yet infectious)
I = Infectious (now can infect others)
R = Removed (got sick, now recovered and immune, or died :( )
N = total population = (S + E + I + R)


note: added cRI/N term:  disease
mutates, can cause reinfection, or immunity lost
This assumes that mutated form jumps to Infected population
Can also assume that mutated form jumps to Exposed population
For now, we assume c=0 (no mutation has been observed)

dS/dt = -beta*S*I/N
dE/dt = +beta*S*I/N - sigma*E
dI/dt = +sigma*E -gamma*I + c*R*I/N
dR/dt = gamma*I -c*R*I/N

this file passes "seir.m" function to ode solver
ode systen is specified in "seir.m" file



Parameters from:

Wang, H., Wang, Z., Dong, Y. et al. Phase-adjusted estimation of
the number of Coronavirus Disease 2019 cases in Wuhan, China.
Cell Discov 6, 10 (2020). https://doi.org/10.1038/s41421-020-0148-0


Wuhan, Feb 2020
Based on estimates for original outbreak in Wuhan

These p #rs are pretty much guestimates, but are probably
the right order of magnitude
"""
import numpy as np
import parameters as parameters
from scipy import integrate
from calculations_module import seir_function
import matplotlib.pyplot as plt



S_0 = 11.0e+6  # Wuhan city  excluding initial infected, exposed population,

I_0 = 40.0  # initial infected from market
# https://www.imperial.ac.uk/mrc-global-infectious-disease-analysis/newsâ€“wuhan-coronavirus/

E_0 = 20. * I_0  # initial exposed
# https://www.medrxiv.org/content/10.1101/2020.01.23.20018549v1.full.pdf


R_0 = 0  # initial recovered (not to be confused with R_zero, below)
# initially, no one has recovered

#
#  params is a structure used to pass parameters.py to the
#   ODE solver

c = 0.0  # no mutation (yet)
# maybe this happens later?

N = S_0 + I_0 + E_0 + R_0  # N = total population

sigma = 1. / 5.2  # https://doi.org/10.1056/NEJMoa2001316 (2020).

gamma = 1. / 18.  # https://www.imperial.ac.uk/mrc-global-infectious-disease-analysis/newsâ€“wuhan-coronavirus
"""
 R_zero = number of people infected by each infectious person
          this has nothing to do with "R" = removed above
          or R_0 (initial value of recovered)
          but is common terminology (confusing, but usual notation)
     time dependent, starts offf large, than drops with
         time due to public health actions (i.e. quarantine, social distancing)

    R_zero > 1, cases increase
    R_zero < 1 cases peak and then drop off 

      R_zero declining with time https://www.nature.com/articles/s41421-020-0148-0

      beta = R_zero*gammma (done in "seir.m" )
 
     table of:   time(days)  R_zero
                  ....     ....
                  ....     ....
                  ....     ....
       linearly interpolate between times

       Note: this is different from Wang et al (2020), which assumes
             piecewise constant values for R_zero

"""
r_zero_array = np.zeros([6, 2])
r_zero_array[0, :] = [0.0,  3.0]
r_zero_array[1, :] = [60.0,  2.6]
r_zero_array[2, :] = [70.0,  1.9]
r_zero_array[3, :] = [84.0,  1.0]
r_zero_array[4, :] = [90.0,  .50]
r_zero_array[5, :] = [1000, .50]
# r_zero_array = [[0.0,  3.0],   # t=0 days    R_zero = 3.0
#                 [60.0,  2.6],   # t = 60 days R_zero = 2.6
#                 [70.0,  1.9],  # t = 70 days R_zero = 1.9
#                 [84.0,  1.0],  # t = 84 days R_zero = 1.0
#                 [90.0,  .50],  # t = 90 days R_zero = .50
#                 [1000, .50]]  # t = 1000 days R_zero =.50

params = parameters.Params(c, N, sigma, gamma, r_zero_array)

#
#
#  time units = days

#
#

#     [start_time  end_time] (days)
#
t_0 = 0
tspan = np.linspace(t_0, 181, 180)  # time in days

#

#    y(1) = S
#    y(2) = E
#    y(3) = I
#    y(4) = R


y_init = np.zeros(4)
y_init[0] = S_0
y_init[1] = E_0
y_init[2] = I_0
y_init[3] = R_0

tol = 1.e-6  # ode solver tolerance

# # set 'Stats','on' to get more info
#
# options = odeset('AbsTol', tol, 'RelTol', tol, 'MaxOrder', 5, 'Stats', 'on')
#
# #
# #    note: set Refine switch to avoid interpolation
# #
# # options = odeset('AbsTol', tol,'RelTol',tol,'MaxOrder',5,'Stats','on','Refine',1)
#
# runtime = cputime
#
# #    non-stiff solver, matlab and Octave


def seir_with_params(t, y):
    return seir_function(t, y, params)


r = integrate.ode(seir_with_params).set_integrator("dopri5")
r.set_initial_value(y_init, t_0)
y = np.zeros((len(tspan), len(y_init)))
y[0, :] = y_init  # array for solution
for i in range(1, 180):
    y[i, :] = r.integrate(tspan[i])
    if not r.successful():
        raise RuntimeError("Could not integrate")

# plt.plot(tspan, y[:, 1:])
# plt.show()
#
#
# # plt.plot([1,2,3])
#
# plt.subplot(2,1,1)
# plt.plot(tspan, y[:,0],'b-')
# xlabel('time(days)');
# ylabel('S: susceptible')


fig, axes = plt.subplots(ncols=2)
axes[0].plot(tspan, y[:, 0], color="b", label="S: susceptible")
axes[1].plot(tspan, y[:, 1], color="r", label="E: exposed")
axes[0].set(xlabel="time (days)", ylabel="S: susceptible")
axes[1].set(xlabel="time (days)", ylabel="E: exposed")

axes[0].legend()
axes[1].legend()
plt.show()

fig, axes = plt.subplots(ncols=2)
axes[0].plot(tspan, y[:, 2], color="b", label="I: infectious")
axes[1].plot(tspan, y[:, 3], color="r", label="R: recovered")
axes[0].set(xlabel="time (days)", ylabel="I: infectious")
axes[1].set(xlabel="time (days)", ylabel="R: recovered")

axes[0].legend()
axes[1].legend()
plt.show()

total_cases = y[:, 1] + y[:, 2] + y[:, 3]
total_cases_active = y[:, 1] + y[:, 2]

fig, axes = plt.subplots(ncols=2)
axes[0].plot(tspan, total_cases, color="b", label="E+I+R: Total cases")
axes[1].plot(tspan, total_cases_active, color="r", label="E+I: Total cases")
axes[0].set(xlabel="time (days)", ylabel="E+I+R: Total cases")
axes[1].set(xlabel="time (days)", ylabel="E+I: Active cases")
plt.show()

help = 9
#
# [t, y] = ode45( @ (t, y) seir(t, y, params), tspan, y_init, options)
#
# #
# #     stiff solver, matlab only
# # [t,y] = ode15s( @(t, y) seir(t,y, params), tspan, yinit, options)
# #
#
# runtime = cputime - runtime
#
# nsteps = length(t)
#
# # disp(sprintf('number of steps:\t#15.5f',nsteps))
#
# figure
#
# subplot(2, 1, 1), plot(t, y(:, 1), 'b-')
# xlabel('time(days)')
# ylabel('S: susceptible')
#
# subplot(2, 1, 2), plot(t, y(:, 2), 'b-')
# xlabel('time(days)')
# ylabel('E: exposed')
#
# figure
#
# subplot(2, 1, 1), plot(t, y(:, 3), 'b-')
# xlabel('time(days)')
# ylabel('I: infectious')
#
# subplot(2, 1, 2), plot(t, y(:, 4), 'b-')
# xlabel('time(days)')
# ylabel('R: recovered')
#
# total_cases(:, 1) = y(:, 2) + y(:, 3) + y(:, 4)
#
# figure
#
# plot(t, total_cases(:, 1), 'b-')
# xlabel('time(days)')
# ylabel('Total Cases: E+I+R ')
#
# figure
# total_cases_active(:, 1) = y(:, 2) + y(:, 3)
# plot(t, total_cases_active(:, 1), 'b-')
# xlabel('time(days)')
# ylabel('Total Active Cases: E+I ')
#
# S_end = y(nsteps, 1)
# E_end = y(nsteps, 2)
# I_end = y(nsteps, 3)
# R_end = y(nsteps, 4)
#
# total = S_end + E_end + I_end + R_end
#
# disp(sprintf('CPU time(sec):\t#15.5f', runtime))
#
# disp(sprintf('\n time (days): \t#10.2f \n', t(nsteps)))
#
# disp(sprintf('total population:\t#10.2f', total))
#
# disp(sprintf('initial infected:\t#10.2f', I_0))
#
# disp(sprintf('\n total cases (E+I+R) at t= #10.2f: #10.2f \n', ...
# t(nsteps), E_end + I_end + R_end ))
#
#
# disp(sprintf('\n Recovered at t= #-10.2f: #10.2f \n', t(nsteps), R_end))
# disp(sprintf('\n Infected (infectious) at t= #-10.2f: #10.2f \n', t(nsteps), I_end))
# disp(sprintf('\n Exposed (non-infectious) at t= #-10.2f: #10.2f \n', t(nsteps), E_end))
# disp(sprintf('\n Susceptable at t= #-10.2f: #10.2f \n', t(nsteps), S_end))
#
#
#