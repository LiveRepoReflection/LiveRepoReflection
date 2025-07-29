import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.List;
import java.util.Arrays;
import java.util.ArrayList;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertThrows;

public class SkylineTest {
    
    private DynamicSkyline skyline;

    @BeforeEach
    public void setUp() {
        skyline = new DynamicSkyline();
    }

    @Test
    public void testEmptySkyline() {
        List<List<Integer>> result = skyline.getSkyline();
        assertThat(result).isEmpty();
    }

    @Test
    public void testSingleBuilding() {
        skyline.addBuilding(1, 5, 10);
        List<List<Integer>> expected = Arrays.asList(
            Arrays.asList(1, 10),
            Arrays.asList(5, 0)
        );
        assertThat(skyline.getSkyline()).isEqualTo(expected);
    }

    @Test
    public void testMultipleBuildingsNoOverlap() {
        skyline.addBuilding(1, 5, 10);
        skyline.addBuilding(6, 10, 15);
        List<List<Integer>> expected = Arrays.asList(
            Arrays.asList(1, 10),
            Arrays.asList(5, 0),
            Arrays.asList(6, 15),
            Arrays.asList(10, 0)
        );
        assertThat(skyline.getSkyline()).isEqualTo(expected);
    }

    @Test
    public void testMultipleBuildingsWithOverlap() {
        skyline.addBuilding(1, 5, 10);
        skyline.addBuilding(3, 7, 15);
        List<List<Integer>> expected = Arrays.asList(
            Arrays.asList(1, 10),
            Arrays.asList(3, 15),
            Arrays.asList(7, 0)
        );
        assertThat(skyline.getSkyline()).isEqualTo(expected);
    }

    @Test
    public void testRemoveBuilding() {
        skyline.addBuilding(1, 5, 10);
        skyline.addBuilding(3, 7, 15);
        skyline.removeBuilding(3, 7, 15);
        List<List<Integer>> expected = Arrays.asList(
            Arrays.asList(1, 10),
            Arrays.asList(5, 0)
        );
        assertThat(skyline.getSkyline()).isEqualTo(expected);
    }

    @Test
    public void testRemoveNonExistentBuilding() {
        skyline.addBuilding(1, 5, 10);
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            skyline.removeBuilding(3, 7, 15);
        });
        assertThat(exception.getMessage()).contains("Building does not exist");
    }

    @Test
    public void testCompletelyContainedBuilding() {
        skyline.addBuilding(1, 10, 10);
        skyline.addBuilding(3, 5, 20);
        List<List<Integer>> expected = Arrays.asList(
            Arrays.asList(1, 10),
            Arrays.asList(3, 20),
            Arrays.asList(5, 10),
            Arrays.asList(10, 0)
        );
        assertThat(skyline.getSkyline()).isEqualTo(expected);
    }

    @Test
    public void testIdenticalBuildings() {
        skyline.addBuilding(1, 5, 10);
        skyline.addBuilding(1, 5, 10);
        skyline.removeBuilding(1, 5, 10);
        List<List<Integer>> expected = Arrays.asList(
            Arrays.asList(1, 10),
            Arrays.asList(5, 0)
        );
        assertThat(skyline.getSkyline()).isEqualTo(expected);
    }

    @Test
    public void testMultipleRemoves() {
        skyline.addBuilding(1, 5, 10);
        skyline.addBuilding(3, 7, 15);
        skyline.addBuilding(6, 10, 12);
        
        skyline.removeBuilding(3, 7, 15);
        
        List<List<Integer>> expected = Arrays.asList(
            Arrays.asList(1, 10),
            Arrays.asList(5, 0),
            Arrays.asList(6, 12),
            Arrays.asList(10, 0)
        );
        assertThat(skyline.getSkyline()).isEqualTo(expected);
    }

    @Test
    public void testAddRemoveAdd() {
        skyline.addBuilding(1, 5, 10);
        skyline.removeBuilding(1, 5, 10);
        skyline.addBuilding(1, 5, 20);
        
        List<List<Integer>> expected = Arrays.asList(
            Arrays.asList(1, 20),
            Arrays.asList(5, 0)
        );
        assertThat(skyline.getSkyline()).isEqualTo(expected);
    }

    @Test
    public void testLargeNumbersRange() {
        skyline.addBuilding(0, 1_000_000_000, 1_000_000_000);
        List<List<Integer>> result = skyline.getSkyline();
        
        List<List<Integer>> expected = Arrays.asList(
            Arrays.asList(0, 1_000_000_000),
            Arrays.asList(1_000_000_000, 0)
        );
        assertThat(result).isEqualTo(expected);
    }

    @Test
    public void testPartialOverlaps() {
        skyline.addBuilding(1, 5, 10);
        skyline.addBuilding(4, 8, 15);
        skyline.addBuilding(7, 10, 8);
        
        List<List<Integer>> expected = Arrays.asList(
            Arrays.asList(1, 10),
            Arrays.asList(4, 15),
            Arrays.asList(8, 8),
            Arrays.asList(10, 0)
        );
        assertThat(skyline.getSkyline()).isEqualTo(expected);
    }

    @Test
    public void testSameHeightMerge() {
        skyline.addBuilding(1, 3, 10);
        skyline.addBuilding(3, 5, 10);
        
        List<List<Integer>> expected = Arrays.asList(
            Arrays.asList(1, 10),
            Arrays.asList(5, 0)
        );
        assertThat(skyline.getSkyline()).isEqualTo(expected);
    }

    @Test
    public void testComplexScenario() {
        skyline.addBuilding(2, 9, 10);
        skyline.addBuilding(3, 7, 15);
        skyline.addBuilding(5, 12, 12);
        skyline.addBuilding(15, 20, 10);
        skyline.addBuilding(19, 24, 8);
        
        skyline.removeBuilding(3, 7, 15);
        skyline.removeBuilding(15, 20, 10);
        
        List<List<Integer>> expected = Arrays.asList(
            Arrays.asList(2, 10),
            Arrays.asList(5, 12),
            Arrays.asList(12, 0),
            Arrays.asList(19, 8),
            Arrays.asList(24, 0)
        );
        assertThat(skyline.getSkyline()).isEqualTo(expected);
    }

    @Test
    public void testAddRemoveAddDifferentHeight() {
        skyline.addBuilding(1, 5, 10);
        skyline.removeBuilding(1, 5, 10);
        skyline.addBuilding(1, 5, 5);
        
        List<List<Integer>> expected = Arrays.asList(
            Arrays.asList(1, 5),
            Arrays.asList(5, 0)
        );
        assertThat(skyline.getSkyline()).isEqualTo(expected);
    }

    @Test
    public void testBuildingWithZeroHeight() {
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            skyline.addBuilding(1, 5, 0);
        });
        assertThat(exception.getMessage()).contains("height must be positive");
    }

    @Test
    public void testBuildingWithInvalidCoordinates() {
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            skyline.addBuilding(5, 1, 10);
        });
        assertThat(exception.getMessage()).contains("left must be less than right");
    }
}