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
     * @param extraDataFn (Optional) Function to write extra data for each particle.
     * @throws IOException On I/O errors.
     */
    public void exportPositions(List<T> particles, double time, Function<T, String> extraDataFn) throws IOException {
        Objects.requireNonNull(particles);
        final int dataSize = particles.size();
        fileWriter.write(String.format("%d\n%g\n", dataSize, time));
        for (T element : particles) {
            // Write basic element data
            fileWriter.write(String.format("%d\t%g\t%g\t%g\t%g",
                    element.getId(),
                    element.getDrawPosition() == null ? element.getX() : element.getDrawX(),
                    element.getDrawPosition() == null ? element.getY() : element.getDrawY(),
                    element.getVX(),
                    element.getVY()))
            ;
            // Write color
            Color color = element.getColor();
            fileWriter.write(String.format("\t%d\t%d\t%d", color.getRed(), color.getGreen(), color.getBlue()));
            // Write draw radius
            fileWriter.write(String.format("\t%g", element.getDrawRadius()));
            // Write extra element data, if any
            if (extraDataFn != null) {
                fileWriter.write('\t' + extraDataFn.apply(element));
            }
            // Always write newline
            fileWriter.write('\n');
        }
        fileWriter.flush();
    }

    /**
     * Equivalent to {@code exportPositions(particles, time, null)}.
     * @see #exportPositions(List, double, Function)
     */
    public void exportPositions(List<T> particles, double time) throws IOException {
        exportPositions(particles, time, null);
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
