import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantReadWriteLock;

public class AlgoStockTrader {
    private final double minProfit;
    private final long maxStaleness;
    
    // Thread-safe map to store latest price data for each stock and exchange
    private final ConcurrentHashMap<Integer, StockData> stockDataMap;

    public AlgoStockTrader(double minProfit, long maxStaleness) {
        if (minProfit < 0.01 || minProfit > 10.0) {
            throw new IllegalArgumentException("minProfit must be between 0.01 and 10.0");
        }
        if (maxStaleness < 100 || maxStaleness > 5000) {
            throw new IllegalArgumentException("maxStaleness must be between 100 and 5000");
        }
        
        this.minProfit = minProfit;
        this.maxStaleness = maxStaleness;
        this.stockDataMap = new ConcurrentHashMap<>();
    }

    public List<ArbitrageOpportunity> processUpdates(List<PriceUpdate> updates) {
        List<ArbitrageOpportunity> opportunities = new ArrayList<>();
        
        for (PriceUpdate update : updates) {
            StockData stockData = stockDataMap.computeIfAbsent(
                update.stockId(), 
                k -> new StockData()
            );
            
            stockData.updatePrice(update);
            
            List<ArbitrageOpportunity> newOpportunities = 
                stockData.findArbitrageOpportunities(
                    update.stockId(), 
                    minProfit, 
                    maxStaleness
                );
            
            opportunities.addAll(newOpportunities);
        }
        
        return opportunities;
    }

    private static class StockData {
        private final Map<Integer, ExchangeData> exchangeData;
        private final ReentrantReadWriteLock lock;

        public StockData() {
            this.exchangeData = new HashMap<>();
            this.lock = new ReentrantReadWriteLock();
        }

        public void updatePrice(PriceUpdate update) {
            lock.writeLock().lock();
            try {
                exchangeData.put(
                    update.exchangeId(),
                    new ExchangeData(update.price(), update.timestamp())
                );
            } finally {
                lock.writeLock().unlock();
            }
        }

        public List<ArbitrageOpportunity> findArbitrageOpportunities(
            int stockId, 
            double minProfit, 
            long maxStaleness
        ) {
            lock.readLock().lock();
            try {
                List<ArbitrageOpportunity> opportunities = new ArrayList<>();
                
                for (Map.Entry<Integer, ExchangeData> buyEntry : exchangeData.entrySet()) {
                    int buyExchangeId = buyEntry.getKey();
                    ExchangeData buyData = buyEntry.getValue();
                    
                    for (Map.Entry<Integer, ExchangeData> sellEntry : exchangeData.entrySet()) {
                        int sellExchangeId = sellEntry.getKey();
                        if (buyExchangeId == sellExchangeId) continue;
                        
                        ExchangeData sellData = sellEntry.getValue();
                        
                        // Check time staleness
                        long timeDiff = Math.abs(
                            sellData.timestamp - buyData.timestamp
                        );
                        if (timeDiff > maxStaleness) continue;
                        
                        // Check profit threshold
                        double profit = sellData.price - buyData.price;
                        if (profit >= minProfit) {
                            opportunities.add(new ArbitrageOpportunity(
                                stockId,
                                buyExchangeId,
                                sellExchangeId,
                                buyData.price,
                                sellData.price,
                                Math.max(buyData.timestamp, sellData.timestamp)
                            ));
                        }
                    }
                }
                
                return opportunities;
            } finally {
                lock.readLock().unlock();
            }
        }
    }

    private static class ExchangeData {
        private final double price;
        private final long timestamp;

        public ExchangeData(double price, long timestamp) {
            this.price = price;
            this.timestamp = timestamp;
        }
    }
}

record PriceUpdate(long timestamp, int stockId, int exchangeId, double price) {}
record ArbitrageOpportunity(int stockId, int buyExchangeId, int sellExchangeId, 
                           double buyPrice, double sellPrice, long timestamp) {}