package ar.edu.itba.ss.runners.singleLane;

import ar.edu.itba.ss.files.OvitoWriter;
import ar.edu.itba.ss.models.KSSS;
import ar.edu.itba.ss.particles.Car;
import ar.edu.itba.ss.particles.Particle;
import ar.edu.itba.ss.runners.Runner;

import java.awt.geom.Point2D;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

public class Ksss extends Runner{

    @SuppressWarnings("Duplicates")
    public static void main(String[] args) throws IOException {
        final int ROAD_LENGTH = 1000,
                MAX_SPEED = 20;
        final double P = 0.1;
        final int car_radius = 1;
        OvitoWriter<Particle> ovitoWriter = new OvitoWriter<>(Paths.get("out.txt"));

        List<Car> placeholders = new ArrayList<>(2);
        placeholders.add(new Car(new Point2D.Double(0, ROAD_LENGTH/2.0 + 20), 0.1).fake());
        placeholders.add(new Car(new Point2D.Double(ROAD_LENGTH, ROAD_LENGTH/2.0 - 20), 0.1).fake());

        List<Car> carsH = new ArrayList<>();
        carsH.add(new Car(new Point2D.Double(0, ROAD_LENGTH/2.0), new Point2D.Double(2, 0), car_radius));
        carsH.add(new Car(new Point2D.Double(10, ROAD_LENGTH/2.0), new Point2D.Double(1, 0), car_radius));
//        cars.add(new Car(new Point2D.Double(7, 0), new Point2D.Double(2, 0)));
        carsH.add(new Car(new Point2D.Double(20, ROAD_LENGTH/2.0), car_radius));

        KSSS modelH = new KSSS(ROAD_LENGTH, MAX_SPEED, 5, true, 0.5, 0.94, 0.1, carsH);
        int t = 0;
        while (t < 500) { // TODO: parametrizar tiempo de simulación
            List<Particle> allCars = withPlaceholders(placeholders, carsH);
            ovitoWriter.exportPositions(allCars, t);
            carsH = modelH.evolve();
            t++;
        }
        ovitoWriter.close();
    }
}
