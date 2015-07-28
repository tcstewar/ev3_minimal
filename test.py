import nengo
import numpy as np
import ev3link
import embodied_benchmarks as bench

if not hasattr(ev3link, 'link'):
    ev3link.link = ev3link.EV3Link('10.42.0.3')
    
link = ev3link.link

path0 = '/sys/class/tacho-motor/motor0/'
link.write(path0 + 'command', 'run-direct')
link.write(path0 + 'position', '0')
print link.read(path0 + 'position')
    
    
model = nengo.Network()
with model:
    
    def ev3_system(t, x):
        value = int(100 * x[0])
        if value > 100:
            value = 100
        if value < -100:
            value = -100
        value = '%d' % value
        ev3link.link.write(path0 + 'duty_cycle_sp', value)
        p = link.read(path0 + 'position')
        try:
            return float(p) / 180 * np.pi
        except:
            return 0
    
    ev3 = nengo.Node(ev3_system, size_in=1, size_out=1)
    
    
    pid = bench.pid.PID(2,1, 3, tau_d=0.001)
    control = nengo.Node(lambda t, x: pid.step(x[:1], x[1:]), size_in=2)
    nengo.Connection(ev3, control[:1], synapse=0)
    nengo.Connection(control, ev3, synapse=None)
    
    
    desired = nengo.Node(0)
    nengo.Connection(desired, control[1:], synapse=None)
    
    