package ar.edu.itba.ss.runners.singleLane.ondaVerde;

import ar.edu.itba.ss.files.OvitoWriter;
import ar.edu.itba.ss.models.SingleLaneModel;
import ar.edu.itba.ss.particles.Car;
import ar.edu.itba.ss.particles.Particle;
import ar.edu.itba.ss.particles.TrafficLight;
import ar.edu.itba.ss.runners.Runner;

import java.awt.geom.Point2D;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;

@SuppressWarnings("Duplicates")
public class OndaVerdeChangingGreen extends Runner {

    public static void main(String[] args) throws IOException {
        final int ROAD_LENGTH = 250,    // 250 * 7.5m = 1.875km
                MAX_SPEED = 3,          // 3 * 7.5 * 3.6 = 81km/h
                SECURITY_GAP = 1;

        final int GREEN_DURATION = 5,
                RED_DURATION = 10,
                PHASE_BETWEEN_LIGHTS = 5;
        final double car_radius = 0.5;
        final String experimentFolder = "changing_green";
        String experimentName;

        File outputFile = Paths.get("ondaVerde", experimentFolder, "_results.csv").toFile(),
                containingDir = outputFile.getParentFile();
        // Create directories if needed
        if (!containingDir.exists() && !containingDir.mkdirs()) {
            throw new IllegalArgumentException("Could not create directories for output files: " + outputFile.toString());
        }
        FileWriter resultsFileWriter = new FileWriter(outputFile);
        resultsFileWriter.write("greenDuration,redDuration,phaseBetweenLights,time\n");

        for (int i = 0; i < 100; i++) {
            int GREEN_DURATION_FINAL = GREEN_DURATION + i,
                    RED_DURATION_FINAL = RED_DURATION,
                    PHASE_BETWEEN_LIGHTS_FINAL = PHASE_BETWEEN_LIGHTS;
            experimentName = String.format("g%d_r%d_p%d", GREEN_DURATION_FINAL, RED_DURATION_FINAL, PHASE_BETWEEN_LIGHTS_FINAL);
            // Map recording the time required for each car to complete a loop. Mapping is car ID => time taken
            boolean errored;
            do {
                Map<Integer, Integer> timeMap = new HashMap<>();
                OvitoWriter<Particle> ovitoWriter = null;
                int t = 0;
                try {
                    ovitoWriter = new OvitoWriter<>(Paths.get("ondaVerde", experimentFolder, experimentName + ".txt"));
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
                        timeMap.put(carsH.get(carsH.size() - 1).getId(), -1);
                    }

                    /* *************************************************************************************************************
                     *                                      TRAFFIC LIGHTS EVERY ~400M
                     * ************************************************************************************************************/
                    List<TrafficLight> trafficLightsH = new ArrayList<>();
                    int phase = 0;
                    for (int x = 54; x < ROAD_LENGTH; x += 54) { // 54 * 7.5 = 405m
                        trafficLightsH.add(new TrafficLight(new Point2D.Double(x, 0), RED_DURATION_FINAL, GREEN_DURATION_FINAL, phase));
                        phase += PHASE_BETWEEN_LIGHTS_FINAL; // The phase varies between lights
                    }
                    ar.edu.itba.ss.models.LiPumaNavas modelH = new ar.edu.itba.ss.models.LiPumaNavas(ROAD_LENGTH, MAX_SPEED, SECURITY_GAP, true, carsH, trafficLightsH, 0, false);

                    while (timeMap.containsValue(-1)) {
                        List<Particle> allCars = withPlaceholders(placeholders, carsH);
                        allCars.addAll(trafficLightsH);
                        ovitoWriter.exportPositions(allCars, t);

                        // Record cars that looped
                        Map<Integer, Double> positionsBefore = positionsMap(carsH, modelH);
                        carsH = modelH.evolve();
                        recordLoopedCars(positionsBefore, positionsMap(carsH, modelH), timeMap, t);
                        t++;
                        if (t > 500) {
                            System.err.println("Simulation " + experimentName + " not completed after 500 seconds, terminating run");
                            break;
                        }
                    }
                    System.out.println("Run " + experimentName + " completed at t=" + t);
                    errored = false;
                    resultsFileWriter.write(String.format("%d,%d,%d,%d\n", GREEN_DURATION_FINAL, RED_DURATION_FINAL, PHASE_BETWEEN_LIGHTS_FINAL, t));
                    resultsFileWriter.flush();
                } catch (IllegalStateException | IllegalArgumentException e) {
                    errored = true;
                    System.out.format("Error in run at t=%d: %s. Retrying\n", t, e.getMessage());
                } finally {
                    if (ovitoWriter != null) {
                        ovitoWriter.close();
//                        Files.copy(Paths.get("out.txt"), Paths.get("in.txt"), StandardCopyOption.REPLACE_EXISTING);
                    }
                }
            } while (errored);
        }
        resultsFileWriter.close();
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

    /**
     * TODO NOW doc me
     * @param positionsMapBefore
     * @param positionsMapAfter
     * @param timeMap
     * @param t
     * @return
     */
    private static boolean recordLoopedCars(Map<Integer, Double> positionsMapBefore, Map<Integer, Double> positionsMapAfter, Map<Integer, Integer> timeMap, final int t) {
        if (!positionsMapBefore.keySet().equals(positionsMapAfter.keySet())) {
            throw new IllegalArgumentException(String.format("Key set mismatch, %s != %s", positionsMapBefore.toString(), positionsMapAfter.toString()));
        }
        AtomicBoolean result = new AtomicBoolean(false);
        positionsMapBefore.keySet().stream()
                .filter(id -> positionsMapAfter.get(id) < positionsMapBefore.get(id) && timeMap.get(id) == -1)
                .forEach(loopedId -> {
                    timeMap.put(loopedId, t);
                    result.set(true);
                });
        return result.get();
    }

    /**
     * TODO NOW doc me
     * @param cars
     * @param model
     * @return
     */
    private static Map<Integer, Double> positionsMap(List<Car> cars, SingleLaneModel model) {
        Map<Integer, Double> result = new HashMap<>(cars.size());
        cars.forEach(c -> result.put(c.getId(), model.getPositionComponent(c)));
        return result;
    }
}
