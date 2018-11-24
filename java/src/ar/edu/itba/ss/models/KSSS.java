package ar.edu.itba.ss.models;

import ar.edu.itba.ss.particles.Car;

import java.util.List;
import java.util.Random;

// TODO: ver que pasa cuando max_speed es uno


/**
 * https://es.wikipedia.org/wiki/Modelo_Knospe,_Santen,_Schadschneider,_Schreckenberg
 */
public class KSSS extends Model{

    private int maxSpeed;
    private int roadLength;

    private int H = 6;
    private double P0 = 0.5;
    private double PB = 0.94;
    private double PD = 0.1;
    private int BS = 7;

    public KSSS(int roadLength, int maxSpeed, List<Car> cars) {
        super(cars);
        System.out.println(cars);
        this.maxSpeed = maxSpeed;
        this.roadLength = roadLength;
    }

    @Override
    public List<Car> evolve() {
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
                if(p==PB){
                    currentCar.turnBlinkersOn();
                }
            }

            //Rule 4: Move car and update car velocity
            currentCar.setVx(v);
            double newPos = v + currentCar.getX();
            if(newPos > roadLength){ // Periodic borders
                newPos -= roadLength;
            }
            currentCar.setX(newPos);
        }
        return particles;
    }
}
