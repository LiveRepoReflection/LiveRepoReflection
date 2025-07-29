import unittest
from congestion_control import Sender, BottleneckLink, Simulator

class TestCongestionControl(unittest.TestCase):
    def setUp(self):
        self.initial_rate = 10
        self.max_rate = 100
        self.capacity = 50
        self.buffer_size = 100
        self.duration = 100

    def test_sender_initialization(self):
        sender = Sender(self.initial_rate, self.max_rate)
        self.assertEqual(sender.get_rate(), self.initial_rate)

    def test_sender_rate_bounds(self):
        sender = Sender(self.initial_rate, self.max_rate)
        
        # Test max rate bound
        for _ in range(1000):  # Many ACKs to try to exceed max_rate
            sender.receive_ack()
        self.assertLessEqual(sender.get_rate(), self.max_rate)
        
        # Test minimum rate bound
        for _ in range(1000):  # Many loss indications to try to go below 0
            sender.receive_loss_indication()
        self.assertGreaterEqual(sender.get_rate(), 0)

    def test_bottleneck_link_capacity(self):
        link = BottleneckLink(self.capacity, self.buffer_size)
        packets_sent = self.capacity + 10  # Exceed capacity
        transmitted, loss = link.transmit(packets_sent)
        
        self.assertEqual(transmitted, self.capacity)
        self.assertTrue(loss)

    def test_bottleneck_link_buffer(self):
        link = BottleneckLink(self.capacity, self.buffer_size)
        packets_sent = self.buffer_size + 10  # Exceed buffer
        transmitted, loss = link.transmit(packets_sent)
        
        self.assertLessEqual(transmitted, self.buffer_size)
        self.assertTrue(loss)

    def test_bottleneck_link_feedback(self):
        link = BottleneckLink(self.capacity, self.buffer_size)
        packets_transmitted = 10
        acks, loss_indication = link.generate_feedback(packets_transmitted)
        
        self.assertEqual(acks, packets_transmitted)
        self.assertFalse(loss_indication)

    def test_simulation_basic(self):
        sender = Sender(self.initial_rate, self.max_rate)
        link = BottleneckLink(self.capacity, self.buffer_size)
        simulator = Simulator(sender, link, self.duration)
        
        rates = simulator.run()
        
        self.assertEqual(len(rates), self.duration)
        self.assertTrue(all(0 <= rate <= self.max_rate for rate in rates))

    def test_simulation_convergence(self):
        sender = Sender(self.initial_rate, self.max_rate)
        link = BottleneckLink(self.capacity, self.buffer_size)
        simulator = Simulator(sender, link, self.duration)
        
        rates = simulator.run()
        
        # Check if rates eventually stabilize around link capacity
        stable_threshold = 5  # Allow some variation
        final_rates = rates[-10:]  # Look at last 10 time units
        avg_final_rate = sum(final_rates) / len(final_rates)
        
        self.assertLess(abs(avg_final_rate - self.capacity), stable_threshold)

    def test_zero_capacity_link(self):
        sender = Sender(self.initial_rate, self.max_rate)
        link = BottleneckLink(0, self.buffer_size)
        simulator = Simulator(sender, link, self.duration)
        
        rates = simulator.run()
        
        # Rates should eventually drop to near zero
        self.assertLess(rates[-1], 1)

    def test_zero_buffer_size(self):
        sender = Sender(self.initial_rate, self.max_rate)
        link = BottleneckLink(self.capacity, 0)
        simulator = Simulator(sender, link, self.duration)
        
        rates = simulator.run()
        self.assertEqual(len(rates), self.duration)

    def test_high_initial_rate(self):
        sender = Sender(self.max_rate, self.max_rate)
        link = BottleneckLink(self.capacity, self.buffer_size)
        simulator = Simulator(sender, link, self.duration)
        
        rates = simulator.run()
        
        # Rate should decrease due to congestion
        self.assertLess(rates[-1], self.max_rate)

    def test_packet_rounding(self):
        sender = Sender(1.5, self.max_rate)  # Non-integer initial rate
        packets_sent = sender.send_packets(1)
        self.assertEqual(packets_sent, 1)  # Should round down

if __name__ == '__main__':
    unittest.main()