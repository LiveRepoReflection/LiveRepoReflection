public class WorkerNode {
    private String workerId;
    private Resource totalResource;
    private Resource availableResource;
    private boolean active;

    public WorkerNode(String workerId, Resource totalResource) {
        this.workerId = workerId;
        this.totalResource = totalResource;
        this.availableResource = new Resource(totalResource.getCpuCores(), totalResource.getMemoryMB());
        this.active = true;
    }

    public String getWorkerId() {
        return workerId;
    }

    public Resource getTotalResource() {
        return totalResource;
    }

    public synchronized Resource getAvailableResource() {
        return availableResource;
    }

    public synchronized boolean isActive() {
        return active;
    }

    public synchronized void deactivate() {
        active = false;
    }

    public synchronized boolean canAllocate(Resource req) {
        return availableResource.getCpuCores() >= req.getCpuCores() && availableResource.getMemoryMB() >= req.getMemoryMB();
    }

    public synchronized void allocate(Resource req) {
        int newCores = availableResource.getCpuCores() - req.getCpuCores();
        int newMemory = availableResource.getMemoryMB() - req.getMemoryMB();
        availableResource = new Resource(newCores, newMemory);
    }

    public synchronized void release(Resource req) {
        int newCores = availableResource.getCpuCores() + req.getCpuCores();
        int newMemory = availableResource.getMemoryMB() + req.getMemoryMB();
        if(newCores > totalResource.getCpuCores()) {
            newCores = totalResource.getCpuCores();
        }
        if(newMemory > totalResource.getMemoryMB()) {
            newMemory = totalResource.getMemoryMB();
        }
        availableResource = new Resource(newCores, newMemory);
    }
}