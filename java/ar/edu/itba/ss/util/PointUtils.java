package ar.edu.itba.ss.util;

import java.awt.geom.Point2D;

public class PointUtils {

    /**
     * Get the magnitude of a 2-D point.
     *
     * @param point The point.
     * @return      Its magnitude.
     */
    public static double magnitude(Point2D point) {
        // magnitude == distance to origin
        return Math.sqrt(point.distance(new Point2D.Double(0, 0)));
    }

    /**
     * Get a pretty (ie. {@code (x, y)}) format of a 2D point.
     */
    public static String toString(Point2D point) {
        return "(" + point.getX() + ", " + point.getY() + ")";
    }
}
