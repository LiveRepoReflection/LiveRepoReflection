import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.*;
import java.util.List;

class AlgoStockTraderTest {
    private AlgoStockTrader trader;
    
    @BeforeEach
    void setUp() {
        // Initialize with min_profit = 0.5 and max_staleness = 1000
        trader = new AlgoStockTrader(0.5, 1000);
    }

    @Test
    void testBasicArbitrageOpportunity() {
        List<ArbitrageOpportunity> opportunities = trader.processUpdates(List.of(
            new PriceUpdate(1000L, 1, 1, 10.0),
            new PriceUpdate(1100L, 1, 2, 10.7)
        ));

        assertThat(opportunities).hasSize(1);
        ArbitrageOpportunity opportunity = opportunities.get(0);
        assertThat(opportunity.stockId()).isEqualTo(1);
        assertThat(opportunity.buyExchangeId()).isEqualTo(1);
        assertThat(opportunity.sellExchangeId()).isEqualTo(2);
        assertThat(opportunity.buyPrice()).isEqualTo(10.0);
        assertThat(opportunity.sellPrice()).isEqualTo(10.7);
        assertThat(opportunity.timestamp()).isEqualTo(1100L);
    }

    @Test
    void testNoArbitrageWhenProfitTooSmall() {
        List<ArbitrageOpportunity> opportunities = trader.processUpdates(List.of(
            new PriceUpdate(1000L, 1, 1, 10.0),
            new PriceUpdate(1100L, 1, 2, 10.4) // Difference of 0.4, below min_profit
        ));

        assertThat(opportunities).isEmpty();
    }

    @Test
    void testNoArbitrageWhenDataStale() {
        List<ArbitrageOpportunity> opportunities = trader.processUpdates(List.of(
            new PriceUpdate(1000L, 1, 1, 10.0),
            new PriceUpdate(2500L, 1, 2, 11.0) // Time difference > max_staleness
        ));

        assertThat(opportunities).isEmpty();
    }

    @Test
    void testMultipleStocksMultipleExchanges() {
        List<ArbitrageOpportunity> opportunities = trader.processUpdates(List.of(
            new PriceUpdate(1000L, 1, 1, 10.0),
            new PriceUpdate(1100L, 1, 2, 10.7),
            new PriceUpdate(1200L, 2, 1, 20.0),
            new PriceUpdate(1300L, 2, 2, 20.8)
        ));

        assertThat(opportunities).hasSize(2);
        assertThat(opportunities).extracting("stockId")
                                .containsExactly(1, 2);
    }

    @Test
    void testOutOfOrderUpdates() {
        List<ArbitrageOpportunity> opportunities = trader.processUpdates(List.of(
            new PriceUpdate(1100L, 1, 2, 10.7),
            new PriceUpdate(1000L, 1, 1, 10.0)
        ));

        assertThat(opportunities).hasSize(1);
        ArbitrageOpportunity opportunity = opportunities.get(0);
        assertThat(opportunity.buyPrice()).isEqualTo(10.0);
        assertThat(opportunity.sellPrice()).isEqualTo(10.7);
    }

    @Test
    void testPriceUpdatesOverwritePreviousValues() {
        List<ArbitrageOpportunity> opportunities = trader.processUpdates(List.of(
            new PriceUpdate(1000L, 1, 1, 10.0),
            new PriceUpdate(1100L, 1, 1, 10.2), // Update price on exchange 1
            new PriceUpdate(1200L, 1, 2, 11.0)
        ));

        assertThat(opportunities).hasSize(1);
        ArbitrageOpportunity opportunity = opportunities.get(0);
        assertThat(opportunity.buyPrice()).isEqualTo(10.2);
        assertThat(opportunity.sellPrice()).isEqualTo(11.0);
    }

    @Test
    void testNoArbitrageWhenPricesEqual() {
        List<ArbitrageOpportunity> opportunities = trader.processUpdates(List.of(
            new PriceUpdate(1000L, 1, 1, 10.0),
            new PriceUpdate(1100L, 1, 2, 10.0)
        ));

        assertThat(opportunities).isEmpty();
    }

    @Test
    void testLargeNumberOfUpdates() {
        // Create a large number of updates to test performance
        List<PriceUpdate> updates = new java.util.ArrayList<>();
        for (int i = 0; i < 1000; i++) {
            updates.add(new PriceUpdate(1000L + i, i % 10, i % 5, 100.0 + i * 0.1));
        }

        assertThatCode(() -> trader.processUpdates(updates))
            .doesNotThrowAnyException();
    }

    @Test
    void testInvalidInputs() {
        assertThatThrownBy(() -> new AlgoStockTrader(0.0, 1000))
            .isInstanceOf(IllegalArgumentException.class);

        assertThatThrownBy(() -> new AlgoStockTrader(0.5, 50))
            .isInstanceOf(IllegalArgumentException.class);
    }

    @Test
    void testConcurrentUpdates() throws InterruptedException {
        int numberOfThreads = 10;
        Thread[] threads = new Thread[numberOfThreads];
        
        for (int i = 0; i < numberOfThreads; i++) {
            final int threadId = i;
            threads[i] = new Thread(() -> {
                List<PriceUpdate> updates = List.of(
                    new PriceUpdate(1000L + threadId, threadId, 1, 10.0 + threadId),
                    new PriceUpdate(1100L + threadId, threadId, 2, 11.0 + threadId)
                );
                trader.processUpdates(updates);
            });
        }

        for (Thread thread : threads) {
            thread.start();
        }

        for (Thread thread : threads) {
            thread.join();
        }
    }
}

record PriceUpdate(long timestamp, int stockId, int exchangeId, double price) {}
record ArbitrageOpportunity(int stockId, int buyExchangeId, int sellExchangeId, 
                           double buyPrice, double sellPrice, long timestamp) {}