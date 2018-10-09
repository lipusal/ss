package ar.edu.itba.ss.models;

import ar.edu.itba.ss.particles.Particle;

import java.util.List;
import java.util.Objects;

public abstract class Model<T extends Particle> {

    protected List<T> particles;

    public Model(List<T> particles) {
        Objects.requireNonNull(particles);
        this.particles = particles;
    }

    /**
     * Evolves the model from its current state. Returns the particles resulting from one evolution step.
     *
     * @return The evolved particles.
     */
    public abstract List<T> evolve();
}
