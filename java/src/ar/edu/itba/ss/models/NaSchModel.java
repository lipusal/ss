package ar.edu.itba.ss.models;

import ar.edu.itba.ss.particles.Car;
import ar.edu.itba.ss.particles.Particle;

import java.util.*;

/**
 * Nagel-Schreckenberg model implementation with periodic boundary conditions. This model simulates one-lane traffic.
 * All traffic moves along the X axis to the right. Periodic boundary conditions means that traffic exiting to the right
 * reappears on the left.  This model does not contemplate collisions.
 *
 * @see <a href="https://es.wikipedia.org/wiki/Modelo_Nagel-Schreckenberg">Wikipedia entry</a>.
 */
public class NaSchModel extends Model<Car> {

    private final int roadLength, maxSpeed;
    private final double p;
    private final Random random;

    /**
     * Instances a new Na-Sch model.
     *  @param roadLength  Road length.
     * @param maxSpeed    Maximum speed that any one car is allowed to reach.
     * @param p           Probability of a <b>moving</b> car to randomly reduce speed. If 0, this model is deterministic.
     * @param cars        The cars themselves. <b>PRECONDITIONS:</b>
*                    <ul>
*                      <li>Cars are listed in order, ie. car #2 MUST be to the right of car #1.</li>
*                      <li>Cars do not overlap</li>
*                      <li>0 <= x <= roadLength for each car</li>
*                      <li>0 <= Vx <= maxSpeed for each car</li>
     */
    public NaSchModel(int roadLength, int maxSpeed, double p, List<Car> cars) {
        super(cars);
        this.roadLength = roadLength;
        this.maxSpeed = maxSpeed;
        this.p = p;
        this.random = new Random();
        validateCars(cars);
    }

    private void validateCars(List<Car> cars) throws IllegalArgumentException {
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

    @Override
    public List<Car> evolve() {
        // Get new velocities
        for (int i = 0; i < particles.size(); i++) {
            Car currentCar = particles.get(i), carAhead = getCarAhead(i);
            double newSpeed;
            // Rule 1: Accelerate if we haven't reached top speed
            newSpeed = Math.min(currentCar.getVX()+1, maxSpeed);
            // Rule 2: Slow down if close to other cars
            newSpeed = Math.min(newSpeed, currentCar.distanceTo(carAhead)-1);
            // Rule 3: Brake at random if not already stopped
            if (newSpeed > 0 && p > 0 && random.nextDouble() <= p) {
                newSpeed--;
            }
            currentCar.setVx((int) newSpeed);
        }
        // Advance cars by their velocities, and return a SORTED list (see precondition in constructor)
        Set<Car> sortedCars = new TreeSet<>(Comparator.comparingDouble(Particle::getX)); // Leftmost car will be first
        particles.forEach(car -> {
            car.advanceForward((int) car.getVX());
            if (car.getX() > roadLength) {
                // Out bounds; wrap around (periodic boundary conditions), add first in list rather than last
                car.setX((int) car.getX() - roadLength);
            }
            sortedCars.add(car);
        });
        particles = new ArrayList<>(sortedCars);
        // Make sure we didn't break anything. Re-throw IllegalArgument as IllegalState exceptions
        try {
            validateCars(particles);
        } catch (IllegalArgumentException e) {
            throw new IllegalStateException(e);
        }
        return particles;
    }
    
    private Car getCarAhead(int index) {
//        if (index == particles.size() - 1) {
////            System.out.println("WARNING: Wrapping around road to get next car, confirm whether you want this");;
//            return null;
//        } else {
//            return particles.get(index + 1);
//        }
        return particles.get((index + 1) % particles.size());   // Periodic boundary conditions (ie. the rightmost car has the leftmost car ahead)
    }

    @Override
    public String toString() {
        StringBuilder result = new StringBuilder("[");
        int carIndex = 0;
        for (int i = 0; i < roadLength; i++) {
            Car currentCar = carIndex < particles.size() ? particles.get(carIndex) : null;
            if (currentCar != null && currentCar.getX() == i) {
                result.append(String.format("%03d", currentCar.getId()));
                carIndex++;
            } else {
                result.append("___");
            }
            if (i < roadLength - 1) {
                result.append(',');
            }
        }
        result.append(']');
        return result.toString();
    }
}
