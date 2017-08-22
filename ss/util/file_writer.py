class FileWriter:
    """Utility class used for exporting results to Ovito-compatible formats"""

    @staticmethod
    def export_positions_matlab(board, selected_particle=0, output='dynamic.m'):
        """Writes a .m file that generates a plot of the specified particles, painting the selected particle of a
        particular color, all its neighbors in another color, and all other particles in a different color. Also
        configures a grid to match up with the borders of the board's cells."""
        file = open(output, 'w')
        xs, ys = [], []
        particles = board.particles
        neighbors = board.neighbors
        for particle in particles:
            xs.append(particle.x)
            ys.append(particle.y)

        # Write positions
        file.write('xs = [%s];\n' % (" ".join(str(x) for x in xs)))
        file.write('ys = [%s];\n' % (" ".join(str(y) for y in ys)))
        # Draw the selected particle in a special color and its neighbors in another color; all others black
        colors = []
        selected_neighbors = []
        # Put only real particles in selected_neighbors
        for i in range(len(neighbors[particles[selected_particle].id])):
            particle = neighbors[particles[selected_particle].id][i]
            selected_neighbors.append(particle.original_particle if particle.is_fake else particle)

        for i in range(len(particles)):
            if i == selected_particle:
                color = '1 0 0'  # Red
            elif particles[i] in selected_neighbors:
                color = '0 1 0'  # Green
            else:
                color = '0 0 0'  # Black
            colors.append("%s;" % color)
        file.write('colors = [%s];\n' % " ".join(colors))
        # Plot
        file.write('circle_size = 36;\n')  # Default size
        file.write('scatter(xs, ys, circle_size, colors, \'filled\')\n')
        # Set custom axis values to match cells
        file.write('ax = gca;\n')
        file.write('ax.XLim = [0 %i]; ax.YLim = ax.XLim;\n' % board.l)
        file.write('ax.XTick = [0:%g:%i]; ax.YTick = ax.XTick;\n' % (board.l / board.cells_per_row, board.l))
        file.write('grid on;\n')
        file.close()

    @staticmethod
    def export_positions_ovito(particles, output='dynamic.txt'):
        file = open(output, 'w')
        file.write('%i\n' % len(particles))
        for particle in particles:
            file.write('%g\t%g\n' % (particle.x, particle.y))
