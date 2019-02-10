package ar.edu.itba.ss.runners.singleLane;

import ar.edu.itba.ss.files.OvitoWriter;
import ar.edu.itba.ss.particles.Car;
import ar.edu.itba.ss.particles.Particle;
import ar.edu.itba.ss.runners.Runner;

import java.awt.geom.Point2D;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

public class fundamentalDiagram extends Runner {

    public static void main(String[] args) throws IOException {
        final int amountOfCars = 50;
        System.out.println("amount of cars " + amountOfCars);
        final int ROAD_LENGTH = 500,
                MAX_SPEED = 20;
        final double density = 1.0 * amountOfCars / ROAD_LENGTH;
        System.out.println("The system density is " + density);
        final double P = 0.1;
        final int carRadius = 1;
        Boolean hadError;
        do {
            OvitoWriter<Particle> ovitoWriter;
            try {
                ovitoWriter = new OvitoWriter<>(Paths.get("out.txt"));
                // Generate cars and placeholders
                List<Car> placeholders = new ArrayList<>(2);
                placeholders.add(new Car(new Point2D.Double(0, ROAD_LENGTH / 2.0 + 20), 0.1).fake());
                placeholders.add(new Car(new Point2D.Double(ROAD_LENGTH, ROAD_LENGTH / 2.0 - 20), 0.1).fake());
                List<Car> carsH = generateCars(amountOfCars, ROAD_LENGTH, carRadius, 1);

//        ar.edu.itba.ss.models.NaSch modelH = new ar.edu.itba.ss.models.NaSch(ROAD_LENGTH, MAX_SPEED, P, carsH);
                ar.edu.itba.ss.models.KSSS modelH = new ar.edu.itba.ss.models.KSSS(ROAD_LENGTH, MAX_SPEED, 7, carsH);
                int t = 0;
                while (t < 3000) { // TODO: parametrizar tiempo de simulación
                    List<Particle> allCars = withPlaceholders(placeholders, carsH);
                    ovitoWriter.exportPositions(allCars, t);
                    carsH = modelH.evolve();
                    t++;
                }
                double accumVelocity = 0;
                for (Car car : carsH) {
                    accumVelocity += car.getVX();
                }
                System.out.println("average velocity is " + accumVelocity / amountOfCars);
                ovitoWriter.close();
                hadError = false;
            } catch(IllegalStateException | IllegalArgumentException e){
                hadError = true;
                System.out.format("Error in run: %s. Retrying\n", e.getMessage());
            }
        }while(hadError);
    }
}

