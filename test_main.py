import unittest
from unittestbash import BashFunctionAnalyzer  # Adjust according to your structure
import subprocess

class TestMain(unittest.TestCase):

    analyzer = None  # Class variable to store the analyzer instance

    @classmethod
    def setUpClass(cls):
        # Create an instance of BashFunctionAnalyzer once for all tests
        cls.script_path = 'main.sh'  # Path to your shell script
        cls.analyzer = BashFunctionAnalyzer(cls.script_path)

    def test_999_coverage(self):
        coverage = self.analyzer.get_coverage()
        print(f"\nCode Coverage for {self.script_path}: {coverage:.2f}%")
        self.assertGreaterEqual(coverage, 0)  # Ensure we have some coverage        

    def test_1_say_hello(self):
        function_name = 'say_hello'
        print(f"\nTest function: {function_name}")
        
        self.analyzer.run_function(function_name)
        
        # Assert that 'echo' command runs once
        self.analyzer.assert_run_once('echo')  # Adjust this based on your actual commands
        self.analyzer.assertEqual(self.analyzer.status,0)
    
    def test_2_say_hello(self):
        function_name = 'say_hello'
        print(f"\nTest function: {function_name}")
        
        self.analyzer.run_function(function_name,["1"])
        
        self.analyzer.assert_call_number('echo',2)  
        self.analyzer.assertEqual(self.analyzer.status,0)

    def test_2_get_local_time(self):
        function_name = 'get_local_time'
        print(f"\nTest function: {function_name}")
        
        self.analyzer.run_function(function_name)
        self.analyzer.assertOutputMatchesRegex(r"^Current\ time:\ [0-9]{4}-[0-9]{2}-[0-9]{2}\ [0-9]{2}:[0-9]{2}:[0-9]{2}$")
        self.analyzer.assertEqual(self.analyzer.status,0)

    def test_3_get_remote_time(self):
        function_name = 'get_remote_time'
        print(f"\nTest function: {function_name}")
        
        self.analyzer.run_function(function_name)
        self.analyzer.assertEqual(self.analyzer.status,0)

    def test_4_get_remote_time_mocked(self):
        function_name = 'get_remote_time'
        print(f"\nTest function: {function_name} mocked")

        mock_params = {
                'curl': ["echo -e", "HTTP/1.1 200 OK\nDate: Wed, 30 Oct 2024 12:00:00 GMT\n"]
            }
        self.analyzer.run_function(function_name, mock_commands=mock_params)
        self.analyzer.assertEqual(self.analyzer.output, "Current time (remote): Wed, 30 Oct 2024 12:00:00 GMT")
        self.analyzer.assertEqual(self.analyzer.status,0)

    def test_5_make_api_request(self):
        function_name = 'make_api_request'
        print(f"\nTest function: {function_name}")

        mock_params = {
                'curl': ["echo -e", "{\"\"ResponseKey1\"\": 123, \"\"ResponseKey2\"\": 456}"]
            }
        self.analyzer.run_function(function_name, mock_commands=mock_params)
        self.analyzer.assertEqual(self.analyzer.output, "Response from server: {ResponseKey1: 123, ResponseKey2: 456}")
        self.analyzer.assertEqual(self.analyzer.status,0)

    def test_6_main(self):
        function_name = 'main'
        print(f"\nTest function: {function_name} mocked")

        mock_params = {
                'say_hello': ["echo -e", "OK"],
                'get_local_time': ["echo -e", "OK"],
                'get_remote_time': ["echo -e", "OK"],
                'make_api_request': ["echo -e", "OK"],
                'check_file_exist': ["echo -e", "OK"]
            }
        self.analyzer.run_function(function_name, mock_commands=mock_params)
        self.analyzer.assertEqual(self.analyzer.status,0)

if __name__ == '__main__':
    unittest.main()