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

            if (nextTrafficLight != null && wrapAroundDistance(currentCar, nextTrafficLight) < wrapAroundDistance(currentCar, nextCar) && nextTrafficLight.isRed()) {
                interaction(currentCar, nextTrafficLight);
            } else {
                interaction(currentCar, nextCar);
            }
        }
        this.simTime++;
        return particles;
    }

    /**
     * Modified KSSS interaction, treats red traffic lights as stopping cars.
     *
     * @param currentCar Current car
     * @param nextParticle Particle ahead (car or traffic light)
     */
    private void interaction(Car currentCar, Particle nextParticle) {
        double p;
        double th = wrapAroundDistance(currentCar, nextParticle) / Math.abs(getVelocityComponent(currentCar));
        double ts = Math.min(Math.abs(getVelocityComponent(currentCar)), H);

        boolean nextParticleIsStopping =
                (nextParticle instanceof TrafficLight && ((TrafficLight)nextParticle).isRed())
                || (nextParticle instanceof Car && ((Car)nextParticle).areBlinkersOn());

        // Rule 0: Calculation of random parameters
        // th < ts indicates that the preceding car is in the interaction horizon
        if (nextParticleIsStopping && th < ts) {
            p = PB;
        } else if (Math.abs(getVelocityComponent(currentCar)) == 0) {
            p = P0;
        } else {
            p = PD;
        }

        // Rule 1: Acceleration
        double v = getVelocityComponent(currentCar);
        // if the next car is not in the interaction horizon it accelerates by one unit
        if((!currentCar.areBlinkersOn() && !nextParticleIsStopping) || th >= ts) {
            v = Math.min(Math.abs(getVelocityComponent(currentCar)) + 1, maxSpeed);
        }

        // Rule 2: Brake because of interaction with other cars
        v = Math.min(v, currentCar.distanceTo(nextParticle));
        if(v < getVelocityComponent(currentCar)){
            currentCar.turnBlinkersOn();
            currentCar.setColor(Color.RED);
        }

        // Rule 3: Random brake with probability p
        if(new Random().nextDouble() < p){
            v = Math.max(v-1, 0);
            if(p==PB){
                currentCar.turnBlinkersOn();
                currentCar.setColor(Color.RED);
            }
        }

        // Turn off break lights if not breaking
        if (v > getVelocityComponent(currentCar)) {
            currentCar.turnBlinkersOff();
            currentCar.setColor(Color.WHITE);
        }

        //Rule 4: Move car and update car velocity
        setVelocityComponent(currentCar, v);
        double newPos = v + getPositionComponent(currentCar);
        if(newPos > roadLength){ // Periodic borders
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
