package scalable_analytics

import (
	"errors"
	"math"
	"sort"
)

type Event struct {
	Timestamp int64
	NodeID    string
	Metric    string
	Value     float64
}

type AggregationResult struct {
	Count   int
	Sum     float64
	Average float64
	Min     float64
	Max     float64
	StdDev  float64
}

func AggregateEvents(events []Event, metric string, start, end int64) (map[string]AggregationResult, error) {
	if len(events) == 0 {
		return nil, errors.New("no events provided")
	}
	nodeValues := make(map[string][]float64)
	for _, event := range events {
		if event.Metric != metric {
			continue
		}
		if event.Timestamp < start || event.Timestamp > end {
			continue
		}
		nodeValues[event.NodeID] = append(nodeValues[event.NodeID], event.Value)
	}
	if len(nodeValues) == 0 {
		return nil, errors.New("no matching events in the given time window")
	}
	results := make(map[string]AggregationResult)
	for node, values := range nodeValues {
		if len(values) == 0 {
			continue
		}
		count := len(values)
		sum := 0.0
		min := values[0]
		max := values[0]
		for _, v := range values {
			sum += v
			if v < min {
				min = v
			}
			if v > max {
				max = v
			}
		}
		avg := sum / float64(count)
		varianceSum := 0.0
		for _, v := range values {
			diff := v - avg
			varianceSum += diff * diff
		}
		stddev := math.Sqrt(varianceSum / float64(count))
		results[node] = AggregationResult{
			Count:   count,
			Sum:     sum,
			Average: avg,
			Min:     min,
			Max:     max,
			StdDev:  stddev,
		}
	}
	return results, nil
}

func GetTopKAnomalies(events []Event, metric string, start, end int64, k int) ([]string, error) {
	if len(events) == 0 {
		return nil, errors.New("no events provided")
	}
	eventsByTimestamp := make(map[int64][]Event)
	for _, event := range events {
		if event.Metric != metric {
			continue
		}
		if event.Timestamp < start || event.Timestamp > end {
			continue
		}
		eventsByTimestamp[event.Timestamp] = append(eventsByTimestamp[event.Timestamp], event)
	}
	if len(eventsByTimestamp) == 0 {
		return nil, errors.New("no matching events in the given time window")
	}
	medianByTimestamp := make(map[int64]float64)
	for ts, evtSlice := range eventsByTimestamp {
		vals := make([]float64, len(evtSlice))
		for i, e := range evtSlice {
			vals[i] = e.Value
		}
		sort.Float64s(vals)
		n := len(vals)
		var median float64
		if n%2 == 1 {
			median = vals[n/2]
		} else {
			median = (vals[n/2-1] + vals[n/2]) / 2.0
		}
		medianByTimestamp[ts] = median
	}
	type nodeAnomaly struct {
		total float64
		count int
	}
	anomalies := make(map[string]nodeAnomaly)
	for ts, evtSlice := range eventsByTimestamp {
		median := medianByTimestamp[ts]
		for _, e := range evtSlice {
			diff := math.Abs(e.Value - median)
			na := anomalies[e.NodeID]
			na.total += diff
			na.count++
			anomalies[e.NodeID] = na
		}
	}
	type nodeScore struct {
		node  string
		score float64
	}
	scores := make([]nodeScore, 0, len(anomalies))
	for node, na := range anomalies {
		avgAnomaly := na.total / float64(na.count)
		scores = append(scores, nodeScore{node: node, score: avgAnomaly})
	}
	sort.Slice(scores, func(i, j int) bool {
		if scores[i].score == scores[j].score {
			return scores[i].node < scores[j].node
		}
		return scores[i].score > scores[j].score
	})
	if k > len(scores) {
		k = len(scores)
	}
	result := make([]string, 0, k)
	for i := 0; i < k; i++ {
		result = append(result, scores[i].node)
	}
	return result, nil
}

func ComputeCorrelation(events []Event, m1, m2 string, start, end int64) (map[string]float64, error) {
	if len(events) == 0 {
		return nil, errors.New("no events provided")
	}
	type metricValue struct {
		Timestamp int64
		Value     float64
	}
	nodeMetrics := make(map[string]map[string][]metricValue)
	for _, event := range events {
		if event.Timestamp < start || event.Timestamp > end {
			continue
		}
		if event.Metric != m1 && event.Metric != m2 {
			continue
		}
		if _, exists := nodeMetrics[event.NodeID]; !exists {
			nodeMetrics[event.NodeID] = make(map[string][]metricValue)
		}
		nodeMetrics[event.NodeID][event.Metric] = append(nodeMetrics[event.NodeID][event.Metric], metricValue{Timestamp: event.Timestamp, Value: event.Value})
	}
	correlations := make(map[string]float64)
	for node, metrics := range nodeMetrics {
		list1, ok1 := metrics[m1]
		list2, ok2 := metrics[m2]
		if !ok1 || !ok2 {
			continue
		}
		m1Map := make(map[int64]float64)
		m2Map := make(map[int64]float64)
		for _, v := range list1 {
			m1Map[v.Timestamp] = v.Value
		}
		for _, v := range list2 {
			m2Map[v.Timestamp] = v.Value
		}
		var x []float64
		var y []float64
		for ts, v1 := range m1Map {
			if v2, exists := m2Map[ts]; exists {
				x = append(x, v1)
				y = append(y, v2)
			}
		}
		if len(x) < 2 {
			continue
		}
		corr, err := pearsonCorrelation(x, y)
		if err != nil {
			continue
		}
		correlations[node] = corr
	}
	if len(correlations) == 0 {
		return nil, errors.New("not enough data to compute correlations")
	}
	return correlations, nil
}

func pearsonCorrelation(x, y []float64) (float64, error) {
	n := float64(len(x))
	if n < 2 {
		return 0, errors.New("not enough data points")
	}
	var sumX, sumY, sumXY, sumX2, sumY2 float64
	for i := 0; i < len(x); i++ {
		sumX += x[i]
		sumY += y[i]
		sumXY += x[i] * y[i]
		sumX2 += x[i] * x[i]
		sumY2 += y[i] * y[i]
	}
	numerator := n*sumXY - sumX*sumY
	denomPart1 := n*sumX2 - sumX*sumX
	denomPart2 := n*sumY2 - sumY*sumY
	denominator := math.Sqrt(denomPart1 * denomPart2)
	if denominator == 0 {
		return 0, errors.New("division by zero in correlation calculation")
	}
	return numerator / denominator, nil
}