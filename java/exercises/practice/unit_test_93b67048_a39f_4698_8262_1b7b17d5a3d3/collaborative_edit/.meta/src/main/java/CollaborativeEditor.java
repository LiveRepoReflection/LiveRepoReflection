package collaborative_edit;

public class CollaborativeEditor {
    private final StringBuilder document;

    public CollaborativeEditor() {
        document = new StringBuilder();
    }

    public synchronized void applyEdit(String userId, long timestamp, int startIndex, int lengthToDelete, String replacementString) {
        if (startIndex < 0 || startIndex > document.length()) {
            throw new IndexOutOfBoundsException("start index out of bounds: " + startIndex);
        }
        if (startIndex + lengthToDelete > document.length()) {
            throw new IndexOutOfBoundsException("deletion length exceeds document bounds: startIndex=" + startIndex + ", lengthToDelete=" + lengthToDelete);
        }
        // Delete the specified segment.
        document.delete(startIndex, startIndex + lengthToDelete);
        // Insert the replacement string at startIndex.
        document.insert(startIndex, replacementString);
    }

    public synchronized String getDocumentState() {
        return document.toString();
    }
}