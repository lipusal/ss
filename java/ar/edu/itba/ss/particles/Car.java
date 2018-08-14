package ar.edu.itba.ss.particles;

import ar.edu.itba.ss.util.PointUtils;

import java.awt.Point;
import java.awt.geom.Point2D;

public class Car extends Particle {
    private static int globalId = 1;

    private int length;
    private boolean blinkersOn = false, isFake = false;

    public Car(int id, int length, Point position, Point2D.Double velocity, Point2D.Double acceleration) {
        super(id, new Point2D.Double(position.getX(), position.getY()), velocity, acceleration);
        this.length = length;
    }

    public Car(int length, Point position, Point2D.Double velocity, Point2D.Double acceleration) {
        this(globalId++, length, position, velocity, acceleration);
    }

    public Car(Point position, Point2D.Double velocity) {
        this(0, position, velocity, new Point2D.Double());
    }

    public Car(Point position) {
        this(0, position, new Point2D.Double(), new Point2D.Double());
    }

    public double distanceTo(Car other) {
        return position.distance(other.position);
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

    public void setX(int x) {
        position.x = x;
    }

    public void advanceRight(int deltaX) {
        setX((int) getX() + deltaX);
    }

    public void setVx(int vx) {
        velocity.x = vx;
    }

    public void incrementVx() {
        setVx((int) getVX() + 1);
    }

    public void decrementVx() {
        setVx((int) getVX() - 1);
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
