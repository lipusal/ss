package ar.edu.itba.ss.models;

import ar.edu.itba.ss.particles.Car;

import java.util.List;
import java.util.Random;

/**
 * https://es.wikipedia.org/wiki/Modelo_Knospe,_Santen,_Schadschneider,_Schreckenberg
 */
public class KSSS extends Model<Car>{

    private int maxSpeed;
    private int roadLength;
    private int maxTime = 1000;

    // TODO: ver que diablos son estos parametros
    private int H = 6;
    private double P0 = 0.5;
    private double PB = 0.94;
    private double PD = 0.1;
    private int BS = 7;

    private double deltaT = 0.1;
    private double deltaTSave = 0.1;

    // TODO: ver si parametrizar las otras variables
    public KSSS(int roadLength, int maxSpeed, List<Car> cars) {
        super(cars);
        System.out.println(cars);
        this.maxSpeed = maxSpeed;
        this.roadLength = roadLength;
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
        System.out.println(particles);
        int t = 0;

        while(t<maxTime) {
            for (int i = 0; i < particles.size(); i++) {
                Car currentCar = particles.get(i);
                Car nextCar = getCarAhead(i);
                double p;
                double th = currentCar.distanceTo(nextCar) / Math.abs(currentCar.getVelocity().getX());
                double ts = Math.min(Math.abs(currentCar.getVelocity().getX()), H);

                // Rule 0: Calculation of random parameters
                // th < ts indicates that el preceding car is in the interaction horizon
                if(nextCar.areBlinkersOn() && th < ts){
                    p = PB;
                } else if(Math.abs(currentCar.getVelocity().getX()) == 0) {
                    p = P0;
                } else {
                    p = PD;
                }

                // Rule 1: Acceleration
                double v = currentCar.getVX();
                // if the next car is not in the interaction horizon it accelerates by one unit
                if((!currentCar.areBlinkersOn() && !nextCar.areBlinkersOn()) || th >= ts){
                    v = Math.min(Math.abs(currentCar.getVelocity().getX()) + 1, maxSpeed);
                }

                // Rule 2: Brake because of interaction with other cars
                v = Math.min(v, currentCar.distanceTo(nextCar));
                if(v < currentCar.getVX()){
                    currentCar.turnBlinkersOn();
                }

                // Rule 3: Random brake with probability p
                if(new Random().nextDouble() < p){
                    v = Math.max(v-1, 0);
                    if(p==PB){ // TODO: chequear si este if va afuera de esto
                        currentCar.turnBlinkersOn();
                    }
                }

                //Rule 4: Move car and update car velocity
                currentCar.setVx(v);
                currentCar.advanceForward(v);
            }
            t++;

        }
        return particles; //TODO: ver de sacar que no devuelva nada, cambia la misma lista..
    }
}
