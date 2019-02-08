package ar.edu.itba.ss.particles;

import java.awt.*;
import java.awt.geom.Point2D;

public class TrafficLight extends Particle {

    private final double redDuration, greenDuration;
    private double phase;
    private int lastUpdateTime;

    public enum LightState {
        GREEN, RED
    }

    private static final int DRAW_RADIUS = 1;

    private LightState state = LightState.GREEN;

    public TrafficLight(Point2D.Double position, int redDuration, int greenDuration, int phase) {
        super(position);
        setDrawRadius(DRAW_RADIUS);
        setColor(Color.GREEN); // Traffic lights start GREEN, use phase to make the initial green last shorter (or even 0)
        this.redDuration = redDuration;
        this.greenDuration = greenDuration;
        this.phase = phase;
        this.lastUpdateTime = 0;
    }

    public TrafficLight(Point2D.Double position, int redDuration, int greenDuration, int phase, Point2D.Double drawPosition) {
        super(position);
        setDrawRadius(DRAW_RADIUS);
        setColor(Color.GREEN); // Traffic lights start GREEN, use phase to make the initial green last shorter (or even 0)
        this.redDuration = redDuration;
        this.greenDuration = greenDuration;
        this.phase = phase;
        this.lastUpdateTime = 0;
        this.drawPosition = drawPosition;
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

    /**
     * Get remaining time until traffic light changes state.
     *
     * @param currentTime Current time.
     * @return Time until traffic light changes. Greater than or equal to 0.
     */
    public double getRemainingTime(int currentTime) {
        int timeSinceLastChange = currentTime - lastUpdateTime;
        double result = -1;
        switch (getState()) {
            case GREEN:
                result = greenDuration - phase - timeSinceLastChange;
                break;
            case RED:
                result = redDuration - phase - timeSinceLastChange;
                break;
        }
        return Math.max(result, 0);
    }

    private LightState getState() {
        return state;
    }

    public boolean isGreen() {
        return state == LightState.GREEN;
    }

    public boolean isRed() {
        return state == LightState.RED;
    }

    private void changeToGreen(){
        this.state = LightState.GREEN;
        setColor(Color.GREEN);
    }

    private void changeToRed(){
        this.state = LightState.RED;
        setColor(Color.RED);
    }

    @Override
    public String toString() {
        return String.format("TrafficLight #%d @(%g, %g), %s", getId(), getX(), getY(), getState());
    }
}
