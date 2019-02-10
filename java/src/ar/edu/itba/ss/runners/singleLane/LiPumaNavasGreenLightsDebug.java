package ar.edu.itba.ss.runners.singleLane;

import ar.edu.itba.ss.files.OvitoReader;
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

public class LiPumaNavasGreenLightsDebug extends Runner {

    @SuppressWarnings("Duplicates")
    public static void main(String[] args) throws IOException {
        final int ROAD_LENGTH = 500,    // 500 * 7.5m = 3.75km
                MAX_SPEED = 3,          // 3 * 7.5 * 3.6 = 81km/h
                SECURITY_GAP = 1;
        OvitoWriter<Particle> ovitoWriter = null;
        int TIME = 133;
        try {
            double deltaT = (ROAD_LENGTH/4.0) / MAX_SPEED; // Distance between lights / VMax = t min for cars to get from one light to the next
            // TODO try making green last as long as needed for all cars to pass. But all traffic lights should have the same durations
            // First traffic light
            int greenDurationOne = 50;
            int redDurationOne = 25;
            int phaseOne = 0;
            // Second traffic light
            int greenDurationTwo = 50;
            int redDurationTwo = 25;
            int phaseTwo = (int) deltaT % greenDurationOne;
            // Third traffic light
            int greenDurationThree = 50;
            int redDurationThree = 25;
            int phaseThree = (int) (2 * deltaT) % greenDurationOne;

            ovitoWriter = new OvitoWriter<>(Paths.get("out-debug.txt"));
            List<Car> placeholders = new ArrayList<>(2);
            placeholders.add(new Car(new Point2D.Double(0, -10), 0.1).fake());
            placeholders.add(new Car(new Point2D.Double(ROAD_LENGTH, 10), 0.1).fake());

            /* *************************************************************************************************************
             *                                                  MODEL
             * ************************************************************************************************************/
            /* *************************************************************************************************************
             *                                      TRAFFIC LIGHTS EVERY ~400M
             * ************************************************************************************************************/
            List<TrafficLight> trafficLightsH = new ArrayList<>();
            for (int x = 54; x < ROAD_LENGTH; x += 54) {
                trafficLightsH.add(new TrafficLight(new Point2D.Double(x, 0), redDurationOne, greenDurationOne, phaseOne));
            }
            evolveTrafficLightsUntil(trafficLightsH, TIME);

            List<Car> carsH = new OvitoReader<Car>(Paths.get("in.txt")).importPositionsOvito(TIME, placeholders.size(), trafficLightsH.size());

            ar.edu.itba.ss.models.LiPumaNavas modelH = new ar.edu.itba.ss.models.LiPumaNavas(ROAD_LENGTH, MAX_SPEED, SECURITY_GAP, true, carsH, trafficLightsH, TIME);

            while (TIME < 500) { // TODO: parametrizar tiempo de simulación
                List<Particle> allCars = withPlaceholders(placeholders, carsH);
                allCars.addAll(trafficLightsH);
                // Export first
                ovitoWriter.exportPositions(allCars, TIME);
                // Evolve later
                carsH = modelH.evolve();
                TIME++;
            }
            ovitoWriter.close();
        } finally {
            if (ovitoWriter != null) {
                ovitoWriter.close();
            }
        }
    }
}
