package ar.edu.itba.ss.models;

import ar.edu.itba.ss.particles.Car;
import ar.edu.itba.ss.particles.Particle;
import ar.edu.itba.ss.particles.TrafficLight;

import java.awt.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * Modified version of KSSS that includes interaction with traffic lights
 */
public class LiPumaNavasModel extends KSSS {

    private int simTime = 0;
    private final double maxDeceleration = -5;

    private List<TrafficLight> trafficLights = new ArrayList<>();

    public LiPumaNavasModel(int roadLength, int maxSpeed, int securityGap, boolean horizontal, List<Car> cars, List<TrafficLight> trafficLights) {
        super(roadLength, maxSpeed, securityGap, horizontal, cars);
        this.trafficLights.addAll(trafficLights);
    }

    @Override
    public List<Car> evolve() {
        for(TrafficLight tl : trafficLights) {
            tl.evolve(simTime);
        }

        for (int i = 0; i < particles.size(); i++) {
            Car currentCar = particles.get(i),
                nextCar = getCarAhead(i),
                nextNextCar = getCarAhead(i+1);
            TrafficLight nextTrafficLight = getTrafficLightAhead(currentCar);
            // Interact with traffic light if it's the closest particle ahead and it's not green
            if (shouldStopForTrafficLight(currentCar, nextTrafficLight, nextCar)) {
                trafficLightInteraction(currentCar, nextTrafficLight);
            } else {
                evolveCar(currentCar, nextNextCar, nextNextCar);
            }
        }
        this.simTime++;
        return particles;
    }

    /**
     * Calculates whether a given car should stop either for the given traffic light or car ahead of it.
     *
     * @param car              The car in question.
     * @param nextTrafficLight The next traffic light.
     * @param nextCar          The next car.
     * @return {@code true} if the car should stop for the traffic light, or {@code false} if it should stop for the car
     * ahead of it.
     */
    private boolean shouldStopForTrafficLight(Car car, TrafficLight nextTrafficLight, Car nextCar) {
        double v = getVelocityComponent(car),
                trafficLightDistance = wrapAroundDistance(car, nextTrafficLight),
                th = wrapAroundDistance(car, nextTrafficLight) / v,
                ts = Math.min(v, H * 2); // Interaction horizon for traffic lights is twice as big as cars' since traffic lights are more visible from far away
        return trafficLightDistance < wrapAroundDistance(car, nextCar)
                && !nextTrafficLight.isGreen()
                &&  th < ts
                && requiredDeceleration(car, nextTrafficLight) >= maxDeceleration; // >=, not <= because we're dealing with negative numbers
    }

    /**
     * Computes the deceleration required for a given car not to crash into the given traffic light.
     *
     * @param car          The car.
     * @param trafficLight The traffic light.
     * @return The required deceleration.
     */
    private double requiredDeceleration(Car car, TrafficLight trafficLight) {
        double distanceToTrafficLight = wrapAroundDistance(car, trafficLight),
                v = getVelocityComponent(car);
        return distanceToTrafficLight <= 1 // TODO consider securityGap here, or use a different traffic light security gap
                ? -v // Come to a stop
                : -(v*v) / (2 * distanceToTrafficLight); // a = (vf^2 - vi^2) / (2*d)
    }

    /**
     * Traffic light interaction. Cars slow down as necessary for red and yellow lights. <b>NOTE:</b> This assumes that
     * {@link #shouldStopForTrafficLight(Car, TrafficLight, Car)} is true.
     *
     *  @param currentCar Current car
     * @param nextTrafficLight The next traffic light
     */
    private void trafficLightInteraction(Car currentCar, TrafficLight nextTrafficLight) {
        double distance = wrapAroundDistance(currentCar, nextTrafficLight),
                v = getVelocityComponent(currentCar),
                requiredDeceleration = requiredDeceleration(currentCar, nextTrafficLight);
        if (distance == 0 && v > -maxDeceleration) {
            throw new IllegalStateException("EDGE CASE: " + currentCar + " is directly under a traffic light and is going too fast to stop. What do we do?");
        } else if (requiredDeceleration < maxDeceleration) {
            throw new IllegalStateException(String.format("Required deceleration for car %s to not crash against traffic light %s exceeds maximum deceleration: %g < %g", currentCar, nextTrafficLight, requiredDeceleration, maxDeceleration));
        }
        double vf = v + requiredDeceleration * 1; // vf = vi + a*t, t = 1s
        setVelocityComponent(currentCar, vf);
        if (vf <= v) {
            currentCar.turnBrakeLightsOn();
        } else {
            currentCar.turnBrakeLightsOff();
        }
        double newPos = getPositionComponent(currentCar) + v;
        if (newPos > roadLength) { // Periodic borders
            newPos -= roadLength;
        }
        setPositionComponent(currentCar, newPos);
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
                if (!trafficLight.isRed()) {
                    System.out.println("HEADS UP! " + car + "  passed directly under a red traffic light");
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
}
