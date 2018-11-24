package ar.edu.itba.ss.models;

import ar.edu.itba.ss.particles.Car;
import ar.edu.itba.ss.particles.Particle;

import java.util.List;

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

    /**
     * Instances a new horizontal or vertical single-lane model of the specified length.
     *
     * @param particles  Particles that compose the model.
     * @param roadLength Road length.
     * @param horizontal Whether the model is horizontal (if false, it's vertical).
     */
    public SingleLaneModel(List<Car> particles, int roadLength, boolean horizontal) {
        super(particles);
        this.roadLength = roadLength;
        this.isHorizontal = horizontal;
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

    /* *****************************************************************************************************************
     *                                  BEGIN DIRECTION-INDEPENDENT HELPERS
     * The following methods help make concrete instances of this model work both horizontally and vertically.
     * ****************************************************************************************************************/

    /**
     * Gets the horizontal or vertical component of the specified particle's position, as appropriate for this model.
     */
    protected double getPositionComponent(Particle particle) {
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
    protected double getVelocityComponent(Particle car) {
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

    /* *****************************************************************************************************************
     *                                      END DIRECTION-INDEPENDENT HELPERS
     * ****************************************************************************************************************/
}
