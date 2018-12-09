package ar.edu.itba.ss.runners;

import ar.edu.itba.ss.files.OvitoWriter;
import ar.edu.itba.ss.models.KSSS;
import ar.edu.itba.ss.particles.Car;
import ar.edu.itba.ss.particles.Particle;

import java.awt.geom.Point2D;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

import static ar.edu.itba.ss.util.CarUtils.randomCarsOnY;
import static ar.edu.itba.ss.util.OvitoUtils.withPlaceholders;

public class SingleLaneRunner {

    public static void main(String[] args) throws IOException {
        final int ROAD_LENGTH = 200,
                MAX_SPEED = 20;
        final double P = 0;
        final int car_radius = 5;
        OvitoWriter<Particle> ovitoWriter = new OvitoWriter<>(Paths.get("out.txt"));

        List<Car> placeholders = new ArrayList<>(2);
        placeholders.add(new Car(new Point2D.Double(0, 0), 0.1).fake());
        placeholders.add(new Car(new Point2D.Double(ROAD_LENGTH, 0), 0.1).fake());

        List<Car> cars = randomCarsOnY(10, ROAD_LENGTH, 0, 0);
        KSSS model = new KSSS(ROAD_LENGTH, MAX_SPEED, cars);
//        NaSchModel model = new NaSchModel(ROAD_LENGTH, MAX_SPEED, P, cars);
        int t = 0;
        while (t < 250) { // TODO: parametrizar tiempo de simulación
            List<Particle> allCars = withPlaceholders(placeholders, cars);
            ovitoWriter.exportPositions(allCars, t);
            cars = model.evolve();
            t++;
        }
        ovitoWriter.close();
    }


}
