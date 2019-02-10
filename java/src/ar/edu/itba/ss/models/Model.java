package ar.edu.itba.ss.models;

import ar.edu.itba.ss.particles.Car;

import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;

public abstract class Model {

    protected List<Car> particles;

    public Model(List<Car> particles) {
        Objects.requireNonNull(particles);
        this.particles = particles;
    }

    /**
     * Evolves the model from its current state. Returns the particles resulting from one evolution step.
     *
     * @return The evolved particles.
     */
    public abstract List<Car> evolve();


    protected Car getCarAhead(int index) {
//        if (index == particles.size() - 1) {
////            System.out.println("WARNING: Wrapping around road to get next car, confirm whether you want this");;
//            return null;
//        } else {
//            return particles.get(index + 1);
//        }
        return particles.get((index + 1) % particles.size());   // Periodic boundary conditions (ie. the rightmost car has the leftmost car ahead)
    }

    /**
     * Validates that:
     * <ol>
     *     <li>Cars are listed in order (ie. for every i, j such that 0 <= i, j <= cars.length, then if i < j then car #i.x < car #j.x)</li>
     *     <li>Cars do not overlap</li>
     *     <li>Cars are within bounds ({@code 0 <= x <= roadLength})</li>
     *     <li>Cars speeds are within bounds ({@code 0 <= Vx <= maxSpeed})</li>
     * </ol>
     *
     * @param roadLength Road length, ie. high bound for X coordinate.
     * @param maxSpeed   High bound for Vx.
     * @throws IllegalStateException If any condition is not met.
     */
    protected void validateCars(int roadLength, int maxSpeed) throws IllegalStateException {
        for (int i = 0; i < particles.size(); i++) {
            Car current = particles.get(i),
                carAhead = i < particles.size() - 1 ? getCarAhead(i) : null; // Don't want to wrap around here
            // 1) Cars are listed in order, and
            // 2) Cars do not overlap
            if (carAhead != null) {
                if (current.getX() > carAhead.getX()) {
                    throw new IllegalStateException(String.format("%s and %s are not listed in order (%g > %g)", current, carAhead, current.getX(), carAhead.getX()));
                } else if (current.getX() == carAhead.getX()) {
                    throw new IllegalStateException(String.format("%s and %s overlap (same X coordinate)", current, carAhead));
                }
            }
            // 3) Position
            if (current.getX() < 0 || current.getX() > roadLength) {
                throw new IllegalStateException(String.format("%s is outside of bounds ([%d <= x <= %d, but x=%g])", current, 0, roadLength, current.getX()));
            }
            // 4) Speed
            if (current.getVX() < 0) {
                throw new IllegalStateException(String.format("%s is going to the left (%g)", current, current.getVX()));
            }
            if (current.getVX() > maxSpeed) {
                throw new IllegalStateException(String.format("%s is going too fast (%g, max speed is %d)", current, current.getVX(), maxSpeed));
            }
        }
    }

    /**
     * Copy a list of cars. Note that IDs are copied too.
     *
     * @param original Original cars to copy.
     * @return The copied cars.
     */
    List<Car> copyCars(List<Car> original) {
        return original.stream().map(Car::new).collect(Collectors.toList());
    }
}
