import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class EditorTest {

    private CollaborativeEditor editor;

    @BeforeEach
    public void setUp() {
        editor = new CollaborativeEditor();
    }

    @Test
    public void testInsertSingleThread() {
        editor.insert("user1", 0, "Hello");
        assertEquals("Hello", editor.getDocument());
        editor.insert("user1", 5, " World");
        assertEquals("Hello World", editor.getDocument());
    }

    @Test
    public void testDeleteSingleThread() {
        editor.insert("user1", 0, "Hello World");
        editor.delete("user1", 5, 1);
        assertEquals("HelloWorld", editor.getDocument());
        editor.delete("user1", 0, 5);
        assertEquals("World", editor.getDocument());
    }

    @Test
    public void testInsertConcurrentSamePosition() throws InterruptedException {
        int threadCount = 10;
        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        CountDownLatch readyLatch = new CountDownLatch(threadCount);
        CountDownLatch startLatch = new CountDownLatch(1);
        CountDownLatch doneLatch = new CountDownLatch(threadCount);

        for (int i = 0; i < threadCount; i++) {
            final int index = i;
            executor.submit(() -> {
                try {
                    readyLatch.countDown();
                    startLatch.await();
                    editor.insert("user" + index, 0, "A");
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } finally {
                    doneLatch.countDown();
                }
            });
        }

        readyLatch.await();
        startLatch.countDown();
        doneLatch.await();
        executor.shutdown();

        String result = editor.getDocument();
        assertEquals(threadCount, result.length());
        for (char c : result.toCharArray()) {
            assertEquals('A', c);
        }
    }

    @Test
    public void testInsertConcurrentDifferentPositions() throws InterruptedException {
        editor.insert("user1", 0, "Hello");
        int threadCount = 5;
        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        CountDownLatch readyLatch = new CountDownLatch(threadCount);
        CountDownLatch startLatch = new CountDownLatch(1);
        CountDownLatch doneLatch = new CountDownLatch(threadCount);

        for (int i = 0; i < threadCount; i++) {
            final int index = i;
            executor.submit(() -> {
                try {
                    readyLatch.countDown();
                    startLatch.await();
                    int pos = editor.getDocument().length();
                    editor.insert("user" + index, pos, "X");
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } finally {
                    doneLatch.countDown();
                }
            });
        }

        readyLatch.await();
        startLatch.countDown();
        doneLatch.await();
        executor.shutdown();

        String doc = editor.getDocument();
        assertEquals(10, doc.length());
        assertEquals("Hello", doc.substring(0, 5));
        for (int i = 5; i < 10; i++) {
            assertEquals('X', doc.charAt(i));
        }
    }

    @Test
    public void testConcurrentInsertAndDelete() throws InterruptedException {
        editor.insert("user1", 0, "ABCDEFG");
        ExecutorService executor = Executors.newFixedThreadPool(2);
        CountDownLatch latch = new CountDownLatch(1);

        Runnable insertTask = () -> {
            try {
                latch.await();
                editor.insert("user2", 3, "123");
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        };

        Runnable deleteTask = () -> {
            try {
                latch.await();
                editor.delete("user3", 2, 3);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        };

        executor.submit(insertTask);
        executor.submit(deleteTask);
        latch.countDown();
        executor.shutdown();
        while (!executor.isTerminated()) {
            Thread.sleep(50);
        }

        String result = editor.getDocument();
        // The expected length is original length 7 plus inserted 3 minus deleted 3 = 7.
        assertEquals(7, result.length());
    }

    @Test
    public void testMultipleConcurrentDeletes() throws InterruptedException {
        editor.insert("user1", 0, "1234567890");
        int threadCount = 3;
        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        CountDownLatch readyLatch = new CountDownLatch(threadCount);
        CountDownLatch startLatch = new CountDownLatch(1);
        CountDownLatch doneLatch = new CountDownLatch(threadCount);

        for (int i = 0; i < threadCount; i++) {
            final int pos = 3;
            final int length = 4;
            executor.submit(() -> {
                try {
                    readyLatch.countDown();
                    startLatch.await();
                    editor.delete("user_del", pos, length);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } finally {
                    doneLatch.countDown();
                }
            });
        }

        readyLatch.await();
        startLatch.countDown();
        doneLatch.await();
        executor.shutdown();

        String result = editor.getDocument();
        assertTrue(result.length() >= 0 && result.length() <= 10);
    }
}