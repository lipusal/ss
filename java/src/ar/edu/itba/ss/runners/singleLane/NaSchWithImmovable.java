package ar.edu.itba.ss.runners.singleLane;

import ar.edu.itba.ss.files.OvitoWriter;
import ar.edu.itba.ss.models.NaSch;
import ar.edu.itba.ss.particles.Car;
import ar.edu.itba.ss.particles.ImmovableCar;
import ar.edu.itba.ss.particles.Particle;
import ar.edu.itba.ss.runners.Runner;

import java.awt.geom.Point2D;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

public class NaSchWithImmovable extends Runner{

    @SuppressWarnings("Duplicates")
    public static void main(String[] args) throws IOException {
        final int ROAD_LENGTH = 300,
                MAX_SPEED = 20;
        final double P = 0.1;
        final double CAR_RADIUS = 0.5;
        OvitoWriter<Particle> ovitoWriter = new OvitoWriter<>(Paths.get("out.txt"));

        List<Car> placeholders = new ArrayList<>(2);

        /* *************************************************************************************************************
         *                                          HORIZONTAL MODEL
         * ************************************************************************************************************/
        placeholders.add(new Car(new Point2D.Double(0, ROAD_LENGTH/2.0 + 20), 0.1).fake());
        placeholders.add(new Car(new Point2D.Double(ROAD_LENGTH, ROAD_LENGTH/2.0 - 20), 0.1).fake());

        List<Car> carsH = new ArrayList<>();
        carsH.add(new Car(new Point2D.Double(0, ROAD_LENGTH/2.0), new Point2D.Double(2, 0), CAR_RADIUS));
        carsH.add(new Car(new Point2D.Double(10, ROAD_LENGTH/2.0), new Point2D.Double(1, 0), CAR_RADIUS));
//        cars.add(new Car(new Point2D.Double(7, 0), new Point2D.Double(2, 0)));
        carsH.add(new Car(new Point2D.Double(20, ROAD_LENGTH/2.0), CAR_RADIUS));
        carsH.add(new ImmovableCar(new Point2D.Double(ROAD_LENGTH - 10, ROAD_LENGTH/2.0)));

        NaSch modelH = new NaSch(ROAD_LENGTH, MAX_SPEED, P, carsH);
        int t = 0;
        while (t < 100) {
            List<Particle> allCars = withPlaceholders(placeholders, carsH);
            ovitoWriter.exportPositions(allCars, t);
            carsH = modelH.evolve();
            t++;
        }
        ovitoWriter.close();
    }

}
