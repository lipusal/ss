package ar.edu.itba.ss.runners;

import ar.edu.itba.ss.particles.Car;

import java.awt.geom.Point2D;
import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

public class SingleLaneRunner {

    /**
     * Generate a list of cars with V0 = 0 in random positions along the road with given length.
     *
     * @param carCount    Number of cars to generate
     * @param roadLength  Road length
     * @param minDistance Min distance between cars
     * @return The resulting cars
     */
    private List<Car> randomCars(int carCount, int roadLength, int minDistance) {
        // TODO: Consider minDistance? Maybe we can't have cars directly next to each other. That might require to
        // TODO: start this method from scratch

        // Build range from 0 to roadLength (exclusive)
        List<Integer> allPositions = IntStream
                .range(0, roadLength)
                .boxed()
                .collect(Collectors.toList());
        // Shuffle it
        Collections.shuffle(allPositions);
        // Return the first carCount positions, mapped to cars
        return allPositions.stream()
                .limit(carCount)
                .map(position -> new Car(new Point2D.Double(position, 0)))
                .collect(Collectors.toList());
    }
}
