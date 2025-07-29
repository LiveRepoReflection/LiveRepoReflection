public class Edge {
    public int node1Id;
    public int node2Id;
    public int dataTransferSize;
    
    public Edge(int node1Id, int node2Id, int dataTransferSize) {
        this.node1Id = node1Id;
        this.node2Id = node2Id;
        this.dataTransferSize = dataTransferSize;
    }
}