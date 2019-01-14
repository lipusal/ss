package ar.edu.itba.ss.particles;

import java.awt.*;
import java.awt.geom.Point2D;

public class TrafficLight extends Particle {

    private final double redDuration, greenDuration, yellowDuration;
    private double phase;
    private int lastUpdateTime;

    public enum LightState {
        GREEN, YELLOW, RED
    }

    private static final int DRAW_RADIUS = 5;

    private LightState state = LightState.GREEN;

    public TrafficLight(Point2D.Double position, int redDuration, int yellowDuration, int greenDuration, int phase) {
        super(position);
        setDrawRadius(DRAW_RADIUS);
        setColor(Color.GREEN); // Traffic lights start GREEN, use phase to make the initial green last shorter (or even 0)
        this.redDuration = redDuration;
        this.yellowDuration = yellowDuration;
        this.greenDuration = greenDuration;
        this.phase = phase;
        this.lastUpdateTime = 0;
    }

    /**
     * Creates a traffic light with a 0-duration yellow light.
     *
     * @see #TrafficLight(Point2D.Double, int, int, int, int)
     */
    public TrafficLight(Point2D.Double position, int redDuration, int greenDuration, int phase) {
        this(position, redDuration, 0, greenDuration, phase);
    }

    /**
     * Cycle the traffic light around green, yellow or red as appropriate.
     *
     * @param time Current simulation time.
     */
    public void evolve(int time) {
        int timeSinceLastChange = time - lastUpdateTime;
        switch (getState()) {
            case GREEN:
                if (timeSinceLastChange + phase >= greenDuration) {
                    if (yellowDuration > 0) { // Edge case: 0-duration yellow light
                        changeToYellow();
                    } else {
                        changeToRed();
                    }
                    lastUpdateTime = time;
                    if (phase != 0) {
                        phase = 0;
                    }
                }
            break;
            case YELLOW:
                if (timeSinceLastChange + phase >= yellowDuration) {
                    changeToRed();
                    lastUpdateTime = time;
                    if (phase != 0) {
                        phase = 0;
                    }
                }
            break;
            case RED:
                if (timeSinceLastChange + phase >= redDuration) {
                    changeToGreen();
                    lastUpdateTime = time;
                    if (phase != 0) {
                        phase = 0;
                    }
                }
            break;
        }
    }

    private LightState getState() {
        return state;
    }

    public boolean isGreen() {
        return state == LightState.GREEN;
    }

    public boolean isYellow() {
        return state == LightState.YELLOW;
    }

    public boolean isRed() {
        return state == LightState.RED;
    }

    private void changeToGreen(){
        this.state = LightState.GREEN;
        setColor(Color.GREEN);
    }

    public void changeToYellow() {
        this.state = LightState.YELLOW;
        setColor(Color.YELLOW);
    }

    private void changeToRed(){
        this.state = LightState.RED;
        setColor(Color.RED);
    }
}
