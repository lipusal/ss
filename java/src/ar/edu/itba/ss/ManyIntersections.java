package ar.edu.itba.ss;

import ar.edu.itba.ss.files.OvitoWriter;
import ar.edu.itba.ss.models.LiPumaNavasModel;
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

@SuppressWarnings("ALL")
public class ManyIntersections {

    public static void main(String[] args) throws IOException {
        final int ROAD_LENGTH = 500,
                MAX_SPEED = 20;
        final double P = 0;
        final int car_radius = 5;
        OvitoWriter<Particle> ovitoWriter = new OvitoWriter<>(Paths.get("out.txt"));

        List<Car> placeholders = new ArrayList<>(2);

        List<List<Car>> carsList = new ArrayList<>();

        double firstStreetCoordinates = ROAD_LENGTH/3.0;
        double secondStreetCoordinates = 2*ROAD_LENGTH/3.0;

        /* *************************************************************************************************************
         *                                          HORIZONTAL MODELS
         * ************************************************************************************************************/
        /* FIRST HORIZONTAL STREET*/
        // Add placeholders for corners of the street
        placeholders.add(new Car(new Point2D.Double(0, firstStreetCoordinates), 0.1).fake());
        placeholders.add(new Car(new Point2D.Double(ROAD_LENGTH, firstStreetCoordinates), 0.1).fake());
        // Add cars
        List<Car> carsH = new ArrayList<>();
        carsH.add(new Car(new Point2D.Double(0, firstStreetCoordinates), new Point2D.Double(2, 0), car_radius));
        carsH.add(new Car(new Point2D.Double(10, firstStreetCoordinates), new Point2D.Double(1, 0), car_radius));
        carsH.add(new Car(new Point2D.Double(20, firstStreetCoordinates), car_radius));
        // Add traffic light
        List<TrafficLight> trafficLightsH = new ArrayList<>();
        trafficLightsH.add(new TrafficLight(1, new Point2D.Double(firstStreetCoordinates - 5, firstStreetCoordinates), 25, 50, 0));
        trafficLightsH.add(new TrafficLight(1, new Point2D.Double(firstStreetCoordinates - 5, secondStreetCoordinates), 25, 50, 0));
        LiPumaNavasModel modelH = new LiPumaNavasModel(ROAD_LENGTH, true, MAX_SPEED, carsH, trafficLightsH);

        /* SECOND HORIZONTAL STREET*/
        // Add placeholders for corners of the street
        placeholders.add(new Car(new Point2D.Double(0, secondStreetCoordinates), 0.1).fake());
        placeholders.add(new Car(new Point2D.Double(ROAD_LENGTH, secondStreetCoordinates), 0.1).fake());
        // Add cars
        List<Car> carsH2 = new ArrayList<>();
        carsH2.add(new Car(new Point2D.Double(0, secondStreetCoordinates), new Point2D.Double(2, 0), car_radius));
        carsH2.add(new Car(new Point2D.Double(10, secondStreetCoordinates), new Point2D.Double(1, 0), car_radius));
        carsH2.add(new Car(new Point2D.Double(20, secondStreetCoordinates), car_radius));
        // Add traffic light
        List<TrafficLight> trafficLightsH2 = new ArrayList<>();
        trafficLightsH2.add(new TrafficLight(1, new Point2D.Double(secondStreetCoordinates - 5, firstStreetCoordinates), 25, 50, 0));
        trafficLightsH2.add(new TrafficLight(1, new Point2D.Double(secondStreetCoordinates - 5, secondStreetCoordinates), 25, 50, 0));
        LiPumaNavasModel modelH2 = new LiPumaNavasModel(ROAD_LENGTH, true, MAX_SPEED, carsH2, trafficLightsH2);

        /* *************************************************************************************************************
         *                                          VERTICAL MODELS
         * ************************************************************************************************************/
        /* FIRST VERTICAL STREET*/
        // Add traffic light
        placeholders.add(new Car(new Point2D.Double(firstStreetCoordinates, 0), 0.1).fake());
        placeholders.add(new Car(new Point2D.Double(firstStreetCoordinates, ROAD_LENGTH), 0.1).fake());
        // Add cars
        List<Car> carsV = new ArrayList<>();
        carsV.add(new Car(new Point2D.Double(firstStreetCoordinates, 0), new Point2D.Double(0, 2), car_radius));
        carsV.add(new Car(new Point2D.Double(firstStreetCoordinates, 10), new Point2D.Double(0, 1), car_radius));
        carsV.add(new Car(new Point2D.Double(firstStreetCoordinates, 20), car_radius));
        // Add traffic lights
        List<TrafficLight> trafficLightsV = new ArrayList<>();
        trafficLightsV.add(new TrafficLight(1, new Point2D.Double(firstStreetCoordinates, firstStreetCoordinates - 5), 50, 25, 25));
        trafficLightsV.add(new TrafficLight(1, new Point2D.Double(firstStreetCoordinates, secondStreetCoordinates - 5), 50, 25, 25));
        LiPumaNavasModel modelV = new LiPumaNavasModel(ROAD_LENGTH, false, MAX_SPEED, carsV, trafficLightsV);

        /* SECOND VERTICAL STREET*/
        placeholders.add(new Car(new Point2D.Double(ROAD_LENGTH/2.0, 0), 0.1).fake());
        placeholders.add(new Car(new Point2D.Double(ROAD_LENGTH/2.0, ROAD_LENGTH), 0.1).fake());
        // Add cars
        List<Car> carsV2 = new ArrayList<>();
        carsV2.add(new Car(new Point2D.Double(secondStreetCoordinates, 0), new Point2D.Double(0, 2), car_radius));
        carsV2.add(new Car(new Point2D.Double(secondStreetCoordinates, 10), new Point2D.Double(0, 1), car_radius));
        carsV2.add(new Car(new Point2D.Double(secondStreetCoordinates, 20), car_radius));
        // Add traffic lights
        List<TrafficLight> trafficLightsV2 = new ArrayList<>();
        trafficLightsV.add(new TrafficLight(1, new Point2D.Double(secondStreetCoordinates, firstStreetCoordinates - 5), 50, 25, 25));
        trafficLightsV.add(new TrafficLight(1, new Point2D.Double(secondStreetCoordinates, secondStreetCoordinates - 5), 50, 25, 25));
        LiPumaNavasModel modelV2 = new LiPumaNavasModel(ROAD_LENGTH, false, MAX_SPEED, carsV2, trafficLightsV2);

        int t = 0;
        while (t < 500) { // TODO: parametrizar tiempo de simulación
            // Add cars and placeholders
            List<Particle> allCars = withPlaceholders(placeholders, carsH);
            allCars.addAll(carsV);
            allCars.addAll(carsH2);
            allCars.addAll(carsV2);
            // Add the traffic lights
            allCars.addAll(trafficLightsH);
            allCars.addAll(trafficLightsH2);
            allCars.addAll(trafficLightsV);
            allCars.addAll(trafficLightsV2);
            // Export ovito positions
            ovitoWriter.exportPositions(allCars, t);
            // Evolve all the models
            carsH = modelH.evolve();
            carsV = modelV.evolve();
            carsH2 = modelH2.evolve();
            carsV2 = modelV2.evolve();
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
