package ar.edu.itba.ss.runners.singleIntersection;

import ar.edu.itba.ss.files.OvitoWriter;
import ar.edu.itba.ss.models.LiPumaNavas;
import ar.edu.itba.ss.particles.Car;
import ar.edu.itba.ss.particles.Particle;
import ar.edu.itba.ss.particles.TrafficLight;

import java.awt.geom.Point2D;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class TimeMinimizer {

    public static void main(String[] args) throws IOException {
        // We imagine each cell representing 7.5m, which is about the average car length plus distance with their predecessor in a traffic jam
        final int ROAD_LENGTH = 135,    // 135 * 7.5 = 1012.5m ~ 1km
                  MAX_SPEED = 3,        // 3 * 7.5 * 3.6 = 81km/h
                  SECURITY_GAP = 3,
                  RED_DURATION = 25,
                  GREEN_DURATION = 50;
        final double CAR_RADIUS = 0.5;  // Each car takes up 1 cell

        for (int numCars = 2; numCars <= 10; numCars++) {
            OvitoWriter<Particle> ovitoWriter = null;
            boolean errored;
            do {
                int t = 0;
                try {
                    ovitoWriter = new OvitoWriter<>(Paths.get("timeMin" , "c" + numCars + ".txt"));
                    int[] positions = splitEvenly((int) (ROAD_LENGTH/2.0 - SECURITY_GAP), numCars);
                    List<Car> placeholders = new ArrayList<>(4);
                    placeholders.add(new Car(new Point2D.Double(0, 0), 0.1).fake());
                    placeholders.add(new Car(new Point2D.Double(ROAD_LENGTH, ROAD_LENGTH), 0.1).fake());

                    /* *************************************************************************************************************
                     *                                          HORIZONTAL MODEL
                     * ************************************************************************************************************/
                    List<Car> carsH = new ArrayList<>();
                    for(int pos : positions) {
                        carsH.add(new Car(new Point2D.Double(pos, ROAD_LENGTH/2.0), CAR_RADIUS));
                    }
                    List<TrafficLight> trafficLightsH = new ArrayList<>();
                    trafficLightsH.add(new TrafficLight(new Point2D.Double(ROAD_LENGTH/2.0 - 5, ROAD_LENGTH/2.0), RED_DURATION, GREEN_DURATION, 0, new Point2D.Double(ROAD_LENGTH/2.0 + 10, ROAD_LENGTH/2.0)));
                    LiPumaNavas modelH = new LiPumaNavas(ROAD_LENGTH, MAX_SPEED, SECURITY_GAP, true, carsH, trafficLightsH);

                    /* *************************************************************************************************************
                     *                                          VERTICAL MODEL
                     * ************************************************************************************************************/
                    List<Car> carsV = new ArrayList<>();
                    for (int i = 0; i < positions.length * 0.6; i++) { // Vertical model has 2/3 the traffic of horizontal
                        carsV.add(new Car(new Point2D.Double(ROAD_LENGTH/2.0, positions[i]), CAR_RADIUS));
                    }
                    List<TrafficLight> trafficLightsV = new ArrayList<>();
                    trafficLightsV.add(new TrafficLight(new Point2D.Double(ROAD_LENGTH/2.0, ROAD_LENGTH/2.0 - 5), GREEN_DURATION, RED_DURATION, RED_DURATION, new Point2D.Double(ROAD_LENGTH/2.0, ROAD_LENGTH/2.0  + 10)));
                    LiPumaNavas modelV = new LiPumaNavas(ROAD_LENGTH, MAX_SPEED, 3, false, carsV, trafficLightsV);


                    while (t < 500) { // TODO: parametrizar tiempo de simulación
                        List<Particle> allParticles = withPlaceholders(placeholders, carsH);
                        allParticles.addAll(carsV);
                        allParticles.addAll(trafficLightsH);
                        allParticles.addAll(trafficLightsV);
                        ovitoWriter.exportPositions(allParticles, t);
                        carsH = modelH.evolve();
                        carsV = modelV.evolve();
                        t++;
                    }
                    errored = false;
                } catch (IllegalStateException | IllegalArgumentException e) {
                    errored = true;
                    System.out.format("Error in run with %d cars in t=%d: %s. Retrying\n", numCars, t, e.getMessage());
//                    System.out.flush();
//                    e.printStackTrace();
//                    System.err.flush();
//                    System.out.println();
//                    System.out.flush();
                } finally {
                    if (ovitoWriter != null) {
                        ovitoWriter.close();
                    }
                }
            } while(errored);
        }
    }

    private static List<Particle> withPlaceholders(List<Car> placeholders, List<Car> cars) {
        List<Particle> result = new ArrayList<>(cars);
        result.addAll(placeholders);
        return result;
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
