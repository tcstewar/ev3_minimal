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
        value = int(20 * x[0])
        value = value
        if value > 100:
            value = 100
        if value < -100:
            value = -100
        value = '%d' % value
        ev3link.link.write(path0 + 'duty_cycle_sp', value)
        try:
            p = link.read(path0 + 'position')
            return float(p) / 180 * np.pi
        except:
            return 0
    
    ev3 = nengo.Node(ev3_system, size_in=1, size_out=1)
    
    
    control = nengo.Node(None, size_in=1)
    nengo.Connection(control, ev3, synapse=None)
    

    adapt = nengo.Ensemble(n_neurons=1000, dimensions=1, neuron_type=nengo.LIFRate())
    nengo.Connection(ev3, adapt[0], synapse=None)
    conn = nengo.Connection(adapt, ev3, synapse=0.001, 
                            function=lambda x: 0,
                            learning_rule_type=nengo.PES())
    conn.learning_rule_type.learning_rate *= 1
    nengo.Connection(control, conn.learning_rule, transform=-1, synapse=None)
    
    jacobian = nengo.Ensemble(n_neurons=200, dimensions=2, neuron_type=nengo.LIFRate())
    
    
    desired = nengo.Node(0)
    #nengo.Connection(desired, control[1:], synapse=None)
    
    nengo.Connection(ev3, jacobian[0], synapse=None)
    nengo.Connection(desired, jacobian[1], synapse=None)
    
    nengo.Connection(jacobian, control, function=lambda x: x[1] - x[0], 
                     transform=5, synapse=0)

    
    
    