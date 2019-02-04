package ar.edu.itba.ss.runners.singleLane;

import ar.edu.itba.ss.files.OvitoWriter;
import ar.edu.itba.ss.particles.Car;
import ar.edu.itba.ss.particles.Particle;
import ar.edu.itba.ss.particles.TrafficLight;
import ar.edu.itba.ss.runners.Runner;

import java.awt.geom.Point2D;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

public class LiPumaNavasGreenLights extends Runner {

    @SuppressWarnings("Duplicates")
    public static void main(String[] args) throws IOException {
        final int ROAD_LENGTH = 500,    // 500 * 7.5m = 3.75km
                MAX_SPEED = 3,          // 3 * 7.5 * 3.6 = 81km/h
                SECURITY_GAP = 1;
        final double car_radius = 0.5;
        boolean errored = false;
        do {
            OvitoWriter<Particle> ovitoWriter = null;
            try {
                double deltaT = (ROAD_LENGTH/4.0) / MAX_SPEED; // Distance between lights / VMax = t min for cars to get from one light to the next
                // TODO try making green last as long as needed for all cars to pass. But all traffic lights should have the same durations
                // First traffic light
                int greenDurationOne = 20;
                int redDurationOne = 10;
                int phaseOne = 0;
                // Second traffic light
                int greenDurationTwo = 20;
                int redDurationTwo = 10;
                int phaseTwo = (int) deltaT % greenDurationOne;
                // Third traffic light
                int greenDurationThree = 20;
                int redDurationThree = 10;
                int phaseThree = (int) (2 * deltaT) % greenDurationOne;

                ovitoWriter = new OvitoWriter<>(Paths.get("out.txt"));
                List<Car> placeholders = new ArrayList<>(2);
                placeholders.add(new Car(new Point2D.Double(0, -10), 0.1).fake());
                placeholders.add(new Car(new Point2D.Double(ROAD_LENGTH, 10), 0.1).fake());

                /* *************************************************************************************************************
                 *                                                  MODEL
                 * ************************************************************************************************************/
                List<Car> carsH = new ArrayList<>();
                carsH.add(new Car(new Point2D.Double(0, 0), new Point2D.Double(2, 0), car_radius));
                carsH.add(new Car(new Point2D.Double(10, 0), new Point2D.Double(1, 0), car_radius));
                carsH.add(new Car(new Point2D.Double(20, 0), car_radius));
                carsH.add(new Car(new Point2D.Double(30, 0), car_radius));
                carsH.add(new Car(new Point2D.Double(40, 0), car_radius));
                carsH.add(new Car(new Point2D.Double(50, 0), car_radius));

                List<TrafficLight> trafficLightsH = new ArrayList<>();
                trafficLightsH.add(new TrafficLight(new Point2D.Double(ROAD_LENGTH / 4.0, 0), redDurationOne, greenDurationOne, phaseOne));
                trafficLightsH.add(new TrafficLight(new Point2D.Double((2 * ROAD_LENGTH) / 4.0, 0), redDurationTwo, greenDurationTwo, phaseTwo));
                trafficLightsH.add(new TrafficLight(new Point2D.Double((3 * ROAD_LENGTH) / 4.0, 0), redDurationThree, greenDurationThree, phaseThree));
                ar.edu.itba.ss.models.LiPumaNavas modelH = new ar.edu.itba.ss.models.LiPumaNavas(ROAD_LENGTH, MAX_SPEED, SECURITY_GAP, true, carsH, trafficLightsH);

                int t = 0;
                while (t < 500) { // TODO: parametrizar tiempo de simulación
                    List<Particle> allCars = withPlaceholders(placeholders, carsH);
                    allCars.addAll(trafficLightsH);
                    ovitoWriter.exportPositions(allCars, t);
                    carsH = modelH.evolve();
                    t++;
                }
                ovitoWriter.close();
            } catch (IllegalStateException | IllegalArgumentException e) {
                errored = true;
                System.out.format("Error in run: %s. Retrying\n", e.getMessage());
            } finally {
                if (ovitoWriter != null) {
                    ovitoWriter.close();
                }
            }
        } while (errored);
    }
}
