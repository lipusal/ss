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
public class NaSchModel extends SingleLaneModel {

    private final int maxSpeed;
    private final double p;
    private final Random random;

    /**
     * Instances a new Na-Sch model.
     * @param roadLength  Road length.
     * @param maxSpeed    Maximum speed that any one car is allowed to reach.
     * @param p           Probability of a <b>moving</b> car to randomly reduce speed. If 0, this model is deterministic.
     * @param horizontal  Whether the road is horizontal or vertical.
     * @param cars        The cars themselves. <b>PRECONDITIONS:</b>
     *                    <ul>
     *                      <li>Cars are listed in order, ie. car #2 MUST be to the right of car #1.</li>
     *                      <li>Cars do not overlap</li>
     *                      <li>0 <= x <= roadLength for each car</li>
     *                      <li>0 <= Vx <= maxSpeed for each car</li>
     */
    public NaSchModel(int roadLength, int maxSpeed, double p, boolean horizontal, List<Car> cars) {
        super(cars, roadLength, horizontal);
        this.maxSpeed = maxSpeed;
        this.p = p;
        this.random = new Random();
        validateCars(cars, roadLength, maxSpeed);
    }

    /**
     * Equivalent to {@code NaSchModel(roadLength, maxSpeed, p, true, cars)}.
     */
    public NaSchModel(int roadLength, int maxSpeed, double p, List<Car> cars) {
        this(roadLength, maxSpeed, p, true, cars);
    }


    @Override
    public List<Car> evolve() {
        // Get new velocities
        for (int i = 0; i < particles.size(); i++) {
            Car currentCar = particles.get(i), carAhead = getCarAhead(i);
            double currentSpeed = getVelocityComponent(currentCar), newSpeed;
            // Rule 1: Accelerate if we haven't reached top speed
            newSpeed = Math.min(currentSpeed + 1, maxSpeed);

            // Rule 2: Slow down if close to other cars
            int b = wrapAroundDistance(currentCar, carAhead) - 1;
            // Turn on brake lights if appropriate. Brake lights are not part of this model, they are merely for visualization.
            if (b < newSpeed) {
                currentCar.turnBrakeLightsOn();
            }
            newSpeed = Math.min(newSpeed, b);

            // Rule 3: Brake at random if not already stopped
            if (newSpeed > 0 && p > 0 && random.nextDouble() <= p) {
                newSpeed--;
                currentCar.turnBrakeLightsOn();
            }
            // Turn off brake lights if accelerating
            if (newSpeed > currentSpeed) {
                currentCar.turnBrakeLightsOff();
            }
            setVelocityComponent(currentCar, newSpeed);
        }
        // Advance cars by their velocities, and return a SORTED list (see precondition in constructor)
        Set<Car> sortedCars = new TreeSet<>(Comparator.comparingDouble(this::getPositionComponent)); // Leftmost car will be first
        particles.forEach(car -> {
            double newPosition = getPositionComponent(car) + getVelocityComponent(car);
            if (newPosition > roadLength) {
                // Out bounds; wrap around (periodic boundary conditions), add first in list rather than last
                newPosition -= roadLength;
            }
            setPositionComponent(car, newPosition);
            sortedCars.add(car);
        });
        particles = new ArrayList<>(sortedCars);
        // Make sure we didn't break anything. Re-throw IllegalArgument as IllegalState exceptions
        try {
            validateCars(particles, roadLength, maxSpeed);
        } catch (IllegalArgumentException e) {
            throw new IllegalStateException(e);
        }
        return particles;
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
