package ar.edu.itba.ss.particles;

import java.awt.*;
import java.awt.geom.Point2D;

/**
 * {@link Car} subclass that can only be instantiated in a given position and does not move.  Calls to {@link #setX(double)},
 * {@link #setVx(double)}, etc. have no effect.
 */
public class ImmovableCar extends Car {

    public ImmovableCar(Point2D.Double position) {
        super(position);
        this.color = Color.MAGENTA;
    }

    // Ignore all position, velocity or acceleration changes
    @Override
    public void setX(double x) {}

    @Override
    public void setY(double y) {}

    @Override
    public void setVx(double vx) {}

    @Override
    public void setVy(double vy) {}

    @Override
    public void setAX(double ax) {}

    @Override
    public void setColor(Color color) {}

    @Override
    public void turnBrakeLightsOn() {
        super.turnBrakeLightsOn();
        this.color = Color.MAGENTA;
    }

    @Override
    public void turnBrakeLightsOff() {
        super.turnBrakeLightsOff();
        this.color = Color.MAGENTA;
    }

    @Override
    public String toString() {
        return "Immovable " + super.toString();
    }
}
