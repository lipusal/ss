package ar.edu.itba.ss.runners.singleLane;

import ar.edu.itba.ss.files.OvitoReader;
import ar.edu.itba.ss.files.OvitoWriter;
import ar.edu.itba.ss.particles.Car;
import ar.edu.itba.ss.particles.Particle;
import ar.edu.itba.ss.runners.Runner;

import java.awt.geom.Point2D;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

@SuppressWarnings("Duplicates")
public class FundamentalDiagramDebug extends Runner {

    public static void main(String[] args) throws IOException {
        final int amountOfCars = 50;
        System.out.println("amount of cars " + amountOfCars);
        final int ROAD_LENGTH = 500,
                MAX_SPEED = 20;
        final double density = 1.0 * amountOfCars / ROAD_LENGTH;
        System.out.println("The system density is " + density);
        int TIME = 706;

        OvitoWriter<Particle> ovitoWriter = null;
        try {
            ovitoWriter = new OvitoWriter<>(Paths.get("out-debug.txt"));
            // Generate placeholders
            List<Car> placeholders = new ArrayList<>(2);
            placeholders.add(new Car(new Point2D.Double(0, 20), 0.1).fake());
            placeholders.add(new Car(new Point2D.Double(ROAD_LENGTH, -20), 0.1).fake());
            // Load cars
            List<Car> carsH = new OvitoReader<Car>(Paths.get("in.txt")).importPositionsOvito(TIME, placeholders.size(), 0);

            ar.edu.itba.ss.models.KSSS modelH = new ar.edu.itba.ss.models.KSSS(ROAD_LENGTH, MAX_SPEED, 7, carsH);
            while (TIME < 3000) { // TODO: parametrizar tiempo de simulación
                List<Particle> allCars = withPlaceholders(placeholders, carsH);
                ovitoWriter.exportPositions(allCars, TIME);
                carsH = modelH.evolve();
                TIME++;
            }
            double accumVelocity = 0;
            for (Car car : carsH) {
                accumVelocity += car.getVX();
            }
            System.out.println("average velocity is " + accumVelocity / amountOfCars);
        } finally {
            if (ovitoWriter != null) {
                ovitoWriter.close();
            }
        }
    }
}

