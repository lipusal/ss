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
public class LiPumaNavasModel extends SingleLaneModel {

    private int maxSpeed;

    private int H = 6;
    private double P0 = 0.5;
    private double PB = 0.94;
    private double PD = 0.1;
    private int BS = 7;
    private int simTime = 0;
    private final double maxDeceleration = -5;

    private List<TrafficLight> trafficLights = new ArrayList<>();

    public LiPumaNavasModel(int roadLength, boolean horizontal, int maxSpeed, List<Car> cars, List<TrafficLight> trafficLights) {
        super(cars, roadLength, horizontal);
        this.maxSpeed = maxSpeed;
        this.trafficLights.addAll(trafficLights);
    }

    @Override
    public List<Car> evolve() {
        for(TrafficLight tl : trafficLights) {
            tl.evolve(simTime);
        }

        for (int i = 0; i < particles.size(); i++) {
            Car currentCar = particles.get(i);
            Car nextCar = getCarAhead(i);
            TrafficLight nextTrafficLight = getTrafficLightAhead(currentCar);
            // Interact with traffic light if it's the closest particle ahead and it's not green
            boolean shouldInteractWithTrafficLight =
                    nextTrafficLight != null
                    && wrapAroundDistance(currentCar, nextTrafficLight) < wrapAroundDistance(currentCar, nextCar)
                    && !nextTrafficLight.isGreen();

            double newV;
            if (shouldInteractWithTrafficLight) {
                newV = trafficLightInteraction(currentCar, nextTrafficLight);
            } else {
                newV = carInteraction(currentCar, nextCar);
            }
            updateCar(currentCar, newV);
        }
        this.simTime++;
        return particles;
    }

    /**
     * Update a car given its new velocity component:
     * <ul>
     *     <li>Turn stopping lights on/off as necessary</li>
     *     <li>Update velocity component</li>
     *     <li>Update position based on new velocity</li>
     * </ul>
     *
     * @param car  Car to update.
     * @param newV Car's new velocity.
     */
    private void updateCar(Car car, double newV) {
        // Update blinkers and color
        if (newV < getVelocityComponent(car)) {
            car.turnBrakeLightsOn();
            car.setColor(Color.RED);
        } else {
            car.turnBrakeLightsOff();
            car.setColor(Color.WHITE);
        }
        // Update velocity
        setVelocityComponent(car, newV);
        // Update position with new velocity
        double newPos = newV + getPositionComponent(car);
        if(newPos > roadLength){ // Periodic borders, wrap around if necessary
            newPos -= roadLength;
        }
        setPositionComponent(car, newPos);
    }

    /**
     * Modified KSSS interaction, treats red traffic lights as stopping cars.
     *
     * @param currentCar Current car
     * @param carAhead Particle ahead (car or traffic light)
     * @return The car's new velocity component.
     */
    private double carInteraction(Car currentCar, Car carAhead) {
        double p;
        double th = wrapAroundDistance(currentCar, carAhead) / Math.abs(getVelocityComponent(currentCar));
        double ts = Math.min(Math.abs(getVelocityComponent(currentCar)), H);

        // Rule 0: Calculation of random parameters
        // th < ts indicates that the preceding car is in the interaction horizon
        if (carAhead.areBrakeLightsOn() && th < ts) {
            p = PB;
        } else if (Math.abs(getVelocityComponent(currentCar)) == 0) {
            p = P0;
        } else {
            p = PD;
        }

        // Rule 1: Acceleration
        double v = getVelocityComponent(currentCar);
        // if the next car is not in the interaction horizon it accelerates by one unit
        if((!currentCar.areBrakeLightsOn() && !carAhead.areBrakeLightsOn()) || th >= ts) {
            v = Math.min(Math.abs(getVelocityComponent(currentCar)) + 1, maxSpeed);
        }

        // Rule 2: Brake because of interaction with other cars
        v = Math.min(v, currentCar.distanceTo(carAhead));
        if(v < getVelocityComponent(currentCar)){
            currentCar.turnBrakeLightsOn();
            currentCar.setColor(Color.RED);
        }

        // Rule 3: Random brake with probability p
        if(new Random().nextDouble() < p){
            v = Math.max(v-1, 0);
            if(p==PB){
                currentCar.turnBrakeLightsOn();
                currentCar.setColor(Color.RED);
            }
        }

        // Turn off break lights if not breaking
        if (v > getVelocityComponent(currentCar)) {
            currentCar.turnBrakeLightsOff();
            currentCar.setColor(Color.WHITE);
        }

        return v;
    }

    // TODO NOW if a car is braking hard from a traffic light, all cars behind it should slow down too

    /**
     * Traffic light interaction. Cars slow down as hard as needed for red and yellow lights (up to a maximum for yellow
     * lights) and accelerate for yellow lights if they won't break in time.
     *
     *  @param currentCar Current car
     * @param nextTrafficLight Particle ahead (car or traffic light)
     * @return Whether {@link #carInteraction(Car, Car)} should be called after calling this method. This happens when
     * the car does not interact with the next traffic light (eg. because it's green) and so the regular KSSS interaction
     * should be evaluated with the car preceding it (which is past the traffic light).
     */
    private double trafficLightInteraction(Car currentCar, TrafficLight nextTrafficLight) {
        double distance = wrapAroundDistance(currentCar, nextTrafficLight);
        double v = getVelocityComponent(currentCar);
        if (distance == 0 && v > -maxDeceleration) {
            throw new IllegalStateException("EDGE CASE: " + currentCar + " is directly under a traffic light and is going too fast to stop. What do we do?");
        }
        double requiredDeceleration = distance == 0
                ? -v // Come to a stop
                : -(v*v) / (2 * distance); // a = (vf^2 - vi^2) / (2*d)

        // Cars can see "infinitely" ahead for traffic lights, and can tell whether they will stop in time for yellow lights
        boolean mustStop = nextTrafficLight.isRed()
                || (nextTrafficLight.isYellow() && requiredDeceleration >= maxDeceleration); // >=, not <= because we're dealing with negative numbers
        if (mustStop) {
            return v + (requiredDeceleration * 1); // vf = vi + a*t, t = 1s
        } else {
            return Math.min(v+1, maxSpeed);
        }
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
