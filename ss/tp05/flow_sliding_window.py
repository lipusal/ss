def sliding_window_flow(window_size, input="flow_n.txt", output="sliding_window.txt"):
    """Use a sliding-window strategy to calculate flow of particles in the given simulation. Write each step of the
    algorithm in the specified output file."""
    file = open(input, "r")
    ns, ts = [], []
    for line in file:
        n, t = map(float, line.split(','))
        ns.append(n)
        ts.append(t)
    file.close()

    file = open(output, mode="w")
    width = window_size // 2
    i = 0
    while i + width - 1 < len(ns):
        start, end = i - width, i + width - 1
        flow = (ns[end] - ns[start]) / (ts[end] - ts[start])
        line = "%i,%g\n" % (i, flow)
        file.write(line)
        print(line.strip())
        i += 1
    file.close()


def append_event(output, num_fallen_particles, t, mode="a"):
    file = open(output, mode)
    file.write('%i,%g\n' % (num_fallen_particles, t))
    file.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("window_size", help="Window size to use.", type=int)
    parser.add_argument("--input", "-i", help="Input file. Default is 'flow_n.txt'", type=str, default='flow_n.txt')
    parser.add_argument("--output", "-o", help="Output file. Default is 'sliding_window.txt'", type=str, default="sliding_window.txt")
    args = parser.parse_args()

    sliding_window_flow(args.window_size, args.input, args.output)
