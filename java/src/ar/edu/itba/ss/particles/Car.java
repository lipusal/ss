package ar.edu.itba.ss.particles;

import ar.edu.itba.ss.util.PointUtils;

import java.awt.geom.Point2D;

public class Car extends Particle {
    private static int globalId = 1;

    private boolean blinkersOn = false, isFake = false;

    public Car(int id, Point2D.Double position, Point2D.Double velocity, Point2D.Double acceleration, double radius) {
        super(id, position, velocity, acceleration, radius);
    }

    public Car(Point2D.Double position, Point2D.Double velocity, Point2D.Double acceleration) {
        super(globalId++, position, velocity, acceleration);
    }

    public Car(Point2D.Double position, Point2D.Double velocity) {
        this(position, velocity, new Point2D.Double());
    }

    public Car(Point2D.Double position, Point2D.Double velocity, double radius) {
        super(globalId++, position, velocity, new Point2D.Double(0,0), radius);
    }

    public Car(Point2D.Double position, double radius) {
        this(0, position, new Point2D.Double(), new Point2D.Double(), radius);
    }

    public Car(Point2D.Double position) {
        this(position, 1.0);
    }

    public double distanceTo(Car other) {
        return position.distance(other.position) - radius - other.radius;
    }

    public void turnBlinkersOn() {
        this.blinkersOn = true;
    }

    public void turnBlinkersOff() {
        this.blinkersOn = false;
    }

    public boolean areBlinkersOn() {
        return this.blinkersOn;
    }

    @Override
    public String toString() {
        return String.format("Car #%d @%s, Vx=%g, Ax=%g, blinkers %s", id, PointUtils.toString(position), getVX(), getAX(), blinkersOn ? "ON" : "OFF");
    }

    public void setX(double x) {
        position.x = x;
    }

    public void advanceForward(double deltaX) {
        setX(getX() + deltaX);
    }

    public void setVx(double vx) {
        velocity.x = vx;
    }

    public void incrementVx() {
        setVx(getVX() + 1);
    }

    public void decrementVx() {
        setVx(getVX() - 1);
    }

    public boolean isFake() {
        return isFake;
    }

    /**
     * Sets the fake boolean.

     * @return The instance, for chaining.
     */
    public Car setFake(boolean fake) {
        isFake = fake;
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
