package ar.edu.itba.ss.files;

import ar.edu.itba.ss.particles.Particle;

import java.awt.*;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Objects;
import java.util.function.Function;

public class OvitoWriter<T extends Particle> {
    private final File file;
    private final FileWriter fileWriter;

    public OvitoWriter(File file) throws IOException {
        this.file = file;
        this.fileWriter = new FileWriter(this.file);
    }

    public OvitoWriter(Path path) throws IOException {
        this(path.toFile());
    }

    public void close() throws IOException {
        this.fileWriter.close();
    }

    /**
     * Export positions in an OVITO-compatible format.
     *
     * @param particles   List of particles to export.
     * @param time        Current simulation time
     * @param colors      (Optional) Colors to paint each particle in. Defaults to white for all particles.
     * @param extraDataFn (Optional) Function to write extra data for each particle.
     * @throws IOException On I/O errors.
     */
    public void exportPositions(List<T> particles, double time, List<Color> colors, Function<T, String> extraDataFn) throws IOException {
        Objects.requireNonNull(particles);
        final int dataSize = particles.size();
        if (colors != null && dataSize != colors.size()) {
            throw new IllegalArgumentException(String.format("Data length (%d) does not match colors length (%d)", dataSize, colors.size()));
        }
        fileWriter.write(String.format("%d\n%g\n", dataSize, time));
        for (int i = 0; i < dataSize; i++) {
            // Write basic element data
            T element = particles.get(i);
            fileWriter.write(String.format("%d\t%g\t%g", element.getId(), element.getX(), element.getY()));
            // Write color, fall back to white if not specified
            Color color = colors == null ? Color.WHITE : colors.get(i);
            fileWriter.write(String.format("\t%d\t%d\t%d", color.getRed(), color.getGreen(), color.getBlue()));
            // Write extra element data, if any
            if (extraDataFn != null) {
                fileWriter.write(extraDataFn.apply(element));
            }
            // Always write newline
            fileWriter.write('\n');
        }
        fileWriter.flush();
    }

    /**
     * Appends the specified line to the file.
     *
     * @param line          The line to append. <b>NOTE:</b> A newline is automatically added after the line, so there's
     *                      no need to include it in here.
     * @throws IOException  On I/O errors.
     */
    public void appendLine(String line) throws IOException {
        fileWriter.write(line + "\n");
        fileWriter.flush();
    }
}
