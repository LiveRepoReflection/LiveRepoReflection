/**
 * Represents a fractal transformation between a domain block and a range block.
 * This class stores all parameters needed to transform a domain block to approximate a range block.
 */
public class Transformation {
    public final int rangeRow;     // Row coordinate of range block top-left corner
    public final int rangeCol;     // Column coordinate of range block top-left corner
    public final int domainRow;    // Row coordinate of domain block top-left corner
    public final int domainCol;    // Column coordinate of domain block top-left corner
    public final int rotation;     // Rotation angle in degrees (0, 90, 180, 270)
    public final boolean flip;     // Whether to apply horizontal flip
    public final double scale;     // Intensity scaling factor
    public final double offset;    // Intensity offset
    public final double rmse;      // Root Mean Squared Error of the transformation

    /**
     * Creates a new transformation with the specified parameters.
     *
     * @param rangeRow Row coordinate of range block top-left corner
     * @param rangeCol Column coordinate of range block top-left corner
     * @param domainRow Row coordinate of domain block top-left corner
     * @param domainCol Column coordinate of domain block top-left corner
     * @param rotation Rotation angle in degrees (0, 90, 180, 270)
     * @param flip Whether to apply horizontal flip
     * @param scale Intensity scaling factor
     * @param offset Intensity offset
     * @param rmse Root Mean Squared Error of the transformation
     */
    public Transformation(int rangeRow, int rangeCol, int domainRow, int domainCol,
                         int rotation, boolean flip, double scale, double offset, double rmse) {
        this.rangeRow = rangeRow;
        this.rangeCol = rangeCol;
        this.domainRow = domainRow;
        this.domainCol = domainCol;
        this.rotation = rotation;
        this.flip = flip;
        this.scale = scale;
        this.offset = offset;
        this.rmse = rmse;
    }

    @Override
    public String toString() {
        return String.format("Transformation(rangeRow=%d, rangeCol=%d, domainRow=%d, domainCol=%d, " +
                            "rotation=%d, flip=%b, scale=%.4f, offset=%.4f, rmse=%.4f)",
                            rangeRow, rangeCol, domainRow, domainCol,
                            rotation, flip, scale, offset, rmse);
    }
}