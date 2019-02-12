package ar.edu.itba.ss.models;

import ar.edu.itba.ss.particles.Car;
import ar.edu.itba.ss.particles.Particle;
import ar.edu.itba.ss.particles.TrafficLight;

import java.util.*;

/**
 * Modified version of KSSS that includes interaction with traffic lights
 */
@SuppressWarnings("Duplicates")
public class LiPumaNavas extends SingleLaneModel {
    protected int maxSpeed;

    protected int H = 6;
    /**
     * Probability of a stopped car to remain stopped.
     */
    protected double P0 = 0.5;
//    protected double P0 = 0;
    /**
     * Probability of a car who can see its car ahead to brake when needed.
     */
    protected double PB = 0.94;
//    protected double PB = 1;
    /**
     * Probability of a car to brake randomly.
     */
    protected double PD = 0.1;
//    protected double PD = 0;
    protected int securityGap;

    private int simTime;
    private final double maxDeceleration = -5;

    private List<TrafficLight> trafficLights = new ArrayList<>();

    /**
     * Map of car IDs to booleans indicating whether a car with a given ID is interacting with a traffic light. Used to
     * indicate when the first car in a group is braking for a traffic light, so the interaction propagates down the
     * group and cars interact differently.
     */
    private Map<Integer, Boolean> trafficLightInteractions;

    public LiPumaNavas(int roadLength, int maxSpeed, int securityGap, boolean horizontal, List<Car> cars, List<TrafficLight> trafficLights, int startTime, boolean autoFix) {
        super(cars, roadLength, horizontal, autoFix);
        this.maxSpeed = maxSpeed;
        this.securityGap = securityGap;
        this.trafficLights.addAll(trafficLights);
        this.simTime = startTime;
        // Initialize and populate traffic light interactions
        trafficLightInteractions = new HashMap<>(cars.size());
        cars.forEach(c -> trafficLightInteractions.put(c.getId(), false));

        validateCars(roadLength, maxSpeed);
    }

    /**
     * Equivalent to {@code LiPumaNavas(roadLength, maxSpeed, securityGap, horizontal, cars, trafficLights, 0);}
     * @see #LiPumaNavas(int, int, int, boolean, List, List, int, boolean)
     */
    public LiPumaNavas(int roadLength, int maxSpeed, int securityGap, boolean horizontal, List<Car> cars, List<TrafficLight> trafficLights) {
        this(roadLength, maxSpeed, securityGap, horizontal, cars, trafficLights, 0, true);
    }

    /**
     * Equivalent to {@code LiPumaNavas(roadLength, maxSpeed, securityGap, true, cars, trafficLights)}.
     *
     * @see #LiPumaNavas(int, int, int, boolean, List, List)
     */
    public LiPumaNavas(int roadLength, int maxSpeed, int securityGap, List<Car> cars, List<TrafficLight> trafficLights) {
        this(roadLength, maxSpeed, securityGap, true, cars, trafficLights);
    }

    /**
     * Equivalent to {@link #LiPumaNavas(int, int, int, boolean, List, List)} original constructor} with overrides
     * for different probability parameters.
     */
    public LiPumaNavas(int roadLength, int maxSpeed, int securityGap, boolean horizontal, double P0, double Pb, double Pd, List<Car> cars, List<TrafficLight> trafficLights) {
        this(roadLength, maxSpeed, securityGap, horizontal, cars, trafficLights);
        this.P0 = P0;
        this.PB = Pb;
        this.PD = Pd;
    }

    @Override
    public List<Car> evolve() {
        for(TrafficLight tl : trafficLights) {
            tl.evolve(simTime);
        }
        List<Double> newSpeeds = new ArrayList<>(particles.size());
        Map<Integer, Boolean> newInteractions = new HashMap<>(trafficLightInteractions.size());
        for (int i = 0; i < particles.size(); i++) {
            Car currentCar = particles.get(i),
                nextCar = getCarAhead(i),
                nextNextCar = getCarAhead(i+1);
            TrafficLight nextTrafficLight = getTrafficLightAhead(currentCar);
            newInteractions.put(currentCar.getId(), false);

            if (shouldStopForTrafficLight(currentCar, nextTrafficLight, nextCar)) {
                // First car in group to stop for traffic light
                newSpeeds.add(trafficLightInteraction(currentCar, nextTrafficLight));
                newInteractions.put(currentCar.getId(), true);
            } else if (shouldStopForTrafficLightChain(currentCar, nextTrafficLight, nextCar)) {
                // Car ahead is interacting with traffic light
                newSpeeds.add(trafficLightChainInteraction(currentCar, nextCar, nextTrafficLight));
                newInteractions.put(currentCar.getId(), true);
            } else {
                // Regular KSSS evolution
                newSpeeds.add(evolveCar(currentCar, nextCar, nextNextCar));
            }
        }
        // Advance cars
        particles = advanceCars(particles, newSpeeds, false);
        // Update interactions
        trafficLightInteractions = newInteractions;
        // Make sure we didn't break anything
        validateCars(roadLength, maxSpeed);
        validateCarOrder();

        this.simTime++;
        return particles;
    }

    /**
     * Copy of KSSS evolution step.
     *
     * @param currentCar  Current car.
     * @param nextCar     Car ahead of {@code currentCar}.
     * @param nextNextCar Car ahead of {@code nextCar}.
     * @return The car's new velocity.
     */
    private double evolveCar(Car currentCar, Car nextCar, Car nextNextCar) {
        double currentCarSpeed = getVelocityComponent(currentCar);
        double p;
        double th = wrapAroundDistance(currentCar, nextCar) / currentCarSpeed;
        double ts = Math.min(currentCarSpeed, H);

        // Rule 0: Calculation of random parameters
        // th < ts indicates that the car ahead is within the interaction horizon
        if (currentCarSpeed == 0) {
            p = P0;
        } else if(nextCar.areBrakeLightsOn() && th < ts){
            p = getVelocityComponent(nextCar) > 0 ? PB : 1;
        } else {
            p = PD;
        }

        // Rule 1: Acceleration
        double v = getVelocityComponent(currentCar);
        // if the next car is not in the interaction horizon it accelerates by one unit
        if((!currentCar.areBrakeLightsOn() && !nextCar.areBrakeLightsOn()) || th >= ts) {
            v = Math.min(currentCarSpeed + 1, maxSpeed);
        }

        // Rule 2: Brake because of interaction with other cars
        v = Math.min(effectiveGap(currentCar, nextCar, nextNextCar), v);
        if(v < currentCarSpeed){
            currentCar.turnBrakeLightsOn();
        }

        // Rule 3: Random brake with probability p
        if (new Random().nextDouble() < p) {
            v = Math.max(v-1, 0);
            if(p == PB || v <= currentCarSpeed) {
                currentCar.turnBrakeLightsOn();
            }
        }

        // Turn off brake lights if accelerating
        if (v > currentCarSpeed) {
            currentCar.turnBrakeLightsOff();
        }

        return v;
    }

    /**
     * Calculates whether a given car should stop for the given traffic light, given this car's preceding car. If the
     * traffic light is closer than the car, not green and within the interaction horizon (or the car is already stopped
     * for it), the car should stop/remain stopped for the traffic light.
     *
     * @param car              The car in question.
     * @param nextTrafficLight The next traffic light.
     * @param nextCar          The next car.
     * @return {@code true} if the car should stop for the traffic light, or {@code false} if it should stop for the car
     * ahead of it.
     */
    private boolean shouldStopForTrafficLight(Car car, TrafficLight nextTrafficLight, Car nextCar) {
        if (nextTrafficLight == null) { // Edge case: Car is directly under the red traffic light. Don't stop.
            return false;
        }
        double v = getVelocityComponent(car),
                trafficLightDistance = wrapAroundDistance(car, nextTrafficLight),
                th = wrapAroundDistance(car, nextTrafficLight) / v,
                ts = Math.min(v, H * 3);                                            // Bigger interaction horizon for traffic lights since they're visible from farther away and cars approach them with a much bigger delta T than with another car
        return trafficLightDistance < wrapAroundDistance(car, nextCar)              // Traffic light is closer than next car
                && !nextTrafficLight.isGreen()                                      // Traffic light is not green
                &&  (th < ts                                                        // Traffic light is within interaction horizon (always false when car is stopped), OR
                    || (v == 0                                                      // Car is stopped because of the traffic light
                    && (effectiveGap(car, nextTrafficLight) == 0 || trafficLightInteractions.get(car.getId()))))
                && requiredDeceleration(car, nextTrafficLight) >= maxDeceleration;  // Required deceleration is acceptable (>=, not <= because we're dealing with negative numbers)
    }

    /**
     * Similar to {@link #shouldStopForTrafficLight(Car, TrafficLight, Car)} but for cars that are behind another car
     * that is already stopping for a traffic light.  This is used to override KSSS to prevent collisions.
     *
     * @param currentCar       Current car
     * @param nextTrafficLight Next traffic light
     * @param nextCar          Next car (can be either before or after {@code nextTrafficLight})
     * @return Whether the current car should stop as part of a traffic light chain.
     */
    private boolean shouldStopForTrafficLightChain(Car currentCar, TrafficLight nextTrafficLight, Car nextCar) {
        if (nextTrafficLight == null) {
            return false;
        }

        double v = getVelocityComponent(currentCar),
                carDistance = wrapAroundDistance(currentCar, nextCar),
                trafficLightDistance = wrapAroundDistance(currentCar, nextTrafficLight),
                th = carDistance / v,
                ts = Math.min(v, H);

        return carDistance < trafficLightDistance                   // Next particle is a car
                && trafficLightInteractions.get(nextCar.getId())    // Next car is interacting with traffic light
                && (th < ts                                         // Is within interaction horizon or is stopped right behind a car
                    || (v == 0 && effectiveGap(currentCar, nextCar, nextTrafficLight) == 0));
    }

    /**
     * Computes the deceleration required for a given car not to crash into the given traffic light.
     *
     * @param car          The car.
     * @param trafficLight The traffic light.
     * @return The required deceleration.
     */
    private double requiredDeceleration(Car car, TrafficLight trafficLight) {
        double trafficLightEffectiveGap = effectiveGap(car, trafficLight),
                v = getVelocityComponent(car);
        return trafficLightEffectiveGap == 0
                ? -v // Come to a stop
                : Math.floor(-(v*v) / (2 * trafficLightEffectiveGap)); // a = (vf^2 - vi^2) / (2*d). Use floor to always give whole numbers.
    }

    /**
     * Computes the deceleration required for a given car not to crash into the car ahead.
     *
     * @param currentCar  The car.
     * @param nextCar     The car ahead.
     * @param nextTrafficLight The car ahead of {@code nextCar}.
     * @return The required deceleration.
     */
    private double requiredDeceleration(Car currentCar, Car nextCar, TrafficLight nextTrafficLight) {
        double effectiveGap = effectiveGap(currentCar, nextCar, nextTrafficLight),
                v = getVelocityComponent(currentCar),
                vf = anticipatedSpeed(nextCar, nextTrafficLight),
                a = effectiveGap == 0
                    ? -v // Come to a stop
                    : ((vf*vf) - (v*v)) / (2 * effectiveGap), // a = (vf^2 - vi^2) / (2*d)
                aFloor = Math.floor(a); // Use floor to always give whole numbers.

        return a > -1 ? 0 : aFloor;
    }

    /**
     * Traffic light interaction. Cars slow down as necessary for red and yellow lights. <b>NOTE:</b> This assumes that
     * {@link #shouldStopForTrafficLight(Car, TrafficLight, Car)} is true.
     *
     * @param currentCar Current car
     * @param nextTrafficLight The next traffic light
     */
    private double trafficLightInteraction(Car currentCar, TrafficLight nextTrafficLight) {
        double distance = wrapAroundDistance(currentCar, nextTrafficLight),
                v = getVelocityComponent(currentCar),
                requiredDeceleration = requiredDeceleration(currentCar, nextTrafficLight);
        if (distance == 0 && v > -maxDeceleration) {
            throw new IllegalStateException("EDGE CASE: " + currentCar + " is directly under a traffic light and is going too fast to stop. What do we do?");
        } else if (requiredDeceleration < maxDeceleration) {
            throw new IllegalStateException(String.format("Required deceleration for car %s to not crash against traffic light %s exceeds maximum deceleration: %g < %g", currentCar, nextTrafficLight, requiredDeceleration, maxDeceleration));
        }
        double vf = v + requiredDeceleration * 1; // vf = vi + a*t, t = 1s
        if (vf <= v) {
            currentCar.turnBrakeLightsOn();
        } else {
            currentCar.turnBrakeLightsOff();
        }
        return vf;
    }

    /**
     * Traffic light interaction. Cars slow down as necessary for red and yellow lights. <b>NOTE:</b> This assumes that
     * {@link #shouldStopForTrafficLight(Car, TrafficLight, Car)} is true.
     *
     * @param currentCar Current car
     * @param nextTrafficLight The next traffic light
     */
    private double trafficLightChainInteraction(Car currentCar, Car nextCar, TrafficLight nextTrafficLight) {
        double v = getVelocityComponent(currentCar),
               requiredDeceleration = requiredDeceleration(currentCar, nextCar, nextTrafficLight);
        if (requiredDeceleration < maxDeceleration) {
            throw new IllegalStateException(String.format("Required deceleration for car %s to not crash against %s exceeds maximum deceleration: %g < %g", currentCar, nextCar, requiredDeceleration, maxDeceleration));
        }
        double vf = v + requiredDeceleration * 1; // vf = vi + a*t, t = 1s
        if (vf <= v) {
            currentCar.turnBrakeLightsOn();
        } else {
            currentCar.turnBrakeLightsOff();
        }
        return vf;
    }

    /**
     * Get the traffic light that is ahead of this car, considering periodic boundary conditions.
     *
     * @param car The car
     * @return The traffic light ahead of this car or {@code null} in the edge case where there is only 1 traffic light
     * and this car is in the exact same position as it.
     */
    private TrafficLight getTrafficLightAhead(Car car) {
        int minDistance = Integer.MAX_VALUE;
        TrafficLight result = null;
        for (TrafficLight trafficLight : this.trafficLights) {
            if (getPositionComponent(trafficLight) == getPositionComponent(car)) {
                if (trafficLight.isRed()) {
                    System.out.println("HEADS UP! " + car + "  passed directly under a red traffic light" + trafficLight + " at t=" + simTime);
                }
                continue; // No interaction when at the same position as a traffic light
            }
            int distance = getPositionComponent(car) < getPositionComponent(trafficLight) ? wrapAroundDistance(car, trafficLight) : wrapAroundDistance(trafficLight, car);
            if (distance < minDistance) {
                minDistance = distance;
                result = trafficLight;
            }
        }
        return result;
    }


    /**
     * TODO either adapt and use this in {@link #requiredDeceleration(Car, TrafficLight)} or delete it.
     */
    private int effectiveGap(Car car, TrafficLight trafficLight) {
        if (trafficLight.isGreen()) {
            return Integer.MAX_VALUE; // "Infinite" gap when traffic light is green
        } else {
            return Math.max(wrapAroundDistance(car, trafficLight) - securityGap, 0); // TODO consider using a different traffic light security gap
        }
    }

    /**
     * Effective gap, exclusively for cars, that behaves differently when either {@code middleCar} or {@code rightCar} is
     * stopped. In this case, try to leave as much of {@link #securityGap} as possible.
     *
     * @return The effective gap.
     * @see #effectiveGap(Car, Particle, Particle)
     */
    private int effectiveGap(Car leftCar, Car middleCar, Car rightCar) {
        if (getVelocityComponent(middleCar) == 0 || getVelocityComponent(rightCar) == 0) {
            return Math.max(wrapAroundDistance(leftCar, middleCar) - securityGap, 0);
        } else {
            return effectiveGap(leftCar,  (Particle) middleCar, rightCar);
        }
    }

    /**
     * Copy of {@link KSSS#effectiveGap(Car, Car, Car)} but more generic (ie. works with particles).
     *
     * @param currentCar       Current car
     * @param nextParticle     Particle ahead of current car
     * @param nextNextParticle Particle ahead of next particle
     * @return The effective gap
     */
    @SuppressWarnings("JavadocReference")
    private int effectiveGap(Car currentCar, Particle nextParticle, Particle nextNextParticle) {
        // d(n) = x(n+1) − x(n) − car length
        int dn = wrapAroundDistance(currentCar, nextParticle);  // TODO incorporate car length into these
        double anticipatedSpeed = anticipatedSpeed(nextParticle, nextNextParticle); //
        return dn + (int) Math.max(anticipatedSpeed - securityGap, 0);
    }

    /**
     * Compute expected velocity of a given particle in the next time step, given the particle ahead of it.
     *
     * @param particle     The particle whose speed to anticipate.
     * @param nextParticle The particle ahead of it.
     * @return The anticipated speed of {@code particle} in the next time step.
     */
    private int anticipatedSpeed(Particle particle, Particle nextParticle) {
        int dn1 = wrapAroundDistance(particle, nextParticle);
        return (int) Math.min(dn1, getVelocityComponent(particle));
    }
}
