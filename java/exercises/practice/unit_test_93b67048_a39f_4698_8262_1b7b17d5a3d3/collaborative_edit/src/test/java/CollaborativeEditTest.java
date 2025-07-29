package collaborative_edit;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import static org.junit.jupiter.api.Assertions.*;

public class CollaborativeEditTest {

    private CollaborativeEditor editor;

    @BeforeEach
    public void setup() {
        // Initialize the CollaborativeEditor with an empty document.
        editor = new CollaborativeEditor();
    }

    @Test
    public void testSequentialEdits() {
        // Test sequential edit operations.
        // Edit 1: Insert "Hello" at beginning.
        editor.applyEdit("user1", 1000L, 0, 0, "Hello");
        assertEquals("Hello", editor.getDocumentState(), "After inserting 'Hello'");

        // Edit 2: Append " World" at the end.
        editor.applyEdit("user1", 1001L, editor.getDocumentState().length(), 0, " World");
        assertEquals("Hello World", editor.getDocumentState(), "After appending ' World'");

        // Edit 3: Replace "World" with "Java" starting at index 6.
        editor.applyEdit("user2", 1002L, 6, 5, "Java");
        assertEquals("Hello Java", editor.getDocumentState(), "After replacing 'World' with 'Java'");
    }

    @Test
    public void testOverlapEditsConflictResolution() {
        // Start with a preset document.
        editor.applyEdit("user1", 900L, 0, 0, "ABCDEFGHIJ");
        String initial = editor.getDocumentState();
        assertEquals("ABCDEFGHIJ", initial, "Initial document state check.");

        // Two overlapping edits:
        // Edit 1: Replace characters at indices 2 to 5 with "1234" by user1 at timestamp 1100.
        editor.applyEdit("user1", 1100L, 2, 4, "1234");

        // Edit 2: Concurrently, replace characters at indices 4 to 7 with "WXYZ" by user2 at timestamp 1101.
        editor.applyEdit("user2", 1101L, 4, 4, "WXYZ");

        // Expected behavior: the operations are applied based on timestamp order.
        // First operation changes document to: "AB1234GHIJ"
        // Second operation then applies on the updated document starting at index 4:
        // "AB12" + "WXYZ" replacing "34GH" then "IJ" remains.
        String expected = "AB12WXYZIJ";
        assertEquals(expected, editor.getDocumentState(), "After overlapping edits with conflict resolution.");
    }

    @Test
    @Timeout(value = 5, unit = TimeUnit.SECONDS)
    public void testConcurrentEdits() throws InterruptedException {
        // Test that concurrent edits are handled correctly.
        // Start with an empty document.
        int numThreads = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        CountDownLatch latch = new CountDownLatch(numThreads);
        // Each thread will insert its unique string at the beginning.
        for (int i = 0; i < numThreads; i++) {
            final int id = i;
            executor.submit(() -> {
                // Each thread uses a unique timestamp to enforce order.
                editor.applyEdit("user" + id, System.currentTimeMillis(), 0, 0, "X" + id);
                latch.countDown();
            });
        }
        latch.await();
        executor.shutdown();
        // Because operations may be applied in timestamp order, the final document should
        // be a concatenation of all inserted strings at index 0 in some order.
        // We only assert that all expected substrings exist in the final document.
        String document = editor.getDocumentState();
        for (int i = 0; i < numThreads; i++) {
            assertTrue(document.contains("X" + i), "Document must contain substring 'X" + i + "'");
        }
    }

    @Test
    public void testDeletionAndInsertion() {
        // Create a base document.
        editor.applyEdit("user1", 1000L, 0, 0, "The quick brown fox jumps over the lazy dog");
        String base = editor.getDocumentState();
        assertEquals("The quick brown fox jumps over the lazy dog", base, "Base document check.");

        // Delete the word "brown " (indices 10 to 16) and replace with empty string.
        editor.applyEdit("user2", 1001L, 10, 6, "");
        String expectedAfterDeletion = "The quick fox jumps over the lazy dog";
        assertEquals(expectedAfterDeletion, editor.getDocumentState(), "After deletion of 'brown '");

        // Insert "red " at the same index 10.
        editor.applyEdit("user3", 1002L, 10, 0, "red ");
        String expectedAfterInsertion = "The quick red fox jumps over the lazy dog";
        assertEquals(expectedAfterInsertion, editor.getDocumentState(), "After inserting 'red '");
    }

    @Test
    public void testOutOfRangeEdits() {
        // Starting with a document.
        editor.applyEdit("user1", 1000L, 0, 0, "Hello");
        String current = editor.getDocumentState();
        assertEquals("Hello", current, "Initial state.");

        // Attempt an edit with start index beyond document length.
        Exception exception = assertThrows(IndexOutOfBoundsException.class, () -> {
            editor.applyEdit("user2", 1001L, current.length() + 5, 0, "World");
        });
        String expectedMessage = "start index out of bounds";
        String actualMessage = exception.getMessage();
        assertTrue(actualMessage.contains(expectedMessage), "Expected out-of-bounds exception message.");

        // Attempt an edit with deletion length extending beyond document.
        exception = assertThrows(IndexOutOfBoundsException.class, () -> {
            editor.applyEdit("user3", 1002L, 2, current.length(), "X");
        });
        expectedMessage = "deletion length exceeds document bounds";
        actualMessage = exception.getMessage();
        assertTrue(actualMessage.contains(expectedMessage), "Expected deletion out-of-bounds exception message.");
    }
}