def sliding_window_flow(window_size, input="flow_n.txt", output="sliding_window.txt"):
    file = open(input, "r")
    ns, ts = [], []
    for line in file:
        n, t = map(float, line.split(','))
        ns.append(n)
        ts.append(t)
    file.close()

    file = open(output, mode="w")
    width = window_size // 2
    i = width
    while i + width <= len(ns):
        end, start = i + width, i - width
        flow = (ns[end] - ns[start]) / (ts[end] - ts[start])
        file.write("%i,%g\n" % (i, flow))


def append_event(output, num_fallen_particles, t, mode="a"):
    file = open(output, mode)
    file.write('%i,%g\n' % (num_fallen_particles, t))
    file.close()
