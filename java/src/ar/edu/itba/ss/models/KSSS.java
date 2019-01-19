package ar.edu.itba.ss.models;

import ar.edu.itba.ss.particles.Car;

import java.util.List;
import java.util.Random;

// TODO: ver que pasa cuando max_speed es uno


/**
 * https://es.wikipedia.org/wiki/Modelo_Knospe,_Santen,_Schadschneider,_Schreckenberg
 */
public class KSSS extends SingleLaneModel {

    private int maxSpeed;

    private int H = 6;
    /**
     * Probability of a stopped car to remain stopped.
     */
    private double P0 = 0.5;
    /**
     * Probability of a car who can see its car ahead to brake when needed.
     */
    private double PB = 0.94;
    /**
     * Probability of a car to brake randomly.
     */
    private double PD = 0.1;
    private int BS = 7;
    private int securityGap;

    public KSSS(int roadLength, int maxSpeed, int securityGap, boolean horizontal, List<Car> cars) {
        super(cars, roadLength, horizontal);
        System.out.println(cars);
        this.maxSpeed = maxSpeed;
        this.securityGap = securityGap;
    }

    /**
     * Equivalent to {@code KSSS(roadLength, maxSpeed, securityGap, true, cars)}.
     *
     * @see #KSSS(int, int, int, boolean, List)
     */
    public KSSS(int roadLength, int maxSpeed, int securityGap, List<Car> cars) {
        this(roadLength, maxSpeed, securityGap, true, cars);
    }

    /**
     * Equivalent to {@link #KSSS(int, int, int, boolean, List) original constructor} with overrides for different
     * probability parameters.
     */
    public KSSS(int roadLength, int maxSpeed, int securityGap, boolean horizontal, double P0, double Pb, double Pd, List<Car> cars) {
        this(roadLength, maxSpeed, securityGap, horizontal, cars);
        this.P0 = P0;
        this.PB = Pb;
        this.PD = Pd;
    }

    @Override
    public List<Car> evolve() {
        for (int i = 0; i < particles.size(); i++) {
            Car currentCar = particles.get(i),
                nextCar = getCarAhead(i),
                nextNextCar = getCarAhead(i+1);
            double currentCarSpeed = getVelocityComponent(currentCar);
            double p;
            double th = wrapAroundDistance(currentCar, nextCar) / currentCarSpeed;
            double ts = Math.min(currentCarSpeed, H);

            // Rule 0: Calculation of random parameters
            // th < ts indicates that the car ahead is within the interaction horizon
            if (currentCarSpeed == 0) {
                p = P0;
            } else if(nextCar.areBrakeLightsOn() && th < ts){
                p = PB;
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
            if(new Random().nextDouble() < p){
                v = Math.max(v-1, 0);
                if(p == PB || v <= currentCarSpeed) {
                    currentCar.turnBrakeLightsOn();
                }
            }

            // Turn off brake lights if accelerating
            if (v > currentCarSpeed) {
                currentCar.turnBrakeLightsOff();
            }

            //Rule 4: Move car and update car velocity
            setVelocityComponent(currentCar, v);
            double newPos = getPositionComponent(currentCar) + v;
            if(newPos > roadLength){ // Periodic borders
                newPos -= roadLength;
            }
            setPositionComponent(currentCar, newPos);
        }
        return particles;
    }

    /**
     * Calculate the effective gap between two cars.  The effective gap is predictive, ie. {@code leftCar } car tries to
     * predict how the car ahead of it, {@code middleCar} will react according to the distance to its own predecessor
     * ({@code rightCar}).
     *
     * @param leftCar   Leftmost car.
     * @param middleCar Car ahead of {@code leftCar}.
     * @param rightCar  Car ahead of {@code middleCar}.
     * @return The effective distance.
     * @see <a href="https://arxiv.org/pdf/cond-mat/0012204.pdf">Algorithm in paper</a>.
     */
    private int effectiveGap(Car leftCar, Car middleCar, Car rightCar) {
        // d(n) = x(n+1) − x(n) − car length
        int dn = wrapAroundDistance(leftCar, middleCar);  // TODO incorporate car length into these
        int dn1 = wrapAroundDistance(middleCar, rightCar);
        double anticipatedSpeed = Math.min(dn1, getVelocityComponent(middleCar)); // Expected velocity of middle car in the next time step
        return dn + (int) Math.max(anticipatedSpeed - securityGap, 0);
    }
}
