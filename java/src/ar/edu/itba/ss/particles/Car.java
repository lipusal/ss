package ar.edu.itba.ss.particles;

import ar.edu.itba.ss.util.PointUtils;

import java.awt.*;
import java.awt.geom.Point2D;

public class Car extends Particle {
    private boolean brakeLightsOn = false, isFake = false;

    public Car(int id, Point2D.Double position, Point2D.Double velocity, Point2D.Double acceleration, double radius) {
        super(id, position, velocity, acceleration, radius);
    }

    public Car(Point2D.Double position, Point2D.Double velocity, Point2D.Double acceleration) {
        super(position, velocity, acceleration);
    }

    public Car(Point2D.Double position, Point2D.Double velocity) {
        this(position, velocity, new Point2D.Double());
    }

    public Car(Point2D.Double position, Point2D.Double velocity, double radius) {
        super(position, velocity, new Point2D.Double(0,0), radius);
    }

    public Car(Point2D.Double position, double radius) {
        this(position, new Point2D.Double(), radius);
    }

    public Car(Point2D.Double position) {
        this(position, 1.0);
    }

    public void turnBrakeLightsOn() {
        this.brakeLightsOn = true;
        this.color = Color.RED;
    }

    public void turnBrakeLightsOff() {
        this.brakeLightsOn = false;
        this.color = Color.WHITE;
    }

    public boolean areBrakeLightsOn() {
        return this.brakeLightsOn;
    }

    @Override
    public String toString() {
        return String.format("Car #%d @%s, Vx=%g, Ax=%g, brake lights %s", id, PointUtils.toString(position), getVX(), getAX(), brakeLightsOn ? "ON" : "OFF");
    }

    public void advanceX(double deltaX) {
        setX(getX() + deltaX);
    }

    public boolean isFake() {
        return isFake;
    }

    /**
     * Sets the fake boolean. If {@code true}, sets this car's color to green, otherwise white.

     * @return The instance, for chaining.
     */
    public Car setFake(boolean fake) {
        isFake = fake;
        setColor(isFake ? Color.GREEN : Color.WHITE);
        return this;
    }

    /**
     * Calls {@code setFake(true)}.
     *
     * @see #setFake(boolean)
     */
    public Car fake() {
        return setFake(true);
    }
}
