import unittest
from unittestbash import BashFunctionAnalyzer, patch_bash

class TestMain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script_path = './main.sh'
        cls.analyzer = BashFunctionAnalyzer(cls.script_path)
        cls.tested_functions = set()
        cls.minimum_coverage = 0
        #print("Script info:\n")
        print(f"Total lines: {cls.analyzer.total_lines}")

    def get_color_coverage(self, coverage):
        green = "\033[32m"  # Green text for 100%
        yellow = "\033[33m"  # Yellow text for 90-99.99%
        red = "\033[31m"  # Red text for below 90%
        if coverage == 100:
            color = green
        elif coverage >= self.minimum_coverage:
            color = yellow
        else:
            color = red
        return color

    def test_zzz_coverage(self):
        for func in self.analyzer.functions_info:
            if func not in self.tested_functions:
                print(f"Function {func} not marked as tested")
                #self.fail(f"Function {func} not marked as tested")
        for func in self.tested_functions:
            coverage = self.analyzer.get_coverage(func)
            if coverage < self.minimum_coverage or coverage > 100:
                print(f"Code Coverage for function {func}:{self.get_color_coverage(coverage)}{coverage:.2f}%\033[0m")
            print(f"Code Coverage for function {func}:{self.get_color_coverage(coverage)}{coverage:.2f}%\033[0m")
            self.assertGreaterEqual(coverage, self.minimum_coverage)  # Ensure we have some coverage
            self.assertLessEqual(coverage,100) # Ensure no extra code added to run

        coverage = self.analyzer.get_coverage()
        if coverage < self.minimum_coverage or coverage > 100:
            print(f"Code Coverage for {self.script_path}:{self.get_color_coverage(coverage)}{coverage:.2f}%\033[0m")
        print(f"Code Coverage for {self.script_path}:{self.get_color_coverage(coverage)}{coverage:.2f}%\033[0m")
        self.assertGreaterEqual(coverage, self.minimum_coverage)  # Ensure we have some coverage
        self.assertLessEqual(coverage, 100)  # Ensure no extra code added to run

    def test_say_hello(self, function_name='say_hello'):
        print(f"Test function: {function_name}")

        self.analyzer.run_function(function_name=function_name)

        # validations
        self.analyzer.assert_run_once("echo")
        self.tested_functions.add(function_name)

    def test_get_remote_time_real(self,
                                  function_name='get_remote_time'):
        print(f"Test function: {function_name}")

        self.analyzer.run_function(function_name=function_name)
        #print(self.analyzer.get_function_output(function_name))
        # validations
        self.analyzer.assert_run_once("curl")
        self.analyzer.assertOutputMatchesRegex(r'^Current time \(remote\): (Mon|Tue|Wed|Thu|Fri|Sat|Sun),'
                                               r' \d{2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4} \d{2}:\d{2}:\d{2} GMT$')
        self.analyzer.assert_run_once("echo")
        self.tested_functions.add(function_name)

    #replacing the curl response with fake echo by adding
    # curl() { echo -e "HTTP/1.1 200 OK \nDate: Wed, 28 Jun 2023 12:34:56 GMT \nContent-Type: text/html; charset=UTF-8\n\n"; }
    @patch_bash('mock_commands',{
        'curl': ['echo -e \\"HTTP/1.1 200 OK\\nDate: Wed, 28 Jun 2023 12:34:56 GMT\\nContent-Type: text/html; charset=UTF-8\\n\\n\\";', '']
    })
    def test_get_remote_time_mock(self,
                                  mock_commands,
                                  function_name='get_remote_time'):
        print(f"Test function: {function_name}")

        self.analyzer.run_function(function_name=function_name,
                                   mock_commands=mock_commands)
        #print(self.analyzer.get_function_output(function_name))
        # validations
        self.analyzer.assert_run_once("curl")
        self.analyzer.assertOutputMatchesRegex(r'^Current time \(remote\): Wed, 28 Jun 2023 12:34:56 GMT$')
        self.analyzer.assert_run_once("echo")
        self.tested_functions.add(function_name)

    @patch_bash('mock_read_values', ["yes"])
    @patch_bash('mock_commands',{
        'exit' : ['echo','exit']
    })
    def test_prompt_backup_confirmation_yes(self,
                                            mock_commands,
                                            mock_read_values,
                                            function_name='prompt_backup_confirmation'):
        print(f"Test function: {function_name} with yes input")

        self.analyzer.run_function(function_name,
                                   mock_commands=mock_commands,
                                   mock_read_values=mock_read_values,
                                   )
        self.analyzer.assert_run_once("read")
        self.analyzer.assert_call_number('echo',2)
        self.analyzer.assert_run_once('exit 0')
        self.analyzer.assertOutputMatchesRegex(r'^.+Backup operation started by user\..+$')
        self.tested_functions.add(function_name)
        #self.analyzer.show_code_lines(function_name)
        #self.analyzer.show_executed_lines(function_name)
        self.analyzer.assertStatusOK()

    @patch_bash('mock_read_values', ["no"])
    @patch_bash('mock_commands',{
        'exit' : ['echo','exit']
    })
    def test_prompt_backup_confirmation_no(self,
                                            mock_commands,
                                            mock_read_values,
                                            function_name='prompt_backup_confirmation'):
        print(f"Test function: {function_name} with no input")

        self.analyzer.run_function(function_name,
                                   mock_commands=mock_commands,
                                   mock_read_values=mock_read_values,
                                   )
        self.analyzer.assert_run_once("read")
        self.analyzer.assert_call_number('echo',2)
        self.analyzer.assert_run_once('exit 0')
        self.analyzer.assertOutputMatchesRegex(r'^.+Backup operation canceled by user\..+$')
        self.tested_functions.add(function_name)
        #self.analyzer.show_code_lines(function_name)
        #self.analyzer.show_executed_lines(function_name)
        self.analyzer.assertStatusOK()

    @patch_bash('mock_read_values', ["ok"])
    @patch_bash('mock_commands', {
        'exit': ['echo', 'exit']
    })
    def test_prompt_backup_confirmation_incorrect(self,
                                           mock_commands,
                                           mock_read_values,
                                           function_name='prompt_backup_confirmation'):
        print(f"Test function: {function_name} with incorrect input")

        self.analyzer.run_function(function_name,
                                   mock_commands=mock_commands,
                                   mock_read_values=mock_read_values,
                                   )
        self.analyzer.assert_run_once("read")
        self.analyzer.assert_call_number('echo', 2)
        self.analyzer.assert_run_once('exit 1')
        self.analyzer.assertOutputMatchesRegex(r'^.+Unknown choice\..+$')
        self.tested_functions.add(function_name)
        # self.analyzer.show_code_lines(function_name)
        # self.analyzer.show_executed_lines(function_name)
        self.analyzer.assertStatusOK()

    @patch_bash('mock_commands', {
        'sudo': ['echo', 'sudo'],
        'sleep': ['echo', 'sleep'],
        'grep': ['if [ \\$result -eq 0 ]; then echo \'status OK\'; fi', '']
    })
    def test_check_mysql_service_ok(self,
                                    mock_commands,
                                    function_name="check_mysql_service"):
        print(f"Test function: {function_name} OK")

        self.analyzer.run_function(function_name,
                                   mock_commands=mock_commands
                                   )
        #self.analyzer.show_code_lines(function_name)
        #self.analyzer.show_executed_lines(function_name)
        self.analyzer.assert_call_number('echo', 4)  # Include the mocked echo for sudo and sleep
        self.tested_functions.add(function_name)
        self.analyzer.assertStatusOK()

    @patch_bash('mock_commands', {
        'sudo': ['echo', 'sudo'],
        'sleep': ['echo', 'sleep'],
        'grep': ['if [ \\$result -eq 0 ]; then echo \'\'; else echo \'status OK\'; fi', ''],
        'exit': ['return', 0]
    })
    def test_check_mysql_service_nok_ok(self,
                                        mock_commands,
                                        function_name="check_mysql_service"):
        print(f"Test function: {function_name} NOK -> OK")

        self.analyzer.run_function(function_name,
                                   mock_commands=mock_commands
                                   )
        #self.analyzer.show_code_lines(function_name)
        #self.analyzer.show_executed_lines(function_name)
        self.analyzer.assert_call_number('echo', 9)  # Include the mocked echo for sudo and
        self.analyzer.assert_run_once('exit 0')
        self.tested_functions.add(function_name)
        self.analyzer.assertStatusOK()

    @patch_bash('mock_commands', {
        'sudo': ['echo', 'sudo'],
        'sleep': ['echo', 'sleep'],
        'grep': ['echo', '\'\''],
        'exit': ['return', 0]
    })
    @patch_bash('show_variables', [
        "result"
    ])
    def test_check_mysql_service_nok_nok(self,
                                         show_variables,
                                         mock_commands,
                                         function_name="check_mysql_service"):
        print(f"Test function: {function_name} NOK -> NOK")

        self.analyzer.run_function(function_name,
                                   mock_commands=mock_commands,
                                   show_variables=show_variables
                                   )
        #print(self.analyzer.get_function_output(function_name))
        #self.analyzer.show_code_lines(function_name)
        #self.analyzer.show_executed_lines(function_name)
        self.analyzer.assertEqual(self.analyzer.get_variable_value("result"),'1')
        self.analyzer.assert_run_once('sleep 5')
        self.analyzer.assert_run_once('exit 1')
        self.tested_functions.add(function_name)
        self.analyzer.assertStatusOK()

    @patch_bash('show_variable', [
        'retry_count',
        'sudo_counter'
    ])
    @patch_bash('mock_variables', {
        'sudo_counter': 1 #should start from 1, because the first call though increment, starts on next iteration
    })
    @patch_bash('mock_commands', {
        'sudo': ['sudo_counter=\\$((sudo_counter + 1));', ''],
        'sleep': ['echo', 'sleep'],
        'grep': ['if [ \\$sudo_counter -eq 1 ]; '
                 'then echo \'Not monitored\'; '
                 'fi', ''],  # for not running service first call will return 'Not monitored'
        'exit': ['return', 0]
    })
    def test_stop_service_not_running(self,
                                      mock_commands,
                                      mock_variables,
                                      show_variable,
                                      function_name='stop_service'):
        print(f"Test function: {function_name} not running")

        self.analyzer.run_function(function_name,
                                    mock_variables=mock_variables,
                                    mock_commands=mock_commands,
                                    function_args = ['mysql'],
                                    show_variables=show_variable
                                   )
        #self.analyzer.assert_call_number('echo', 1)  # Adjust this based on your actual commands
        #self.analyzer.show_code_lines(function_name)
        #self.analyzer.show_executed_lines(function_name)
        self.tested_functions.add(function_name)
        self.analyzer.assert_run_once("status='Not monitored'")
        self.analyzer.assertEqual(self.analyzer.get_variable_value('retry_count'),"10") #decrement not occurred
        self.analyzer.assertEqual(self.analyzer.get_variable_value('sudo_counter'),"1") #
        self.analyzer.assertEqual(self.analyzer.get_variable_value('result'),"0")
        self.analyzer.assert_run_once("exit 0")
        self.analyzer.assertStatusOK()


    @patch_bash('show_variable', [
        'retry_count',
        'sudo_counter'
    ])
    @patch_bash('mock_variables', {
        'sudo_counter': 1 #should start from 1, because the first call though increment, starts on next iteration
    })
    @patch_bash('mock_commands', {
        'sudo': ['sudo_counter=\\$((sudo_counter + 1));', ''],
        'sleep': ['echo', 'sleep'],
        'grep': ['if [ \\$sudo_counter -le 1 ]; '
                 '  then echo \'\'; '
                 'elif [ \\$sudo_counter -gt 1 ]; '
                 '  then  echo \'Not monitored\'; '
                 'else '
                 '  echo \'Not monitored\'; '
                 'fi', ''],
        'exit': ['return', 0]
    })
    def test_stop_service_running_stopped(self,
                                          mock_commands,
                                          mock_variables,
                                          show_variable,
                                          function_name='stop_service'):
        print(f"Test function: {function_name} running and stopped")

        self.analyzer.run_function(function_name,
                                   function_args=['mysql'],
                                   mock_variables=mock_variables,
                                   mock_commands=mock_commands,
                                   show_variables=show_variable
                                   )
        # self.analyzer.assert_call_number('echo', 1)  # Adjust this based on your actual commands
        #self.analyzer.show_code_lines(function_name)
        #self.analyzer.show_executed_lines(function_name)
        self.tested_functions.add(function_name)
        self.analyzer.assert_run_once("status='Not monitored'")
        self.analyzer.assertEqual(self.analyzer.get_variable_value('result'),"0")
        self.analyzer.assertEqual(self.analyzer.get_variable_value('retry_count'),"9") #one decrement occurred
        self.analyzer.assert_run_once("(( retry_count-=1 ))") #we succeed after 1 retry
        self.analyzer.assert_run_once("break") #we exit while
        self.analyzer.assert_run_once("exit 0")
        self.analyzer.assertStatusOK()

    @patch_bash('show_variable', [
        'retry_count',
        'sudo_counter'
    ])
    @patch_bash('mock_variables', {
        'sudo_counter': 1 #should start from 1, because the first call though increment, starts on next iteration
    })
    @patch_bash('mock_commands', {
        'sudo': ['sudo_counter=\\$((sudo_counter + 1));', ''],
        'sleep': ['echo', 'sleep'],
        'grep': ['if [ \\$sudo_counter -gt 20 ]; '
                 '  then echo \'Not monitored\'; ' #we protect from endless loop in case retry engine fails to stop
                 'else '
                 '  echo \'\'; '
                 'fi', ''],
        'exit': ['return', 0]
    })
    def test_stop_service_running_exit_retry(self,
                                             mock_commands,
                                             mock_variables,
                                             show_variable,
                                             function_name='stop_service'):
        print(f"Test function: {function_name} running and failed to stop")

        self.analyzer.run_function(function_name,
                                   function_args=['mysql'],
                                   mock_variables=mock_variables,
                                   mock_commands=mock_commands,
                                   show_variables=show_variable
                                   )
        # self.analyzer.assert_call_number('echo', 1)  # Adjust this based on your actual commands
        #self.analyzer.show_code_lines(function_name)
        #self.analyzer.show_executed_lines(function_name)
        self.tested_functions.add(function_name)
        self.analyzer.assertEqual(self.analyzer.get_variable_value('retry_count'),"0") #retry counter dropped to 0
        self.analyzer.assertEqual(self.analyzer.get_variable_value('sudo_counter'),"10") #while retry we tried to run service 10 times
        self.analyzer.assert_call_number("(( retry_count-=1 ))", 10) #we exit while by retry
        self.analyzer.assert_run_once("break") #we exit while
        self.analyzer.assert_run_once("exit 1")
        self.analyzer.assertStatusOK()

    @patch_bash('function_args',side_effect=[
                                        ["\'test message\'",'info'],
                                        ["\'test message\'",'warning'],
                                        ["\'test message\'",'error']])
    @patch_bash('mock_variables',{'LOG_FILE': '.\\test_log.log'})
    def test_log_message(self,
                              mock_variables,
                              function_args,
                              function_name='log_message'):
        print(f"Test function: {function_name} {function_args[1].upper()}")

        self.analyzer.run_function(function_name,
                               mock_variables=mock_variables,
                               function_args=function_args
                               )
        self.analyzer.assert_call_number('echo', 2)  # Adjust this based on your actual commands
        self.analyzer.assertOutputMatchesRegex(r'^.+\[' + function_args[1].upper() + '\] test message.+$')

        self.tested_functions.add(function_name)
        #self.analyzer.show_code_lines(function_name)
        #self.analyzer.show_executed_lines(function_name)
        self.analyzer.assertStatusOK()

    @patch_bash('mock_commands',{
        'say_hello': ['echo', 'say_hello'],
        'get_local_time': ['echo', 'get_local_time'],
        'check_mysql_service': ['echo', 'check_mysql_service'],
        'get_remote_time': ['echo', 'get_remote_time'],
        'prompt_backup_confirmation': ['echo', 'prompt_backup_confirmation'],
        'stop_service': ['echo', 'stop_service'],
        'log_message': ['echo', 'log_message']
    })
    def test_main(self,
                  mock_commands,
                  function_name="main"):
        print(f"Test function: {function_name}")
        mock_functions_base = {
        }

        menu_options = {
            "h": ["say_hello"],
            "t": ['get_local_time'],
            "o": ["get_remote_time"],
            "b": ["prompt_backup_confirmation"],
            "c": ["check_mysql_service"],
            "s": ["stop_service"],
            "l": ["log_message"],
            "n": [],
            "q": []
        }

        for key in menu_options:
            # mock_commands reset (less commands)
            mock_commands_iter = mock_commands.copy()
            #mock_variables["techcommand"] = key
            for mock_command in menu_options[key]:
                mock_commands_iter[mock_command] = ['echo', mock_command]

            mock_read_values = [
                key,
                "q"
            ]
            self.analyzer.run_function(function_name,
                                       mock_commands=mock_commands,
                                       mock_read_values=mock_read_values)
            #print(self.analyzer.get_function_output(function_name))

            for mock_command in menu_options[key]:
                self.analyzer.assert_run_once(f"echo {mock_command}")

        #self.analyzer.show_executed_lines(function_name)
        #self.analyzer.show_code_lines(function_name)
        self.tested_functions.add(function_name)
        self.analyzer.assertStatusOK()

if __name__ == '__main__':
    unittest.main()