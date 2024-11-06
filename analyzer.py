from unittestbash import BashFunctionAnalyzer


if __name__ == "__main__":
    function_name = "make_api_request"
    analyzer = BashFunctionAnalyzer('main.sh')
    print(f"Total lines: {analyzer.total_lines}")
    print(f"Functions info: {analyzer.functions_info}")
    analyzer.run_function(function_name,function_args=["1"])
    print(f"Function output: {analyzer.output}")
    print(f"Function {function_name} combined output: {analyzer.function_output[function_name]}")
    print(f"Executed lines: {analyzer.executed_lines}")
    print(f"Coverage: {analyzer.get_coverage(function_name)}")