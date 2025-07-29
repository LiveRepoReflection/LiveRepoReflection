import java.util.concurrent.locks.ReentrantReadWriteLock;

public class CollaborativeEditor {
    private final StringBuilder document;
    private final ReentrantReadWriteLock lock;

    public CollaborativeEditor() {
        this.document = new StringBuilder();
        this.lock = new ReentrantReadWriteLock();
    }

    /**
     * Inserts the given text at the specified position.
     * The operation is synchronized to ensure thread safety.
     *
     * @param userId the id of the user performing the insert
     * @param position the 0-indexed position to insert text
     * @param text the text to insert
     * @throws IllegalArgumentException if text is null
     */
    public void insert(String userId, int position, String text) {
        if (text == null) {
            throw new IllegalArgumentException("Text cannot be null");
        }
        lock.writeLock().lock();
        try {
            // The position is assumed valid as per constraints.
            document.insert(position, text);
        } finally {
            lock.writeLock().unlock();
        }
    }

    /**
     * Deletes a substring from the document.
     * The deletion is performed atomically under a write lock.
     *
     * @param userId the id of the user performing the deletion
     * @param position the starting 0-indexed position of deletion
     * @param length the number of characters to delete
     * @throws IndexOutOfBoundsException if the range is invalid
     */
    public void delete(String userId, int position, int length) {
        lock.writeLock().lock();
        try {
            if (position < 0 || position + length > document.length()) {
                throw new IndexOutOfBoundsException("Deletion range is invalid.");
            }
            document.delete(position, position + length);
        } finally {
            lock.writeLock().unlock();
        }
    }

    /**
     * Returns the current content of the document.
     * Utilizes a read lock to allow concurrent access by multiple threads.
     *
     * @return the current document as a String
     */
    public String getDocument() {
        lock.readLock().lock();
        try {
            return document.toString();
        } finally {
            lock.readLock().unlock();
        }
    }
}