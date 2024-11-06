#!/usr/bin/env bats

setup() {
    # Create a temporary folder for testing
    TEST_DIR=$(mktemp -d)
    # Create a test file to be used in the tests
    echo "This is a test file." > "$TEST_DIR/testfile.txt"
    
    # Mock the default curl command
    #curl() {
    #    case "$*" in
    #        *"http://fake-api.url.com"*)
    #           echo '{"ResponseKey1": 123, "ResponseKey2": 456}'
    #            ;;
    #        *)
    #            command curl "$@"
    #            ;;
    #    esac
    #}
}

teardown() {
    # Cleanup the temporary directory after tests
    rm -rf "$TEST_DIR"
}

# Mock the `test` command behavior for the `-f` flag
mock_test() {
    if [[ "$1" == "-f" && "$2" == "$TEST_DIR/testfile.txt" ]]; then
        return 0  # Mock that the file exists
    elif [[ "$1" == "-f" ]]; then
        return 1  # Mock that the file does not exist
    fi
    # Call the real test command for all other cases
    command test "$@"
}