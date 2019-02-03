package ar.edu.itba.ss.runners.singleLane;

import ar.edu.itba.ss.files.OvitoWriter;
import ar.edu.itba.ss.particles.Car;
import ar.edu.itba.ss.particles.Particle;
import ar.edu.itba.ss.particles.TrafficLight;

import java.awt.geom.Point2D;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

public class LiPumaNavas {

    @SuppressWarnings("Duplicates")
    public static void main(String[] args) throws IOException {
        final int ROAD_LENGTH = 1000,
                MAX_SPEED = 20;
        final int car_radius = 1;
        OvitoWriter<Particle> ovitoWriter = new OvitoWriter<>(Paths.get("out.txt"));

        List<Car> placeholders = new ArrayList<>(2);

        /* *************************************************************************************************************
         *                                          HORIZONTAL MODEL
         * ************************************************************************************************************/
        placeholders.add(new Car(new Point2D.Double(0, ROAD_LENGTH/2.0 + 20), 0.1).fake());
        placeholders.add(new Car(new Point2D.Double(ROAD_LENGTH, ROAD_LENGTH/2.0 - 20), 0.1).fake());

        List<Car> carsH = new ArrayList<>();
        carsH.add(new Car(new Point2D.Double(0, ROAD_LENGTH/2.0), new Point2D.Double(2, 0), car_radius));
        carsH.add(new Car(new Point2D.Double(10, ROAD_LENGTH/2.0), new Point2D.Double(1, 0), car_radius));
//        cars.add(new Car(new Point2D.Double(7, 0), new Point2D.Double(2, 0)));
        carsH.add(new Car(new Point2D.Double(20, ROAD_LENGTH/2.0), car_radius));

        List<TrafficLight> trafficLightsH = new ArrayList<>();
        trafficLightsH.add(new TrafficLight(new Point2D.Double(ROAD_LENGTH/2.0 - 5, ROAD_LENGTH/2.0), 25, /*TODO calculate this*/10, 50));
        trafficLightsH.get(0).setDrawPosition(new Point2D.Double(ROAD_LENGTH/2.0 - 5, ROAD_LENGTH/2.0 - 10));
        ar.edu.itba.ss.models.LiPumaNavas modelH = new ar.edu.itba.ss.models.LiPumaNavas(ROAD_LENGTH, MAX_SPEED, 3, true, carsH, trafficLightsH);

        int t = 0;
        while (t < 500) { // TODO: parametrizar tiempo de simulación
            List<Particle> allCars = withPlaceholders(placeholders, carsH);
            allCars.addAll(trafficLightsH);
            ovitoWriter.exportPositions(allCars, t);
            carsH = modelH.evolve();
            t++;
        }
        ovitoWriter.close();
    }

    private static List<Particle> withPlaceholders(List<Car> placeholders, List<Car> cars) {
        List<Particle> result = new ArrayList<>(cars);
        result.addAll(placeholders);
        return result;
    }
}
