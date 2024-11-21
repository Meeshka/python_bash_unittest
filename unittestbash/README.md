The python class that can run external bash scripts as standard unittest module.
Class is set to work only with function structured scripts. If you have spaghetti code, 
put it at least to the main().
One day my boss came and said THat we have a huge project written in bash and that new standards 
demand the unit testing automation and acceptance testing. I was shocked but had to find a way to make
the tests. To my disappointment, I couldn't find any existing solution that knows how to run the 
tests as close to python library, as possible. Bats, shunit2, bcov, kcov. Either complicated to use, 
or not really testing the code lines.
I tried to implement something easy to support and use. Though of course I am sure it looks pretty ugly and 
that it can be modified to a higher level of coding. 

**Important**: for the class to work correctly, the main function should be started with condition
Example:

```
#!/bin/bash
function say_hello(){
    echo "Hello, world"
}

main(){
    say_hello
}

if [[ "${BASH_SOURCE[0]}" == "${0}" || "${0}" == "/bin/bash" ]]; then
  main
fi
```

Create test class to use.

Example:
```
import unittest
from unittestbash import BashFunctionAnalyzer

class TestMain(unittest.TestCase):
    analyzer = None  # Class variable to store the analyzer instance

    @classmethod
    def setUpClass(cls):
        # Create an instance of BashFunctionAnalyzer once for all tests
        cls.script_path = '<path to bash script>'  # Path to your shell script
        cls.analyzer = BashFunctionAnalyzer(cls.script_path)
        cls.mock_variables = {} # dict with structure "variable": "mock_value"
        cls.moc_functions = {} # dict with structure "function_name": ["mock expression", "mock_data"]
        cls.tested_functions = set()
        cls.minimum_coverage = 0
        #print(f"Total lines: {cls.analyzer.total_lines}")
```

Basic features of analyzer object:
- **get_code_lines_count**: return the total number of lines with real code. No comments/empty rows or other garbage counted
- **show_info**: optional parameter - function name. Returns lines count for each function.
- **run_function**: main run function. accepts mock functions list, mock variables list, function arguments, read values (to mock 'read' commands)
- **get_function_output**: show the debug output for the latest executed function
- **get_coverage**: optional function name. shows the current coverage through all run tests
- **show_executed_lines**: optional function name. shows lines of code that were run
- **show_code_lines**:  optional function name. shows stored code lines for functions
- **assert_run_once, assert_run, assert_call_number, assertEqual,
assertOutputMatchesRegex, assertOutputDoesNotMatchRegex, assertStatusOK, assertStatusNOK**: 
different validation functions for testing the results.

Various examples of usage:
**Code coverage validation**: I name it always with zzz to make sure it runs after all other tests
```
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
        for func in self.tested_functions:
            coverage = self.analyzer.get_coverage(func)
            if coverage < self.minimum_coverage or coverage > 100:
                print(f"Code Coverage for function {func}:{self.get_color_coverage(coverage)}{coverage:.2f}%\033[0m")
            self.assertGreaterEqual(coverage, self.minimum_coverage)  # Ensure we have some coverage
            self.assertLessEqual(coverage,100) # Ensure no extra code added to run

        coverage = self.analyzer.get_coverage()
        if coverage < self.minimum_coverage or coverage > 100:
            print(f"Code Coverage for {self.script_path}:{self.get_color_coverage(coverage)}{coverage:.2f}%\033[0m")
        self.assertGreaterEqual(coverage, self.minimum_coverage)  # Ensure we have some coverage
        self.assertLessEqual(coverage, 100)  # Ensure no extra code added to run
```

**Trivial run test**:
```
script_run_func() {
    clear
    echo 'Let's run this'
    return_to_main_menu_func
}

def test_script_run_func(self, function_name='script_run_func'):
        print(f"Test function: {function_name}")

        mock_variables = self.mock_variables.copy()
        mock_variables['EXTERNAL_SCRIPT_VARIABLE'] = "test_echo.sh\\ EXTERNAL_SCRIPT_VARIABLE"
        mock_functions = {
            'return_to_main_menu_func': ['echo', 'main menu run OK']
        }

        self.analyzer.run_function(function_name, mock_variables=mock_variables, mock_commands=mock_functions)

        self.analyzer.assert_run_once("clear")
        self.analyzer.assert_run_once("/bin/bash test_echo.sh EXTERNAL_SCRIPT_VARIABLE")
        self.analyzer.assert_run_once("return_to_main_menu_func")
        self.tested_functions.add(function_name)
        self.analyzer.assertStatusOK()
```