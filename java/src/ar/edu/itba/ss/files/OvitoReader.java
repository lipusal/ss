package ar.edu.itba.ss.files;

import ar.edu.itba.ss.particles.Car;
import ar.edu.itba.ss.particles.Particle;

import java.awt.*;
import java.awt.geom.Point2D;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public class OvitoReader<T extends Particle> {
    private final File file;
    private final BufferedReader fileReader;

    public OvitoReader(File file) throws IOException {
        this.file = file;
        this.fileReader = new BufferedReader(new FileReader(this.file));
    }

    public OvitoReader(Path path) throws IOException {
        this(path.toFile());
    }

    public OvitoReader(OvitoWriter<T> writer) throws IOException {
        this(writer.file);
    }

    public void close() throws IOException {
        this.fileReader.close();
    }

    /**
     * Import <b>ONLY CARS</b> from the given output file created by {@link OvitoWriter#exportPositions(List, double)}.
     * @param time              Time to read
     * @param numPlaceholders   Number of placeholders.
     * @param numTrafficLights  Number of traffic lights.
     * @return The imported cars or {@code null} if the time was not found.
     */
    public List<Car> importPositionsOvito(double time, int numPlaceholders, int numTrafficLights) throws IOException {
        boolean done = false;
        List<Car> result = null;
        do {
            if(!fileReader.ready()) {
                throw new IllegalArgumentException("Reached end of file (?) but time " + time + " was not reached");
            }
            int numParticles = Integer.parseInt(fileReader.readLine());
            double currentTime = Double.parseDouble(fileReader.readLine());
            if (currentTime == time) {
                result = new ArrayList<>(numParticles);
            }
            for (int i = 1; i <= numParticles; i++) {
                String line = fileReader.readLine();
                boolean isCar = i <= numParticles - numPlaceholders - numTrafficLights,
                        isTrafficLight = i > numParticles - numTrafficLights,
                        isPlaceholder = !isCar && !isTrafficLight;
                if (currentTime == time) {
                    if (isCar) {
                        String[] params = line.split("\t");
                        int id = Integer.parseInt(params[0]);
                        double x = Double.parseDouble(params[1]),
                                y = Double.parseDouble(params[2]),
                                vx = Double.parseDouble(params[3]),
                                vy = Double.parseDouble(params[4]);
                        Color color = new Color(Integer.parseInt(params[5]), Integer.parseInt(params[6]), Integer.parseInt(params[7]));
                        double radius = Double.parseDouble(params[8]);
                        Car carToAdd = new Car(id, new Point2D.Double(x, y), new Point2D.Double(vx, vy), new Point2D.Double(0, 0), radius);
                        carToAdd.setColor(color);
                        //noinspection ConstantConditions
                        result.add(carToAdd);
                    }
                }
            }
            if (currentTime == time) {
                done = true;
            }
        } while(!done);
        return result;
    }
}
