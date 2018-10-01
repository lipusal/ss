package ar.edu.itba.ss.particles;

import java.awt.geom.Point2D;
import java.util.Objects;

public abstract class Particle {
    protected int id;
    protected Point2D.Double position, velocity, acceleration;

    public Particle(int id, Point2D.Double position, Point2D.Double velocity, Point2D.Double acceleration) {
        this.id = id;
        this.position = position;
        this.velocity = velocity;
        this.acceleration = acceleration;
    }

    /**
     * Creates a new instance of Particle with the specified ID and its position, velocity and acceleration all set to 0.
     *
     * @param id The particle's ID.
     */
    public Particle(int id) {
        this(id, new Point2D.Double(), new Point2D.Double(), new Point2D.Double());
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

    public double getY() {
        return position.getY();
    }

    public Point2D.Double getVelocity() {
        return velocity;
    }

    public double getVX() {
        return velocity.getX();
    }

    public double getVY() {
        return velocity.getY();
    }

    public Point2D.Double getAcceleration() {
        return acceleration;
    }

    public double getAX() {
        return acceleration.getX();
    }

    public double getA() {
        return acceleration.getY();
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
