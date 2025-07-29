package traffic_analyzer

import "sort"

type logEntry struct {
	timestamp        int64
	sourceIP         string
	destinationIP    string
	bytesTransferred int64
}

type TrafficAnalyzer struct {
	logs []logEntry
}

func NewTrafficAnalyzer() *TrafficAnalyzer {
	return &TrafficAnalyzer{
		logs: make([]logEntry, 0),
	}
}

func (ta *TrafficAnalyzer) IngestLogEntry(timestamp int64, sourceIP string, destinationIP string, bytesTransferred int64) {
	ta.logs = append(ta.logs, logEntry{
		timestamp:        timestamp,
		sourceIP:         sourceIP,
		destinationIP:    destinationIP,
		bytesTransferred: bytesTransferred,
	})
}

func (ta *TrafficAnalyzer) TopKDestinationIPs(startTime, endTime int64, k int) []string {
	if startTime > endTime || k <= 0 {
		return []string{}
	}
	freq := make(map[string]int)
	for _, entry := range ta.logs {
		if entry.timestamp >= startTime && entry.timestamp <= endTime {
			freq[entry.destinationIP]++
		}
	}
	type ipCount struct {
		ip    string
		count int
	}
	ipCounts := make([]ipCount, 0, len(freq))
	for ip, count := range freq {
		ipCounts = append(ipCounts, ipCount{ip: ip, count: count})
	}
	sort.Slice(ipCounts, func(i, j int) bool {
		if ipCounts[i].count == ipCounts[j].count {
			return ipCounts[i].ip < ipCounts[j].ip
		}
		return ipCounts[i].count > ipCounts[j].count
	})
	n := k
	if len(ipCounts) < k {
		n = len(ipCounts)
	}
	result := make([]string, 0, n)
	for i := 0; i < n; i++ {
		result = append(result, ipCounts[i].ip)
	}
	return result
}

func (ta *TrafficAnalyzer) AverageBytesTransferred(ip string, startTime, endTime int64) float64 {
	if startTime > endTime {
		return 0.0
	}
	var total int64 = 0
	count := 0
	for _, entry := range ta.logs {
		if entry.timestamp >= startTime && entry.timestamp <= endTime && entry.sourceIP == ip {
			total += entry.bytesTransferred
			count++
		}
	}
	if count == 0 {
		return 0.0
	}
	return float64(total) / float64(count)
}