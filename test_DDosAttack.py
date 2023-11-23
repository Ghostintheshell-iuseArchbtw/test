import subprocess
import unittest

class DefenseScriptTests(unittest.TestCase):
    def test_nmap_attack_detected(self):
        # Simulate Nmap attack by running a subprocess with 'nmap' as the command
        subprocess.Popen(['nmap'], stdout=subprocess.PIPE).communicate()
        
        # Call the defense_script function
        defense_script()
        
        # Assert that the defensive actions were taken
        # You can add more specific assertions based on your implementation
        # For example, you can check if the attacker's IP address was blocked using a firewall rule
        self.assertTrue(subprocess.call(['iptables', '-C', 'INPUT', '-s', 'ATTACKER_IP_ADDRESS', '-j', 'DROP']) == 0)
    
    def test_no_nmap_attack_detected(self):
        # Call the defense_script function without running 'nmap' subprocess
        defense_script()
        
        # Assert that no defensive actions were taken
        # You can add more specific assertions based on your implementation
        # For example, you can check if the firewall rule to block the attacker's IP address does not exist
        self.assertFalse(subprocess.call(['iptables', '-C', 'INPUT', '-s', 'ATTACKER_IP_ADDRESS', '-j', 'DROP']) == 0)

if __name__ == '__main__':
    unittest.main()