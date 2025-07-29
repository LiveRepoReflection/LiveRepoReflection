/**
 * A simple class representing a pair of values.
 * @param <T> The type of the first value
 * @param <U> The type of the second value
 */
public class Pair<T, U> {
    private final T first;
    private final U second;

    /**
     * Constructs a new Pair with the given values.
     * 
     * @param first The first value
     * @param second The second value
     */
    public Pair(T first, U second) {
        this.first = first;
        this.second = second;
    }

    /**
     * Gets the first value of the pair.
     * 
     * @return The first value
     */
    public T getFirst() {
        return first;
    }

    /**
     * Gets the second value of the pair.
     * 
     * @return The second value
     */
    public U getSecond() {
        return second;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        
        Pair<?, ?> pair = (Pair<?, ?>) o;
        
        if (first != null ? !first.equals(pair.first) : pair.first != null) return false;
        return second != null ? second.equals(pair.second) : pair.second == null;
    }

    @Override
    public int hashCode() {
        int result = first != null ? first.hashCode() : 0;
        result = 31 * result + (second != null ? second.hashCode() : 0);
        return result;
    }

    @Override
    public String toString() {
        return "(" + first + ", " + second + ")";
    }
}