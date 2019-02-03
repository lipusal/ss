package ar.edu.itba.ss.runners;

import ar.edu.itba.ss.particles.Car;
import ar.edu.itba.ss.particles.Particle;

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
}
