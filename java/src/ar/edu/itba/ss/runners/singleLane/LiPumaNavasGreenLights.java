package ar.edu.itba.ss.runners.singleLane;

import ar.edu.itba.ss.files.OvitoWriter;
import ar.edu.itba.ss.particles.Car;
import ar.edu.itba.ss.particles.Particle;
import ar.edu.itba.ss.particles.TrafficLight;
import ar.edu.itba.ss.runners.Runner;

import java.awt.geom.Point2D;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class LiPumaNavasGreenLights extends Runner {

    @SuppressWarnings("Duplicates")
    public static void main(String[] args) throws IOException {
        final int ROAD_LENGTH = 250,    // 250 * 7.5m = 1.875km
                MAX_SPEED = 3,          // 3 * 7.5 * 3.6 = 81km/h
                SECURITY_GAP = 1;

        final int greenDuration = 35;
        final int redDuration = 10;
        final int phaseBetweenTrafficLights = 5;

        final double car_radius = 0.5;

        boolean errored = false;

        do {
            OvitoWriter<Particle> ovitoWriter = null;
            int t = 0;
            try {
                ovitoWriter = new OvitoWriter<>(Paths.get("out.txt"));
                List<Car> placeholders = new ArrayList<>(2);
                placeholders.add(new Car(new Point2D.Double(0, -10), 0.1).fake());
                placeholders.add(new Car(new Point2D.Double(ROAD_LENGTH, 10), 0.1).fake());

                /* *************************************************************************************************************
                 *                                                  MODEL
                 * ************************************************************************************************************/
                List<Car> carsH = new ArrayList<>();
                int[] positions = splitEvenly(50, 5);
                for(int pos : positions) {
                    carsH.add(new Car(new Point2D.Double(pos, 0), car_radius));
                }

                /* *************************************************************************************************************
                 *                                      TRAFFIC LIGHTS EVERY ~400M
                 * ************************************************************************************************************/
                List<TrafficLight> trafficLightsH = new ArrayList<>();
                int phase = 0;
                for (int x = 54; x < ROAD_LENGTH; x += 54) { // 54 * 7.5 = 405m
                    trafficLightsH.add(new TrafficLight(new Point2D.Double(x, 0), redDuration, greenDuration, phase));
                    phase += phaseBetweenTrafficLights; // The phase varies between lights
                }
                ar.edu.itba.ss.models.LiPumaNavas modelH = new ar.edu.itba.ss.models.LiPumaNavas(ROAD_LENGTH, MAX_SPEED, SECURITY_GAP, true, carsH, trafficLightsH);

                while (t < 300) { // TODO: parametrizar tiempo de simulación
                    System.out.println(t);
                    List<Particle> allCars = withPlaceholders(placeholders, carsH);
                    allCars.addAll(trafficLightsH);
                    ovitoWriter.exportPositions(allCars, t);
                    carsH = modelH.evolve();
                    t++;
                }
                ovitoWriter.close();
            } catch (IllegalStateException | IllegalArgumentException e) {
                errored = true;
                System.out.format("Error in run at t=%d: %s. Retrying\n", t, e.getMessage());
            } finally {
                if (ovitoWriter != null) {
                    ovitoWriter.close();
                    Files.copy(Paths.get("out.txt"), Paths.get("in.txt"), StandardCopyOption.REPLACE_EXISTING);
                }
            }
        } while (errored);
    }

    private static int[] splitEvenly(int roadLength, int numCars) {
        if (numCars > roadLength) {
            throw new IllegalArgumentException("numCars must be less than or equal to roadLength, but " + numCars + " > " + roadLength);
        } else if (roadLength == 0 || numCars == 0) {
            return new int[0];
        }
        int[] result = new int[numCars];
        for (int i = 0; i < numCars; i++) {
            int nextValue = i * (roadLength - 1) / numCars; // Adapted from https://stackoverflow.com/a/6683724
            if (i > 0) {
                if (nextValue == result[i-1]) {
                    if (i < numCars - 1) {
                        System.out.format("Couldn't fit car #%d/%d in slot #%d, pushing it to the next one over\n", i+1, numCars, nextValue);
                        nextValue++;
                    } else {
                        // Try to find an empty space going backwards in the list
                        boolean saved = false;
                        for (int j = i-1; !saved && j > 0; j--) {
                            if (result[j] > result[j-1] + 1) { // Opening found, there's at least one open slot in the middle
                                nextValue = (result[j] + result[j-1]) / 2; // Set it to middle of the opening
                                saved = true;
                            }
                        }
                        if (!saved) {
                            throw new IllegalArgumentException("Could not fit the last car in the road");
                        }
                    }
                }
            }
            result[i] = nextValue;
        }
        Arrays.sort(result); // Slots may not be all in order, eg. when we have to save the last slot.
        return result;
    }
}
