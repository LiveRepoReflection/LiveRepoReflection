import unittest
from packet_analyzer import PacketAnalyzer

class TestPacketAnalyzer(unittest.TestCase):
    def setUp(self):
        # Default configuration values
        self.port_scan_threshold = 3
        self.time_window_ms = 60000
        self.large_packet_size = 1500
        self.syn_flood_threshold = 5
        self.blacklist = ["192.168.1.100", "10.0.0.50"]
        self.normal_combinations = [("TCP", 80), ("TCP", 443), ("UDP", 53)]
        
        # Create analyzer with configuration
        self.analyzer = PacketAnalyzer(
            port_scan_threshold=self.port_scan_threshold,
            time_window_ms=self.time_window_ms,
            large_packet_size=self.large_packet_size,
            syn_flood_threshold=self.syn_flood_threshold,
            blacklist=self.blacklist,
            normal_combinations=self.normal_combinations
        )

    def test_blacklisted_ips(self):
        # Test source IP blacklisted
        packet1 = "1678886400000,192.168.1.100,10.0.0.20,54321,80,TCP,1024,ACK"
        self.analyzer.process_packet(packet1)
        
        # Test destination IP blacklisted
        packet2 = "1678886400001,192.168.1.1,10.0.0.50,54322,80,TCP,1024,ACK"
        self.analyzer.process_packet(packet2)
        
        # Test non-blacklisted IPs
        packet3 = "1678886400002,192.168.1.2,10.0.0.3,54323,80,TCP,1024,ACK"
        self.analyzer.process_packet(packet3)
        
        flagged_packets = self.analyzer.get_flagged_packets()
        self.assertEqual(len(flagged_packets), 2)
        self.assertTrue(flagged_packets[0].startswith("BLACKLIST:"))
        self.assertTrue(flagged_packets[1].startswith("BLACKLIST:"))

    def test_port_scanning(self):
        # Generate port scanning pattern: same source IP to different ports within time window
        base_time = 1678886400000
        source_ip = "192.168.0.1"
        dest_ip = "10.0.0.1"
        
        # Send packets to different ports
        for i in range(self.port_scan_threshold + 1):
            packet = f"{base_time + i * 100},{source_ip},{dest_ip},54321,{8000 + i},TCP,100,SYN"
            self.analyzer.process_packet(packet)
        
        # Send legit traffic from another IP
        for i in range(self.port_scan_threshold):
            packet = f"{base_time + i * 100},192.168.0.2,{dest_ip},54321,{9000 + i},TCP,100,SYN"
            self.analyzer.process_packet(packet)
            
        flagged_packets = self.analyzer.get_flagged_packets()
        # Expect port_scan_threshold + 1 packets from first IP flagged (all after threshold is reached)
        port_scan_flags = [p for p in flagged_packets if p.startswith("PORTSCAN:")]
        self.assertEqual(len(port_scan_flags), 1)  # Only the last packet gets flagged

    def test_port_scanning_outside_time_window(self):
        # Generate port scanning pattern but outside the time window
        base_time = 1678886400000
        source_ip = "192.168.0.1"
        dest_ip = "10.0.0.1"
        
        # Send packets to different ports with big time gaps
        for i in range(self.port_scan_threshold + 1):
            packet = f"{base_time + i * (self.time_window_ms + 1000)},{source_ip},{dest_ip},54321,{8000 + i},TCP,100,SYN"
            self.analyzer.process_packet(packet)
            
        flagged_packets = self.analyzer.get_flagged_packets()
        port_scan_flags = [p for p in flagged_packets if p.startswith("PORTSCAN:")]
        self.assertEqual(len(port_scan_flags), 0)  # No packets should be flagged

    def test_large_packet_size(self):
        # Test packet exceeding size threshold
        packet1 = f"1678886400000,192.168.1.2,10.0.0.3,54321,80,TCP,{self.large_packet_size + 1},ACK"
        self.analyzer.process_packet(packet1)
        
        # Test packet at size threshold
        packet2 = f"1678886400001,192.168.1.2,10.0.0.3,54322,80,TCP,{self.large_packet_size},ACK"
        self.analyzer.process_packet(packet2)
        
        # Test packet below size threshold
        packet3 = f"1678886400002,192.168.1.2,10.0.0.3,54323,80,TCP,{self.large_packet_size - 1},ACK"
        self.analyzer.process_packet(packet3)
        
        flagged_packets = self.analyzer.get_flagged_packets()
        large_size_flags = [p for p in flagged_packets if p.startswith("LARGESIZE:")]
        self.assertEqual(len(large_size_flags), 1)
        self.assertTrue(large_size_flags[0].startswith(f"LARGESIZE:{packet1}"))

    def test_syn_flood(self):
        # Generate SYN flood pattern: many SYN packets to same destination IP
        base_time = 1678886400000
        dest_ip = "10.0.0.1"
        
        # Send SYN packets from different source IPs to same destination
        for i in range(self.syn_flood_threshold + 1):
            packet = f"{base_time + i * 100},192.168.0.{i},{dest_ip},54321,80,TCP,100,SYN"
            self.analyzer.process_packet(packet)
            
        # Send non-SYN packets
        packet = f"{base_time + 1000},192.168.0.10,{dest_ip},54321,80,TCP,100,ACK"
        self.analyzer.process_packet(packet)
        
        flagged_packets = self.analyzer.get_flagged_packets()
        syn_flood_flags = [p for p in flagged_packets if p.startswith("SYNFLOOD:")]
        self.assertEqual(len(syn_flood_flags), 1)  # Only the last SYN packet gets flagged

    def test_syn_flood_outside_time_window(self):
        # Generate SYN packets outside time window
        base_time = 1678886400000
        dest_ip = "10.0.0.1"
        
        # Send SYN packets with big time gaps
        for i in range(self.syn_flood_threshold + 1):
            packet = f"{base_time + i * (self.time_window_ms + 1000)},192.168.0.{i},{dest_ip},54321,80,TCP,100,SYN"
            self.analyzer.process_packet(packet)
            
        flagged_packets = self.analyzer.get_flagged_packets()
        syn_flood_flags = [p for p in flagged_packets if p.startswith("SYNFLOOD:")]
        self.assertEqual(len(syn_flood_flags), 0)  # No packets should be flagged

    def test_unusual_protocol_port(self):
        # Test unusual protocol/port combination
        packet1 = "1678886400000,192.168.1.2,10.0.0.3,54321,8080,TCP,1000,ACK"  # TCP/8080 not in normal_combinations
        self.analyzer.process_packet(packet1)
        
        # Test normal protocol/port combination
        packet2 = "1678886400001,192.168.1.2,10.0.0.3,54322,80,TCP,1000,ACK"  # TCP/80 is in normal_combinations
        self.analyzer.process_packet(packet2)
        
        packet3 = "1678886400002,192.168.1.2,10.0.0.3,54323,53,UDP,1000,NONE"  # UDP/53 is in normal_combinations
        self.analyzer.process_packet(packet3)
        
        flagged_packets = self.analyzer.get_flagged_packets()
        unusual_flags = [p for p in flagged_packets if p.startswith("UNUSUAL:")]
        self.assertEqual(len(unusual_flags), 1)
        self.assertTrue(unusual_flags[0].startswith(f"UNUSUAL:{packet1}"))

    def test_multiple_flags(self):
        # Test packet meeting multiple flag criteria
        packet1 = f"1678886400000,{self.blacklist[0]},10.0.0.1,54321,8080,TCP,{self.large_packet_size + 100},SYN"
        # This packet should be flagged for: blacklist, unusual protocol/port, and large size
        self.analyzer.process_packet(packet1)
        
        flagged_packets = self.analyzer.get_flagged_packets()
        self.assertEqual(len(flagged_packets), 3)
        
        # Check all three flags exist for this packet
        flag_types = [p.split(':', 1)[0] for p in flagged_packets]
        self.assertIn("BLACKLIST", flag_types)
        self.assertIn("LARGESIZE", flag_types)
        self.assertIn("UNUSUAL", flag_types)

    def test_empty_input(self):
        # Test with no packets
        flagged_packets = self.analyzer.get_flagged_packets()
        self.assertEqual(len(flagged_packets), 0)

    def test_cleanup_old_data(self):
        # Test that old data gets cleaned up properly
        base_time = 1678886400000
        source_ip = "192.168.0.1"
        dest_ip = "10.0.0.1"
        
        # Send initial packets
        for i in range(2):
            packet = f"{base_time + i * 100},{source_ip},{dest_ip},54321,{8000 + i},TCP,100,SYN"
            self.analyzer.process_packet(packet)
            
        # Jump way ahead in time and send new packet
        future_packet = f"{base_time + self.time_window_ms * 2},{source_ip},{dest_ip},54321,8002,TCP,100,SYN"
        self.analyzer.process_packet(future_packet)
        
        # Check internal state (we'll need to expose this for testing)
        # This is a bit implementation-dependent, but we want to verify the old data is gone
        if hasattr(self.analyzer, "_port_scan_records"):
            for record in self.analyzer._port_scan_records.values():
                # Verify no ancient records remain
                self.assertTrue(all(ts > base_time + self.time_window_ms for ts in record.keys()))

    def test_multiple_rules_triggered_separately(self):
        # Test packets triggering different rules
        base_time = 1678886400000
        
        # Blacklist rule
        packet1 = f"{base_time},192.168.1.100,10.0.0.1,54321,80,TCP,100,ACK"
        self.analyzer.process_packet(packet1)
        
        # Large size rule
        packet2 = f"{base_time + 100},192.168.1.2,10.0.0.3,54321,80,TCP,{self.large_packet_size + 1},ACK"
        self.analyzer.process_packet(packet2)
        
        # Unusual protocol/port rule
        packet3 = f"{base_time + 200},192.168.1.2,10.0.0.3,54321,8080,TCP,100,ACK"
        self.analyzer.process_packet(packet3)
        
        flagged_packets = self.analyzer.get_flagged_packets()
        self.assertEqual(len(flagged_packets), 3)
        
        # Check all three types of flags exist
        flag_types = [p.split(':', 1)[0] for p in flagged_packets]
        self.assertIn("BLACKLIST", flag_types)
        self.assertIn("LARGESIZE", flag_types)
        self.assertIn("UNUSUAL", flag_types)
        
if __name__ == '__main__':
    unittest.main()