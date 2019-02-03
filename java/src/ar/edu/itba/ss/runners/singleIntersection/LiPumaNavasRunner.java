package ar.edu.itba.ss.runners.singleIntersection;

import ar.edu.itba.ss.files.OvitoWriter;
import ar.edu.itba.ss.models.LiPumaNavas;
import ar.edu.itba.ss.particles.Car;
import ar.edu.itba.ss.particles.Particle;
import ar.edu.itba.ss.particles.TrafficLight;
import ar.edu.itba.ss.runners.Runner;

import java.awt.geom.Point2D;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

public class LiPumaNavasRunner extends Runner{

    public static void main(String[] args) throws IOException {
        final int ROAD_LENGTH = 1000,
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
        carsH.add(new Car(new Point2D.Double(30, ROAD_LENGTH/2.0), car_radius));
        carsH.add(new Car(new Point2D.Double(40, ROAD_LENGTH/2.0), car_radius));
        carsH.add(new Car(new Point2D.Double(50, ROAD_LENGTH/2.0), car_radius));

        List<TrafficLight> trafficLightsH = new ArrayList<>();
        trafficLightsH.add(new TrafficLight(new Point2D.Double(ROAD_LENGTH/2.0 - 5, ROAD_LENGTH/2.0), 50, 50, 0));
        trafficLightsH.get(0).setDrawPosition(new Point2D.Double(ROAD_LENGTH/2.0 + 10, ROAD_LENGTH/2.0));
        LiPumaNavas modelH = new LiPumaNavas(ROAD_LENGTH, MAX_SPEED, 3, true, carsH, trafficLightsH);

        /* *************************************************************************************************************
         *                                          VERTICAL MODEL
         * ************************************************************************************************************/
        placeholders.add(new Car(new Point2D.Double(ROAD_LENGTH/2.0, 0), 0.1).fake());
        placeholders.add(new Car(new Point2D.Double(ROAD_LENGTH/2.0, ROAD_LENGTH), 0.1).fake());

        List<Car> carsV = new ArrayList<>();
        carsV.add(new Car(new Point2D.Double(ROAD_LENGTH/2.0, 0), new Point2D.Double(0, 2), car_radius));
        carsV.add(new Car(new Point2D.Double(ROAD_LENGTH/2.0, 10), new Point2D.Double(0, 1), car_radius));
//        cars.add(new Car(new Point2D.Double(7, 0), new Point2D.Double(2, 0)));
        carsV.add(new Car(new Point2D.Double(ROAD_LENGTH/2.0, 20), car_radius));

        List<TrafficLight> trafficLightsV = new ArrayList<>();
        trafficLightsV.add(new TrafficLight(new Point2D.Double(ROAD_LENGTH/2.0, ROAD_LENGTH/2.0 - 5), 50, 50, 50));
        trafficLightsV.get(0).setDrawPosition(new Point2D.Double(ROAD_LENGTH/2.0, ROAD_LENGTH/2.0  + 10));
        LiPumaNavas modelV = new LiPumaNavas(ROAD_LENGTH, MAX_SPEED, 3, false, carsV, trafficLightsV);


//        KSSS model = new KSSS(ROAD_LENGTH, MAX_SPEED, cars);
//        NaSch model = new NaSch(ROAD_LENGTH, MAX_SPEED, P, cars);
        int t = 0;
        while (t < 500) { // TODO: parametrizar tiempo de simulación
            List<Particle> allCars = withPlaceholders(placeholders, carsH);
            allCars.addAll(carsV);
            allCars.addAll(trafficLightsH);
            allCars.addAll(trafficLightsV);
            ovitoWriter.exportPositions(allCars, t);
            carsH = modelH.evolve();
            carsV = modelV.evolve();
            t++;
        }
        ovitoWriter.close();
    }

}
