package ar.edu.itba.ss;

import ar.edu.itba.ss.files.OvitoWriter;
import ar.edu.itba.ss.models.KSSS;
import ar.edu.itba.ss.particles.Car;

import java.awt.*;
import java.awt.geom.Point2D;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

public class Main {

    public static void main(String[] args) throws IOException {
        final int ROAD_LENGTH = 2000,
                MAX_SPEED = 20;
        final double P = 0;
        final int car_radius = 5;
        OvitoWriter<Car> ovitoWriter = new OvitoWriter<>(Paths.get("out.txt"));

        List<Car> placeholders = new ArrayList<>(2);
        placeholders.add(new Car(new Point2D.Double(0, 0), 0.1).fake());
        placeholders.add(new Car(new Point2D.Double(ROAD_LENGTH, 0), 0.1).fake());

        List<Car> cars = new ArrayList<>();
        cars.add(new Car(new Point2D.Double(0, 0), new Point2D.Double(2, 0), car_radius));
        cars.add(new Car(new Point2D.Double(10, 0), new Point2D.Double(1, 0), car_radius));
//        cars.add(new Car(new Point2D.Double(7, 0), new Point2D.Double(2, 0)));
        cars.add(new Car(new Point2D.Double(20, 0), car_radius));

        KSSS model = new KSSS(ROAD_LENGTH, MAX_SPEED, cars);
//        NaSchModel model = new NaSchModel(ROAD_LENGTH, MAX_SPEED, P, cars);
        int t = 0;
        while (t < 100) { // TODO: parametrizar tiempo de simulación
            System.out.println(model);
            List<Car> allCars = withPlaceholders(placeholders, cars);
            ovitoWriter.exportPositions(allCars, t, colors(allCars), car -> Double.toString(car.getRadius()));
            cars = model.evolve();
            t++;
        }
        ovitoWriter.close();
    }

    private static List<Car> withPlaceholders(List<Car> placeholders, List<Car> cars) {
        List<Car> result = new ArrayList<>(cars);
        result.addAll(placeholders);
        return result;
    }

    private static List<Color> colors(List<Car> carsWithPlaceholders) {
        Color[] c = new Color[] { Color.RED, Color.BLUE, Color.CYAN };
        int max = c.length;
        return carsWithPlaceholders.stream().map(car -> car.isFake() ? Color.GREEN : c[car.getId() % max]).collect(Collectors.toList());
    }
}
