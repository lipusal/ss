package ar.edu.itba.ss.runners;

import ar.edu.itba.ss.particles.Car;
import ar.edu.itba.ss.particles.Particle;
import ar.edu.itba.ss.particles.TrafficLight;

import java.awt.*;
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
