package ar.edu.itba.ss;

import ar.edu.itba.ss.files.OvitoWriter;
import ar.edu.itba.ss.models.NaSchModel;
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
        final int ROAD_LENGTH = 20,
                MAX_SPEED = 2;
        final double P = 0;
        OvitoWriter<Car> ovitoWriter = new OvitoWriter<>(Paths.get("out.txt"));

        List<Car> placeholders = new ArrayList<>(2);
        placeholders.add(new Car(new Point(0, 0)).fake());
        placeholders.add(new Car(new Point(ROAD_LENGTH, 0)).fake());

        List<Car> cars = new ArrayList<>();
        cars.add(new Car(new Point(0, 0), new Point2D.Double(2, 0)));
        cars.add(new Car(new Point(3, 0), new Point2D.Double(1, 0)));
//        cars.add(new Car(new Point(7, 0), new Point2D.Double(2, 0)));
        cars.add(new Car(new Point(5, 0)));

//        KSSS model = new KSSS(ROAD_LENGTH, MAX_SPEED, cars);
        NaSchModel model = new NaSchModel(ROAD_LENGTH, MAX_SPEED, P, cars);
        int t = 0;
        while (t < 100) {
            System.out.println(model);
            List<Car> allCars = withPlaceholders(placeholders, cars);
            ovitoWriter.exportPositions(allCars, t, colors(allCars), null);
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
