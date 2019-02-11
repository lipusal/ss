package ar.edu.itba.ss.models;

import ar.edu.itba.ss.particles.Car;
import ar.edu.itba.ss.particles.Particle;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Specification of {@link Model} for a single-lane road model with periodic boundary conditions (ie. cars wrap around
 * from the right back to the left).
 */
public abstract class SingleLaneModel extends Model {

    protected final int roadLength;
    /**
     * Whether the lane travels in horizontal (left-to-right) or vertical (bottom-to-top) direction.
     */
    protected final boolean isHorizontal;

    private final List<Integer> originalParticleOrder;
    private final boolean autoFix;

    /**
     * Instances a new horizontal or vertical single-lane model of the specified length.
     *  @param particles  Particles that compose the model.
     * @param roadLength  Road length.
     * @param horizontal  Whether the model is horizontal (if false, it's vertical).
     * @param autoFix     Whether to automatically fix violations.
     */
    public SingleLaneModel(List<Car> particles, int roadLength, boolean horizontal, boolean autoFix) {
        super(particles);
        this.roadLength = roadLength;
        this.isHorizontal = horizontal;
        this.originalParticleOrder = particles.stream().map(Particle::getId).collect(Collectors.toList());
        this.autoFix = autoFix;
    }

    /**
     * Equivalent to {@code SingleLaneModel(particles, roadLength, horizontal, true)}
     */
    public SingleLaneModel(List<Car> particles, int roadLength, boolean horizontal) {
        this(particles, roadLength, horizontal, true);
    }

    /**
     * Distance between two particles considering periodic boundary conditions. <b>NOTE:</b> Be careful and ensure that
     * you don't pass the first particle as the second particle and vice-versa! <b>You will get incorrect results</b>.
     *
     * @param firstParticle First particle (left for horizontal models, bottom for vertical models).
     * @param secondParticle Second particle (right for horizontal models, top for vertical).
     * @return The distance between the particles considering periodic boundary conditions.
     */
    protected int wrapAroundDistance(Particle firstParticle, Particle secondParticle) {
        int result = (int) firstParticle.distanceTo(secondParticle);
        if (getPositionComponent(secondParticle) < getPositionComponent(firstParticle)) {
            // eg. __R_L_____, must get distance wrapping around, not direct distance
            result = roadLength - result;
        }
        return result;
    }

    /**
     * Equivalent to {@link Model#validateCars(int, int)} but is direction-independent.
     * <b>NOTE:</b> If {@link #autoFix} is set, this corrects overlap and backwards-velocity errors, modifying {@link #particles}
     * (re-sorting if necessary).
     *
     * @see Model#validateCars(int, int)
     */
    @Override
    protected void validateCars(int roadLength, int maxSpeed) throws IllegalStateException {
        boolean autoFixed = false;
        for (int i = 0; i < particles.size(); i++) {
            Car current = particles.get(i),
                carAhead = i < particles.size() - 1 ? getCarAhead(i) : null; // Don't want to wrap around here
            // 1) Cars are listed in order, and
            // 2) Cars do not overlap
            if (carAhead != null) {
                if (getPositionComponent(current) > getPositionComponent(carAhead)) {
                    throw new IllegalStateException(String.format("%s and %s are not listed in order (%g > %g)", current, carAhead, getPositionComponent(current), getPositionComponent(carAhead)));
                } else if (getPositionComponent(current) == getPositionComponent(carAhead)) {
                    if (autoFix) {
                        System.out.println("Overlap error, auto-fixing");
                        fixOverlap(roadLength, i, (i+1) % roadLength);
                        autoFixed = true;
                    } else {
                        throw new IllegalStateException(String.format("%s and %s overlap at %s = %g)", current, carAhead, componentAxis(), getPositionComponent(current)));
                    }
                }
            }
            // 3) Position
            if (getPositionComponent(current) < 0 || getPositionComponent(current) > roadLength) {
                throw new IllegalStateException(String.format("%s is outside of bounds (%d <= %s <= %d, but %s = %g)", current, 0, componentAxis(), roadLength, componentAxis(), getPositionComponent(current)));
            }
            // 4) Speed
            if (getVelocityComponent(current) < 0) {
                if (autoFix) {
                    System.out.println("Backwards velocity error, auto-fixing");
                    fixGoingBackwards(i);
                    autoFixed = true;
                } else {
                    throw new IllegalStateException(String.format("%s is going backwards (%g)", current, getVelocityComponent(current)));
                }
            }
            if (getVelocityComponent(current) > maxSpeed) {
                throw new IllegalStateException(String.format("%s is going too fast (%g, max speed is %d)", current, getVelocityComponent(current), maxSpeed));
            }
        }
        if (autoFixed) {
            // Car order potentially changed, re-sort
            particles.sort(Comparator.comparingDouble(this::getPositionComponent));
        }
    }

    /**
     * For overlapping cars, moves first car backwards. Never move a car forward, as some models have traffic lights
     * which are not in scope here. If moving a car backwards creates another conflict, solve it recursively.
     *
     * @param roadLength     Road length.
     * @param firstCarIndex  First car index.
     * @param secondCarIndex Second car index.
     * @throws IllegalStateException When the overlap can't be solved (ie. moving cars backwards creates another overlap
     * all the way around).
     */
    private void fixOverlap(int roadLength, int firstCarIndex, int secondCarIndex) throws IllegalStateException {
        if (secondCarIndex == firstCarIndex) {
            throw new IllegalStateException("Could not fix overlap, wrapped around cars completely");
        }
        int previousCarIndex = wrapUnder(firstCarIndex, 1, particles.size());
        Car conflictingCar = particles.get(firstCarIndex),
            previousCar = particles.get(previousCarIndex);
        int newPosition = wrapUnder((int) getPositionComponent(conflictingCar), 1, roadLength);
        setPositionComponent(conflictingCar, newPosition);
        if (getPositionComponent(previousCar) == newPosition) {
            // Overlap, retry recursively
            fixOverlap(roadLength, previousCarIndex, firstCarIndex);
        }
    }

    private void fixGoingBackwards(int carIndex) {
        /*
        TODO NOW actually solve:
        - Advance position backwards as per velocity
        - Set velocity to 0
        - Fix overlaps
        - Or fix corrupted car order
         */
        setVelocityComponent(particles.get(carIndex), 0);
    }

    /**
     * Validates that the original particle order (ie. the one this model was instantiated with) has not been violated.
     * This is sometimes necessary as in {@link #evolve()} the car list is recreated with a {@link java.util.TreeSet}
     * ordered by position component, which guarantees that the first condition in {@link Model#validateCars(int, int)}
     * will be met. However, that method does not validate that car order was not disrupted, for example if one car
     * passed another.
     *
     * @throws IllegalStateException If original car order was violated (includes the case where cars are added or disappear
     * from the model).
     */
    protected void validateCarOrder() throws IllegalStateException {
        int listIndex = -1;
        // Find starting index. From here on, car order should be maintained (wrapping around if necessary)
        for (int i = 0; i < originalParticleOrder.size(); i++) {
            if (particles.get(i).getId() == originalParticleOrder.get(0)) {
                listIndex = i;
                break;
            }
        }
        if (listIndex == -1) {
            throw new IllegalStateException("Couldn't find leading car with ID #" + originalParticleOrder.get(0) + " in cars list");
        }
        for (int i = 0; i < originalParticleOrder.size(); i++) {
            int carIndex = (listIndex + i) % particles.size();
            if (particles.get(carIndex).getId() != originalParticleOrder.get(i)) {
                throw new IllegalStateException(String.format("Original car order was violated, %s != %s", originalParticleOrder.toString(), particles.stream().map(Particle::getId).collect(Collectors.toList()).toString()));
//                System.err.println(String.format("Original car order was violated, %s != %s", originalParticleOrder.toString(), particles.stream().map(Particle::getId).collect(Collectors.toList()).toString()));
            }
        }
    }

    /**
     * Given a list of cars and velocities, advance every car by its corresponding velocity (respecting periodic boundary
     * conditions, ie. wrapping around) and update its velocity. If specified, also update cars' brake lights.
     *
     * @param originalCars      Cars to advance.
     * @param newVelocities     New car velocities.
     * @param changeBrakeLights Whether brake lights should be modified (ie. turn off for accelerating cars, turn on for braking cars).
     * @return The new car list, <b>with cars in order</b> according to {@link #getPositionComponent(Particle)}.
     * @throws IllegalArgumentException If {@code originalCars.size() != newVelocities.size()}.
     */
    protected List<Car> advanceCars(List<Car> originalCars, List<Double> newVelocities, boolean changeBrakeLights) throws IllegalArgumentException {
        if (originalCars.size() != newVelocities.size()) {
            throw new IllegalArgumentException(String.format("Cars and velocities lists must match in length, %d != %d", originalCars.size(), newVelocities.size()));
        }
        List<Car> advancedCars = new ArrayList<>(originalCars.size());
        for (int i = 0; i < originalCars.size(); i++) {
            Car c = originalCars.get(i);
            double oldV = getVelocityComponent(c),
                    newV = newVelocities.get(i),
                    newPosition = (getPositionComponent(c) + newV) % roadLength; // Modulo for periodic boundary conditions
            setPositionComponent(c, newPosition);
            setVelocityComponent(c, newV);
            if (changeBrakeLights) {
                if (newV < oldV || newV == 0) {
                    c.turnBrakeLightsOn();
                } else {
                    c.turnBrakeLightsOff();
                }
            }
            advancedCars.add(c);
        }
        advancedCars.sort(Comparator.comparingDouble(this::getPositionComponent)); // Sort by position component
        return advancedCars;
    }

    /**
     * Equivalent to {@code advanceCars(originalCars, newVelocities, false)}.
     *
     * @see #advanceCars(List, List, boolean)
     */
    protected List<Car> advanceCars(List<Car> originalCars, List<Double> newVelocities) {
        return advanceCars(originalCars, newVelocities, false);
    }

    /* *****************************************************************************************************************
     *                                  BEGIN DIRECTION-INDEPENDENT HELPERS
     * The following methods help make concrete instances of this model work both horizontally and vertically.
     * ****************************************************************************************************************/

    /**
     * Gets the horizontal or vertical component of the specified particle's position, as appropriate for this model.
     */
    public double getPositionComponent(Particle particle) {
        return isHorizontal ? particle.getX() : particle.getY();
    }

    /**
     * Sets the horizontal or vertical component of the specified particle's position, as appropriate for this model.
     *
     * @param particle The particle.
     * @param newPosition The new position.
     */
    protected void setPositionComponent(Particle particle, double newPosition) {
        if (isHorizontal) {
            particle.setX(newPosition);
        } else {
            particle.setY(newPosition);
        }
    }

    /**
     * Gets the horizontal or vertical component of the specified particle's velocity, as appropriate for this model.
     */
    public double getVelocityComponent(Particle car) {
        return isHorizontal ? car.getVX() : car.getVY();
    }

    /**
     * Sets the horizontal or vertical component of the specified particle's velocity, as appropriate for this model.
     *
     * @param particle The particle.
     * @param newSpeed The new speed.
     */
    protected void setVelocityComponent(Particle particle, double newSpeed) {
        if (isHorizontal) {
            particle.setVx(newSpeed);
        } else {
            particle.setVy(newSpeed);
        }
    }

    private char componentAxis() {
        return isHorizontal ? 'x' : 'y';
    }

    /* *****************************************************************************************************************
     *                                      END DIRECTION-INDEPENDENT HELPERS
     * ****************************************************************************************************************/

    /**
     * Equivalent to {@code x - delta < 0 ? x - delta + max : x - delta}.
     *
     * @param x     Starting value
     * @param delta Amount to subtract
     * @param max   Upper bound if {@code x - delta < 0}.
     * @return The result.
     */
    private int wrapUnder(int x, int delta, int max) {
        int result = x - delta;
        if (result < 0) {
            result += max;
        }
        return result;
    }
}
