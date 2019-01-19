package ar.edu.itba.ss;

import ar.edu.itba.ss.files.OvitoWriter;
import ar.edu.itba.ss.models.KSSS;
import ar.edu.itba.ss.models.LiPumaNavasModel;
import ar.edu.itba.ss.models.NaSchModel;
import ar.edu.itba.ss.particles.Car;
import ar.edu.itba.ss.particles.Particle;
import ar.edu.itba.ss.particles.TrafficLight;

import java.awt.*;
import java.awt.geom.Point2D;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

public class SingleLane {

    public static void main(String[] args) throws IOException {
        final int ROAD_LENGTH = 2000,
                MAX_SPEED = 20;
        final double P = 0;
        final int car_radius = 1;
        OvitoWriter<Particle> ovitoWriter = new OvitoWriter<>(Paths.get("out.txt"));

        List<Car> placeholders = new ArrayList<>(2);

        /* *************************************************************************************************************
         *                                          HORIZONTAL MODEL
         * ************************************************************************************************************/
        placeholders.add(new Car(new Point2D.Double(0, ROAD_LENGTH/2.0), 0.1).fake());
        placeholders.add(new Car(new Point2D.Double(ROAD_LENGTH, ROAD_LENGTH/2.0), 0.1).fake());

        List<Car> carsH = new ArrayList<>();
        carsH.add(new Car(new Point2D.Double(0, ROAD_LENGTH/2.0), new Point2D.Double(2, 0), car_radius));
        carsH.add(new Car(new Point2D.Double(10, ROAD_LENGTH/2.0), new Point2D.Double(1, 0), car_radius));
//        cars.add(new Car(new Point2D.Double(7, 0), new Point2D.Double(2, 0)));
        carsH.add(new Car(new Point2D.Double(20, ROAD_LENGTH/2.0), car_radius));

        List<TrafficLight> trafficLightsH = new ArrayList<>();
        trafficLightsH.add(new TrafficLight(new Point2D.Double(ROAD_LENGTH/2.0 - 5, ROAD_LENGTH/2.0), 25, /*TODO calculate this*/10, 50, 0));
//        LiPumaNavasModel modelH = new LiPumaNavasModel(ROAD_LENGTH, true, MAX_SPEED, carsH, trafficLightsH);

        KSSS modelH = new KSSS(ROAD_LENGTH, MAX_SPEED, 5, carsH);
//        NaSchModel modelH = new NaSchModel(ROAD_LENGTH, MAX_SPEED, P, carsH);
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

    private static List<Color> colors(List<Car> carsWithPlaceholders) {
        Color[] c = new Color[] { Color.RED, Color.BLUE, Color.CYAN };
        int max = c.length;
        return carsWithPlaceholders.stream().map(car -> car.isFake() ? Color.GREEN : c[car.getId() % max]).collect(Collectors.toList());
    }
}
