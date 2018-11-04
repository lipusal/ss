package ar.edu.itba.ss.models;

import ar.edu.itba.ss.particles.Car;

import java.util.List;
import java.util.Objects;

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

    protected void validateCars(List<Car> cars, int roadLength, int maxSpeed) throws IllegalArgumentException {
        for (int i = 0; i < cars.size(); i++) {
            Car current = cars.get(i),
                    carAhead = i < cars.size() - 1 ? getCarAhead(i) : null; // Don't want to wrap around here
            // 1) Cars are listed in order, and
            // 2) Cars do not overlap
            if (carAhead != null) {
                if (current.getX() > carAhead.getX()) {
                    throw new IllegalArgumentException(String.format("%s and %s are not listed in order (%g > %g)", current, carAhead, current.getX(), carAhead.getX()));
                } else if (current.getX() == carAhead.getX()) {
                    throw new IllegalArgumentException(String.format("%s and %s overlap (same X coordinate)", current, carAhead));
                }
            }
            // 3) Position
            if (current.getX() < 0 || current.getX() > roadLength) {
                throw new IllegalArgumentException(String.format("%s is outside of bounds ([%d <= x <= %d, but x=%g])", current, 0, roadLength, current.getX()));
            }
            // 4) Speed
            if (current.getVX() < 0) {
                throw new IllegalArgumentException(String.format("%s is going to the left (%g)", current, current.getVX()));
            }
            if (current.getVX() > maxSpeed) {
                throw new IllegalArgumentException(String.format("%s is going too fast (%g, max speed is %d)", current, current.getVX(), maxSpeed));
            }
        }
    }
}
