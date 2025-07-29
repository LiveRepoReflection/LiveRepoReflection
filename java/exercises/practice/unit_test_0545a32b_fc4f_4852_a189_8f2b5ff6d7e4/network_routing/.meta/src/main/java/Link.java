public class Link {
    public int node1;
    public int node2;
    public int[] costs;

    public Link(int node1, int node2, int[] costs) {
        this.node1 = node1;
        this.node2 = node2;
        this.costs = new int[costs.length];
        System.arraycopy(costs, 0, this.costs, 0, costs.length);
    }

    public double getWeightedCost(double[] weights) {
        double total = 0;
        for (int i = 0; i < costs.length; i++) {
            total += costs[i] * weights[i];
        }
        return total;
    }
}