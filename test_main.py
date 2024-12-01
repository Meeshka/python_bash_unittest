import re
import subprocess
from functools import wraps

def patch_bash(key, value=None, side_effect=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if side_effect:
                for value_set in side_effect:
                    kwargs[key] = value_set
                    func(*args, **kwargs)
            else:
                if value: kwargs[key] = value
                return func(*args, **kwargs)
        return wrapper
    return decorator

class BashFunctionAnalyzer:
    def __init__(self, script_path):
        self.script_path = script_path
        self.function_output = {}
        self.global_variables = {}
        self.func_variables = {}
        self.last_run_function = ""
        self.executed_lines = set()  # To track executed lines
        self.code_lines = set()
        self.output = ""
        self.status = 0
        self.functions_info = self._extract_functions_info()
        self.total_lines = self.get_code_lines_count()

    def get_code_lines_count(self):
        return sum(info['lines_count'] for info in self.functions_info.values())

    def _extract_functions_info(self):
        functions_info = {}
        with open(self.script_path, 'r') as script_file:
            lines = script_file.readlines()
            in_function = False
            function_name = None
            function_lines = []

            for i, line in enumerate(lines):
                # Match function definition with or without '{' on the same line
                match_func = re.match(r'^\s*function\s+(\w+)\s*\(\s*\)\s*', line) or \
                             re.match(r'^\s*(\w+)\s*\(\s*\)\s*', line)
                # Match global variable definitions
                match_var = re.match(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)', line)

                if match_func:
                    if in_function:
                        # Save previous function info before starting a new one
                        functions_info[function_name] = {
                            'params': self._extract_params(function_name, function_lines),
                            'lines_count': len(function_lines)
                        }

                    function_name = match_func.group(1)
                    in_function = True
                    function_lines = []

                    # Check if '{' is on the next line
                    if not line.strip().endswith('{') and (i + 1 < len(lines) and lines[i + 1].strip() == '{'):
                        continue  # Move to the next line to start capturing function content

                # Capture function content if inside a function
                if in_function:
                    cleaned_line = line.split('#', 1)[0].rstrip() # remove comments to escape garbage content
                    cleaned_line = cleaned_line.replace(';;','')
                    stripped_line = cleaned_line.strip()
                    if stripped_line and not stripped_line.startswith('#') and stripped_line != '}':
                        # Split the line by '&&' and process each command
                        commands = re.split(r' && | (?<!\|)\|(?!\|)', stripped_line)
                        content_line = ""
                        for command in commands:
                            if not self._is_control_structure(command):
                                content_line += command

                        if content_line:  # Ensure the command is not empty
                            function_lines.append(f"Line {i}: {content_line}\n")  # Keep newline for later use
                            self.code_lines.add((function_name, f"Line {i+1}: {content_line}\n"))

                # End function block if '}' is found
                if in_function and line.strip() == '}':
                    functions_info[function_name] = {
                        'params': self._extract_params(function_name, function_lines),
                        'lines_count': len(function_lines)
                    }
                    in_function = False

                # Capture global variables if not in a function
                if not in_function and match_var:
                    variable_name = match_var.group(1)
                    variable_value = match_var.group(2).strip()
                    # Remove quotes if present
                    variable_value = variable_value.strip('"').strip("'")
                    self.global_variables[variable_name] = variable_value

        return functions_info

    def _is_control_structure(self, line):
        # Strips leading text (like "line 365: ") before checking for control structures
        line = re.sub(r'^[^:]*:\s*', '', line)  # Remove any prefix of the form "line N: "
        #print(f"Debug: {line}")
        # Checks if the line is a control structure and should be excluded
        control_structures = [
            #r'^\s*if.*?$',  # If statement
            r'^\s*then.*?$',  # Then keyword
            r'^\s*else.*?$',  # Else keyword
            r'^\s*elif.*?$',  # Elif keyword
            r'^\s*fi.*?$',  # Fi keyword
            #r'^\s*while.*?$',  # For loop
            r'^\s*for.*?$',  # For loop
            r'^\s*do.*?$',  # Do keyword
            r'^\s*done.*?$',  # Done keyword
            r'^\s*case.*?$',  # Case statement
            r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\|\s*[a-zA-Z_][a-zA-Z0-9_]*\)\s*$', # case option alone in line
            r'^\"?[a-zA-Z0-9_*]*\"?\)$', # case option alone in line
            r'^\s*esac.*?$',  # Esac keyword
            r'^.*?\[\[\s.*\s?(?:<|>|<=|>=|<>|==|!=|-eq|-ne|-lt|-le|-gt|-ge)\s.*?\]\].*?$',  # Double brackets condition [[ ... ]]
            #r'^.*?\[\s.*\s?(?:<|>|<=|>=|<>|==|!=|-eq|-ne|-lt|-le|-gt|-ge)\s.*?\].*?$',  # Single brackets condition [ ... ]
            r'^.*?\(\(\s.*\s?(?:<|>|<=|>=|<>|==|!=|-eq|-ne|-lt|-le|-gt|-ge)\s.*?\)\).*?$',  # Double brackets condition (( ... ))
            r'^.*?\(\s.*\s?(?:<|>|<=|>=|<>|==|!=|-eq|-ne|-lt|-le|-gt|-ge)\s.*?\).*?$'  # Single brackets condition ( ... )
        ]
        is_control = any(re.match(pattern, line) for pattern in control_structures)
        #print(f"Debug: Control? - {is_control}")
        return is_control

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

    def _process_output_lines(self, combined_output, lines_set, function_name):
        processed_output = combined_output
        in_function = False
        for line in combined_output:
            #print(f"Debug: Line: {line}")
            if not line.startswith("+ "):
                continue

            #print(f"Debug: Line to analyze: {line}")
            # validate for function name OR variable echo
            pattern = r"^\+ line [012]:"
            match_1 = re.match(pattern, line)
            if match_1:
                #print(f"Debug: Line from external command: {line}")
                # Validate for variable value
                var_pattern = r"^\+ line [12]: echo var_(.+)=(.+)$"
                var_match = re.match(var_pattern, line)
                if var_match:
                    processed_output.append(f"+ line 0: variable {var_match.group(1)}={var_match.group(2)}")

                # Validate for function name
                func_pattern = r'^\+ line [12]: ' + function_name + '\\s?(.+)?$'
                func_match = re.match(func_pattern, line)
                if func_match:
                    in_function = True
                    lines_set.add((function_name,f"line 1: {function_name}"))
            else:
                #print(f"Debug: Regular code line: {line}")
                executed_command = line[2:]  # Remove the leading "+ "
                command_parts = executed_command.split()
                #print(f"Debug: {command_parts}")

                if in_function:
                    #print(f"Debug: in control structure {self._is_control_structure(executed_command)}")
                    if not self._is_control_structure(executed_command):
                        lines_set.add((function_name, f"{command_parts[0]} {command_parts[1]}"))
                        #print(f"Debug: added executed command: {executed_command}")
        return processed_output

    def run_function(self, function_name, mock_variables=None, function_args=None, mock_commands=None, mock_read_values=None, show_variables=None):
        if function_name not in self.functions_info:
            print(f"No function named '{function_name}' found.")
            return

        # Prepare the command
        command = 'bash -c "PS4=\'+ line \\${LINENO}: \'; set -x; '

        # Source the script and call the function
        command += f'source {self.script_path}; '

        # Include mock commands in the same command
        if mock_commands:
            # Define each mock command as a function
            mock_statements = '; '.join(
                [f'{cmd}() {{ {mock_cmd} {'' if mock_data=='' else f"\'{mock_data}\';"} }}' for cmd, [mock_cmd, mock_data] in mock_commands.items()])
            command += f"{mock_statements}; "

        if mock_variables:
            mock_statements = '; '.join([f'export {var}={mock_var}' for var, mock_var in mock_variables.items()])
            command += f"{mock_statements}; "

        command += f' {function_name}'
        if function_args:
            args = ' '.join(arg for arg in function_args)
            command += ' ' + args

        if mock_read_values:
            command += ' <<EOF\n'
            for read_value in mock_read_values:
                command += f'{read_value}\n'
            command += 'EOF'

        command += "; "

        if show_variables:
            for variable in show_variables:
                command += f'echo var_{variable}=\\${variable}; '
        command += '"'

        print(f"Debug: resulting command: {command}")
        try:
            result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
            combined_output = result.stdout.splitlines() + result.stderr.splitlines()
            self.function_output[function_name] = combined_output
            self.output = combined_output  # Capture standard output
            self.status = result.returncode
            self.last_run_function = function_name

            # Track executed lines based on Bash trace output
            processed_output = self._process_output_lines(combined_output, self.executed_lines, function_name=function_name)

        except subprocess.CalledProcessError as e:
            print(f"An error occurred while executing the function: {e}")
            self.function_output[function_name] = e.stderr.splitlines()
            self.output = e.stdout.strip()  # You might want to capture output even on error
            self.status = e.returncode

    def get_function_output(self, function_name):
        return self.function_output.get(function_name, [])

    def assert_run_once(self, command):
        # Count occurrences of the command in the output with a '+' prefix
        output = self.get_function_output(self.last_run_function)  # Assuming analysis on the last function run
        command_pattern = fr'^\+ line \d+: {re.escape(command)}'
        count = sum(1 for line in output if re.match(command_pattern, line))

        assert count == 1, f"Expected '{command}' to run exactly once, but found {count} times."

    def assert_run(self, command):
        # Count occurrences of the command in the output with a '+' prefix
        output = self.get_function_output(self.last_run_function)  # Assuming analysis on the first function run
        command_pattern = fr'^\+ line \d+: {re.escape(command)}'
        count = sum(1 for line in output if re.match(command_pattern, line))

        assert count >= 1, f"Expected '{command}' to run at least once, but not found."

    def assert_call_number(self, command, number):
        # Count occurrences of the command in the output with a '+' prefix
        output = self.get_function_output(self.last_run_function)  # Assuming analysis on the first function run
        command_pattern = fr'^\+ line \d+: {re.escape(command)}'
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
        if param1 != param2:
            raise AssertionError(f"Assertion failed: {param1} is not equal to {param2}")

    def assertOutputMatchesRegex(self, regex_pattern):
        for output_line in self.output:
            #print(f"Debug: {output_line}")
            if re.match(regex_pattern, output_line):
                return 0
        raise AssertionError(f"No line in output matches pattern: {regex_pattern}.")

    def assertOutputDoesNotMatchRegex(self, regex_pattern):
        if re.match(regex_pattern, self.output):
            raise AssertionError(f"Output matches pattern: {regex_pattern}. Output was: {self.output}")

    def assertStatusOK(self):
        if self.status != 0:
            raise AssertionError(f"Assertion failed: status is {self.status}")

    def assertStatusNOK(self):
        if self.status == 0:
            raise AssertionError(f"Assertion failed: status is OK, expected NOK")

    def _get_local_variable(self, var_name):
        output = self.get_function_output(self.last_run_function)
        var_reg = r'^\+ line 0: variable (.+)=(.+)$'
        for line in output:
            #print(f"Debug: line check {line}")
            var_match = re.match(var_reg, line)
            if var_match:
                #print(f"Debug: match found {var_match}")
                return var_match.group(2)
        return None

    def get_variable_value(self, var_name):
        variable_value = self.global_variables.get(var_name)
        if variable_value:
            return variable_value
        else:
            #print(f"Debug: local variable check {var_name}")
            variable_value = self._get_local_variable(var_name)
            if variable_value:
                return variable_value

        print(f"No variable '{var_name}' found")

    def _get_executed_lines(self, function_name):
        return [line for func, line in self.executed_lines if func == function_name]

    def show_executed_lines(self, function_name=None):
        if function_name:
            print(f"Executed lines for function '{function_name}':")
            # Filter the executed lines by the specified function name
            found_lines = self._get_executed_lines(function_name)
            if found_lines:
                for executed_line in found_lines:
                    print(f" - {executed_line}")
            else:
                print(f"No executed lines found for function '{function_name}'.")
        else:
            print("Executed lines for all functions:")
            for func, executed_line in self.executed_lines:
                print(f"Function '{func}': {executed_line}")

    def show_code_lines(self, function_name=None):
        if function_name:
            print(f"Code lines for function '{function_name}':")
            # Filter the executed lines by the specified function name
            found_lines = [line for func, line in self.code_lines if func == function_name]
            if found_lines:
                for code_line in found_lines:
                    print(f" - {code_line}")
            else:
                print(f"No code lines found for function '{function_name}'.")
        else:
            print("Code lines for all functions:")
            for func, code_line in self.code_lines:
                print(f"Function '{func}': {code_line}")

