public class DummyService implements Service {
    private final String name;
    private boolean prepareResponse = true;
    private boolean noResponse = false;

    public DummyService(String name) {
        this.name = name;
    }

    public void setPrepareResponse(boolean response) {
        this.prepareResponse = response;
        this.noResponse = false;
    }

    public void setNoResponse(boolean noResponse) {
        this.noResponse = noResponse;
    }

    @Override
    public String getName() {
        return name;
    }

    @Override
    public boolean prepare(Transaction txn) {
        if (noResponse) {
            try {
                // Simulate no response by sleeping beyond the expected timeout.
                Thread.sleep(5000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return false;
        }
        return prepareResponse;
    }

    @Override
    public void commit(Transaction txn) {
        // Simulate the commit operation
    }

    @Override
    public void rollback(Transaction txn) {
        // Simulate the rollback operation
    }
}