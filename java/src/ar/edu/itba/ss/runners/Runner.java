package ar.edu.itba.ss.runners;

import ar.edu.itba.ss.particles.Car;
import ar.edu.itba.ss.particles.Particle;
import ar.edu.itba.ss.particles.TrafficLight;

import java.awt.*;
import java.awt.geom.Point2D;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

public abstract  class Runner {

    protected static List<Particle> withPlaceholders(List<Car> placeholders, List<Car> cars) {
        List<Particle> result = new ArrayList<>(cars);
        result.addAll(placeholders);
        return result;
    }

    protected static List<Color> colors(List<Car> carsWithPlaceholders) {
        Color[] c = new Color[] { Color.RED, Color.BLUE, Color.CYAN };
        int max = c.length;
        return carsWithPlaceholders.stream().map(car -> car.isFake() ? Color.GREEN : c[car.getId() % max]).collect(Collectors.toList());
    }

    /**
     * Generates a list of cars that are evenly distributed with the same initial velocity and car radius
     * @param amountOfCars that will be generated
     * @param roadLength to distribute the cars in a uniform way
     * @param carRadius for all the cars that are generated
     * @param initialVelocity for all the cars that are generated
     * @return list of generated cars
     */
    protected static List<Car> generateCars(int amountOfCars, int roadLength, int carRadius, int initialVelocity){
        List<Car> cars = new ArrayList<>();
        for (int i=0; i<roadLength; i+=(roadLength/amountOfCars)){
            cars.add(new Car(new Point2D.Double(i, 0), new Point2D.Double(initialVelocity, 0), carRadius));
        }
        return cars;
    }

    /**
     * Evolve the given traffic lights for a specified number of seconds. Useful when reconstructing a previous run for
     * debugging purposes.
     *
     * @param trafficLights Traffic lights to evolve.
     * @param time          Time to evolve until.
     */
    protected static void evolveTrafficLightsUntil(List<TrafficLight> trafficLights, int time) {
        for (int i = 0; i < time; i++) {
            for (TrafficLight t : trafficLights) {
                t.evolve(i);
            }
        }
    }
}
