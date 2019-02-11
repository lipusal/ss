package ar.edu.itba.ss.runners.singleIntersection;

import ar.edu.itba.ss.files.OvitoWriter;
import ar.edu.itba.ss.models.LiPumaNavas;
import ar.edu.itba.ss.models.SingleLaneModel;
import ar.edu.itba.ss.particles.Car;
import ar.edu.itba.ss.particles.Particle;
import ar.edu.itba.ss.particles.TrafficLight;

import java.awt.geom.Point2D;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;

public class TimeMinimizer {

    public static void main(String[] args) throws IOException {
        // We imagine each cell representing 7.5m, which is about the average car length plus distance with their predecessor in a traffic jam
        final int ROAD_LENGTH = 135,    // 135 * 7.5 = 1012.5m ~ 1km
                  MAX_SPEED = 3,        // 3 * 7.5 * 3.6 = 81km/h
                  SECURITY_GAP = 1,
                  NUM_CARS = 5;
        final double CAR_RADIUS = 0.5;  // Each car takes up 1 cell

        File outputFile = Paths.get("timeMin", "c"+NUM_CARS, "c" + NUM_CARS+ "_results.csv").toFile(),
            containingDir = outputFile.getParentFile();
        // Make directories if needed
        if (!containingDir.exists() && !containingDir.mkdirs()) {
            throw new IllegalArgumentException("Could not create directories for output files: " + outputFile.toString());
        }
        FileWriter resultsFileWriter = new FileWriter(outputFile);
        resultsFileWriter.write("greenDuration,redDuration,t\n");
        for (int greenDuration = 5; greenDuration <= 100; greenDuration++) {
            for (int redDuration = 5; redDuration <= 100; redDuration++) {
                OvitoWriter<Particle> ovitoWriter = null;
                // Map recording the time required for each car to complete a loop. Mapping is car ID => time taken
                Map<Integer, Integer> timeMap;
                boolean errored;
                do {
                    int t = 0;
                    try {
                        ovitoWriter = new OvitoWriter<>(Paths.get("timeMin" , "c"+NUM_CARS, String.format("g%d_r%d.txt", greenDuration, redDuration)));
                        List<Car> placeholders = new ArrayList<>(4);
                        placeholders.add(new Car(new Point2D.Double(0, 0), 0.1).fake());
                        placeholders.add(new Car(new Point2D.Double(ROAD_LENGTH, ROAD_LENGTH), 0.1).fake());

                         timeMap = new HashMap<>();

                        /* *************************************************************************************************************
                         *                                          HORIZONTAL MODEL
                         * ************************************************************************************************************/
                        List<Car> carsH = new ArrayList<>();
                        for(int pos : splitEvenly((int) (ROAD_LENGTH/2.0 - SECURITY_GAP), NUM_CARS)) {
                            carsH.add(new Car(new Point2D.Double(pos, ROAD_LENGTH/2.0), CAR_RADIUS));
                            timeMap.put(carsH.get(carsH.size()-1).getId(), 0);
                        }
                        List<TrafficLight> trafficLightsH = new ArrayList<>();
                        trafficLightsH.add(new TrafficLight(new Point2D.Double(ROAD_LENGTH/2.0, ROAD_LENGTH/2.0), redDuration, greenDuration, 0, new Point2D.Double(ROAD_LENGTH/2.0 + 10, ROAD_LENGTH/2.0)));
                        LiPumaNavas modelH = new LiPumaNavas(ROAD_LENGTH, MAX_SPEED, SECURITY_GAP, true, carsH, trafficLightsH);

                        /* *************************************************************************************************************
                         *                                          VERTICAL MODEL
                         * ************************************************************************************************************/
                        List<Car> carsV = new ArrayList<>();
                        // Use 2/3 the density of cars as horizontal model
                        for(int pos : splitEvenly((int) (ROAD_LENGTH/2.0 - SECURITY_GAP), (int) (NUM_CARS * (2.0 / 3)))) {
                            carsV.add(new Car(new Point2D.Double(ROAD_LENGTH/2.0, pos), CAR_RADIUS));
                            timeMap.put(carsV.get(carsV.size()-1).getId(), 0);
                        }
                        List<TrafficLight> trafficLightsV = new ArrayList<>();
                        trafficLightsV.add(new TrafficLight(new Point2D.Double(ROAD_LENGTH/2.0, ROAD_LENGTH/2.0), greenDuration, redDuration, redDuration, new Point2D.Double(ROAD_LENGTH/2.0, ROAD_LENGTH/2.0  + 10)));
                        LiPumaNavas modelV = new LiPumaNavas(ROAD_LENGTH, MAX_SPEED, 3, false, carsV, trafficLightsV);


                        while (timeMap.containsValue(0)) {
                            List<Particle> allParticles = withPlaceholders(placeholders, carsH);
                            allParticles.addAll(carsV);
                            allParticles.addAll(trafficLightsH);
                            allParticles.addAll(trafficLightsV);
                            ovitoWriter.exportPositions(allParticles, t);
                            // Record cars that looped
                            Map<Integer, Double> positionsBeforeH = positionsMap(carsH, modelH),
                                    positionsBeforeV = positionsMap(carsV, modelV);
                            carsH = modelH.evolve();
                            carsV = modelV.evolve();
                            recordLoopedCars(positionsBeforeH, positionsMap(carsH, modelH), timeMap, t);
                            recordLoopedCars(positionsBeforeV, positionsMap(carsV, modelV), timeMap, t);
                            // Update time
                            t++;
                            if (t > 500) {
//                                System.err.println("Simulation " + simulationName(NUM_CARS, greenDuration, redDuration) + " not completed after 500 seconds, aborting");
                                System.err.println("Simulation " + simulationName(NUM_CARS, greenDuration, redDuration) + " not completed after 500 seconds, skipping run");
//                                System.exit(1);
                                break;
                            }
                        }
                        System.out.format("Run %s completed at t=%d\n", simulationName(NUM_CARS, greenDuration, redDuration), t);
                        errored = false;
                        resultsFileWriter.write(String.format("%d,%d,%d\n", greenDuration, redDuration, t));
                        resultsFileWriter.flush();
                    } catch (IllegalStateException | IllegalArgumentException e) {
                        errored = true;
                        System.out.format("Error in run %s in t=%d: %s. Retrying\n", simulationName(NUM_CARS, greenDuration, redDuration), t, e.getMessage());
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
        resultsFileWriter.close();
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

    private static boolean recordLoopedCars(Map<Integer, Double> positionsMapBefore, Map<Integer, Double> positionsMapAfter, Map<Integer, Integer> timeMap, final int t) {
        if (!positionsMapBefore.keySet().equals(positionsMapAfter.keySet())) {
            throw new IllegalArgumentException(String.format("Key set mismatch, %s != %s", positionsMapBefore.toString(), positionsMapAfter.toString()));
        }
        AtomicBoolean result = new AtomicBoolean(false);
        positionsMapBefore.keySet().stream()
                .filter(id -> positionsMapAfter.get(id) < positionsMapBefore.get(id) && timeMap.get(id) == 0)
                .forEach(loopedId -> {
                    timeMap.put(loopedId, t);
                    result.set(true);
                });
        return result.get();
    }

    private static String simulationName(int numCars, int greenDuration, int redDuration) {
        return String.format("c%d_g%d_r%d", numCars, greenDuration, redDuration);
    }

    private static Map<Integer, Double> positionsMap(List<Car> cars, SingleLaneModel model) {
        Map<Integer, Double> result = new HashMap<>(cars.size());
        cars.forEach(c -> result.put(c.getId(), model.getPositionComponent(c)));
        return result;
    }
}
