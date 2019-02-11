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
        final int ROAD_LENGTH = 250,    // 250 * 7.5m = 1.875km
                MAX_SPEED = 3,          // 3 * 7.5 * 3.6 = 81km/h
                SECURITY_GAP = 1,
                GREEN_DURATION = 35,
                RED_DURATION = 10,
                PHASE_BETWEEN_TRAFFIC_LIGHTS = 5;

        OvitoWriter<Particle> ovitoWriter = null;
        int TIME = 133;
        try {
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
            int phase = 0;
            for (int x = 54; x < ROAD_LENGTH; x += 54) { // 54 * 7.5 = 405m
                trafficLightsH.add(new TrafficLight(new Point2D.Double(x, 0), RED_DURATION, GREEN_DURATION, phase));
                phase += PHASE_BETWEEN_TRAFFIC_LIGHTS; // The phase varies between lights
            }
            evolveTrafficLightsUntil(trafficLightsH, TIME);

            List<Car> carsH = new OvitoReader<Car>(Paths.get("in.txt")).importPositionsOvito(TIME, placeholders.size(), trafficLightsH.size());

            ar.edu.itba.ss.models.LiPumaNavas modelH = new ar.edu.itba.ss.models.LiPumaNavas(ROAD_LENGTH, MAX_SPEED, SECURITY_GAP, true, carsH, trafficLightsH, TIME);

            while (TIME < 300) { // TODO: parametrizar tiempo de simulación
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
