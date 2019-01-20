package ar.edu.itba.ss.particles;

import java.awt.*;
import java.awt.geom.Point2D;
import java.util.Objects;

public abstract class Particle {
    private static int globalId = 1;

    protected int id;
    protected Point2D.Double position, velocity, acceleration, drawPosition;
    protected double drawRadius;
    protected Color color = Color.WHITE;

    public Particle(int id, Point2D.Double position, Point2D.Double velocity, Point2D.Double acceleration, double drawRadius) {
        this.id = id;
        this.position = position;
        this.velocity = velocity;
        this.acceleration = acceleration;
        this.drawRadius = drawRadius;
    }

    public Particle(Point2D.Double position, Point2D.Double velocity, Point2D.Double acceleration, double radius) {
        this(globalId++, position, velocity, acceleration, radius);
    }

    /**
     * Equivalent to {@code new Particle(id, position, velocity, acceleration, 1.0)}.
     * @see #Particle(int, Point2D.Double, Point2D.Double, Point2D.Double, double)
     */
    public Particle(Point2D.Double position, Point2D.Double velocity, Point2D.Double acceleration) {
        this(globalId++, position, velocity, acceleration, 1.0);
    }

    /**
     * Creates an unmoving particle. Equivalent to {@code new Particle(position, new Point2D.Double(0,0), new Point2D.Double(0,0)}.
     */
    public Particle(Point2D.Double position) {
        this(position, new Point2D.Double(0,0), new Point2D.Double(0,0));
    }

    public double distanceTo(Particle other) {
        return position.distance(other.position);
    }

    public int getId() {
        return id;
    }

    public Point2D.Double getPosition() {
        return position;
    }

    public double getX() {
        return position.getX();
    }

    public void setX(double x) {
        position.x = x;
    }

    public double getY() {
        return position.getY();
    }

    public void setY(double y) {
        position.y = y;
    }

    public Point2D.Double getVelocity() {
        return velocity;
    }

    public double getVX() {
        return velocity.getX();
    }

    public void setVx(double vx) {
        velocity.x = vx;
    }

    public double getVY() {
        return velocity.getY();
    }

    public void setVy(double vy) {
        velocity.y = vy;
    }

    public Point2D.Double getAcceleration() {
        return acceleration;
    }

    public double getAX() {
        return acceleration.getX();
    }

    public void setAX(double ax) {
        acceleration.x = ax;
    }

    public double getAY() {
        return acceleration.getY();
    }



    public double getDrawRadius() {
        return drawRadius;
    }

    public void setDrawRadius(double drawRadius) {
        this.drawRadius = drawRadius;
    }

    public Point2D.Double getDrawPosition() {
        return drawPosition;
    }

    public double getDrawX() {
        return drawPosition.x;
    }

    public double getDrawY() {
        return drawPosition.y;
    }

    public void setDrawPosition(Point2D.Double drawPosition) {
        this.drawPosition = drawPosition;
    }

    public Color getColor() {
        return color;
    }

    public void setColor(Color color) {
        this.color = color;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Particle particle = (Particle) o;
        return id == particle.id;
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
}
