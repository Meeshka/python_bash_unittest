import re
import subprocess

class BashFunctionAnalyzer:
    def __init__(self, script_path):
        self.script_path = script_path
        self.functions_info = self._extract_functions_info()
        self.function_output = {}
        self.last_run_function = ""
        self.executed_lines = set()  # To track executed lines
        self.total_lines = self.get_code_lines_count()
        self.output = ""
        self.status = 0

    def get_code_lines_count(self):
        return sum(info['lines_count'] for info in self.functions_info.values())
    
    def _extract_functions_info(self):
        functions_info = {}
        with open(self.script_path, 'r') as script_file:
            lines = script_file.readlines()
            in_function = False
            function_name = None
            function_lines = []

            for line in lines:
                match = re.match(r'^\s*function\s+(\w+)\s*\(\s*\)\s*{', line) or re.match(r'^\s*(\w+)\s*\(\s*\)\s*{', line)
                if match:
                    if in_function:
                        functions_info[function_name] = {
                            'params': self._extract_params(function_name, function_lines),
                            'lines_count': len(function_lines)
                        }
                    in_function = True
                    function_name = match.group(1)
                    function_lines = []

                # If we are inside a function capture code lines
                if in_function:
                    stripped_line = line.strip()
                    # Count the line only if it's not empty and not a comment
                    if stripped_line and not stripped_line.startswith('#') and stripped_line != '}' and not stripped_line.endswith(' \\'):
                        function_lines.append(line)

                if in_function and line.strip() == '}':
                    functions_info[function_name] = {
                        'params': self._extract_params(function_name, function_lines),
                        'lines_count': len(function_lines)
                    }
                    in_function = False

        return functions_info

    def _extract_params(self, function_name, function_lines):
        params_line = next((line for line in function_lines if '(' in line), None)
        if params_line:
            params = re.findall(r'\$(\w+)', params_line)
            return params
        return []

    def show_info(self, function_name=None):
        if function_name:
            info = self.functions_info.get(function_name)
            if info:
                print(f"Function: {function_name}")
                print(f"Parameters: {info['params']}")
                print(f"Lines of Code: {info['lines_count']}")
            else:
                print(f"No function named '{function_name}' found.")
        else:
            for name, info in self.functions_info.items():
                print(f"Function: {name}")
                print(f"Parameters: {info['params']}")
                print(f"Lines of Code: {info['lines_count']}\n")

    def run_function(self, function_name, mock_variables=None, function_args=None, mock_commands=None):
        if function_name not in self.functions_info:
            print(f"No function named '{function_name}' found.")
            return

        # Prepare the command
        command = 'bash -c "PS4=\'+ line \${LINENO}: \'; set -x;'

        # Source the script and call the function
        command += f'source {self.script_path}; '

        # Include mock commands in the same command
        if mock_commands:
            # Define each mock command as a function
            mock_statements = '; '.join([f'{cmd}() {{ {mock_cmd} \'{mock_data}\'; }}' for cmd, [mock_cmd, mock_data] in mock_commands.items()])
            command += f"{mock_statements}; "

        if mock_variables:
            mock_statements = '; '.join([f'export {var}={mock_var}' for var,mock_var in mock_variables.items()])
            command += f"{mock_statements}; "

        command += f' {function_name}'
        if function_args:
            args = ' '.join(arg for arg in function_args)
            command += ' '+args

        command += '"'

        #print(f"Debug: resulting command: {command}")
        try:
            result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
            combined_output = result.stdout.splitlines() + result.stderr.splitlines()
            self.function_output[function_name] = combined_output
            self.output = result.stdout.strip()  # Capture standard output
            self.status = result.returncode
            self.last_run_function = function_name

            # Track executed lines based on Bash trace output
            in_function = False
            current_func = ""
            for line in combined_output:
                if line.startswith("+ "):
                    executed_command = line[2:]  # Remove the leading "+ "
                    #print(f"Debug: executed command: {executed_command}")
                    if in_function:
                        self.executed_lines.add((current_func, executed_command))
                        if '[' in executed_command and ']' in executed_command:
                            self.executed_lines.add((current_func, executed_command + " end"))
                        #print(f"Debug: added line run {executed_command} for {current_func}")
                    else:
                        command_parts = executed_command.split()
                        #print(f"Debug: command parts: {command_parts}")
                        # Check if the executed command corresponds to any function line
                        for i, (func_name, info) in enumerate(self.functions_info.items(), start=1):
                            if func_name in command_parts:
                                if func_name == command_parts[2]:  # This implies the function ran
                                    current_func = func_name
                                    #print(f"Debug: Found function run: {current_func} in {executed_command}")
                                    in_function = True
                                    self.executed_lines.add((func_name, executed_command))
                                    #print(f"Debug: added line run {executed_command} for {current_func}")

        except subprocess.CalledProcessError as e:
            print(f"An error occurred while executing the function: {e}")
            self.function_output[function_name] = e.stderr.splitlines()
            self.output = e.stdout.strip()  # You might want to capture output even on error
            self.status = e.returncode
            

    def get_function_output(self, function_name):
        return self.function_output.get(function_name, [])

    def assert_run_once(self, command):
        # Count occurrences of the command in the output with a '+' prefix
        output = self.get_function_output(self.last_run_function)  # Assuming analysis on the first function run
        command_pattern = fr'^\+ line \d+: {command}'
        count = sum(1 for line in output if re.match(command_pattern, line))
        
        assert count == 1, f"Expected '{command}' to run exactly once, but found {count} times."
    
    def assert_call_number(self, command, number):
        # Count occurrences of the command in the output with a '+' prefix
        output = self.get_function_output(self.last_run_function)  # Assuming analysis on the first function run
        command_pattern = fr'^\+ line \d+: {command}'
        count = sum(1 for line in output if re.match(command_pattern, line))
        
        assert count == number, f"Expected '{command}' to run exactly {number} times, but found {count} times."

    def get_coverage(self, function_name=None):
        total_lines = 0
        covered_lines = 0
        if function_name:
            covered_lines = sum(1 for func, _ in self.executed_lines if func == function_name)
            info = self.functions_info.get(function_name)
            if info:
                total_lines = info["lines_count"]
            else:
                print(f"No function named '{function_name}' found.")
        else:
            total_lines = self.total_lines
            covered_lines = len(self.executed_lines)

        if total_lines == 0:
            return 0.0
        
        coverage = (covered_lines / total_lines) * 100
        return coverage
    
    def assertEqual(self, param1, param2):
        """Assert that param1 equals param2."""
        if param1 != param2:
            raise AssertionError(f"Assertion failed: {param1} is not equal to {param2}")
        
    def assertOutputMatchesRegex(self, regex_pattern):
        """Asserts that the output matches the given regex pattern."""
        if not re.match(regex_pattern, self.output):
            raise AssertionError(f"Output does not match pattern: {regex_pattern}. Output was: {self.output}")

    def assertOutputDoesNotMatchRegex(self, regex_pattern):
        """Asserts that the output does not match the given regex pattern."""
        if re.match(regex_pattern, self.output):
            raise AssertionError(f"Output matches pattern: {regex_pattern}. Output was: {self.output}")
