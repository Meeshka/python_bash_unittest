#!/usr/bin/env bats

source ./main.sh
source ./tests/test_setup.bash

#setup_file

# Test functions
@test "say_hello outputs 'Hello, World!'" {
  run say_hello
  [ "$status" -eq 0 ]
  [ "$output" == "Hello, World!" ]
}

@test "get_local_time outputs current time in expected format" {
  run get_local_time
  [ "$status" -eq 0 ]
  [[ "$output" =~ ^Current\ time:\ [0-9]{4}-[0-9]{2}-[0-9]{2}\ [0-9]{2}:[0-9]{2}:[0-9]{2}$ ]]
}

@test "get_remote_time outputs UTC time" {
  run get_remote_time
  echo "$output"
  [ "$status" -eq 0 ]
  [[ "$output" =~ ^Current\ time\ \(remote\)\:\ [a-zA-Z]{3},\ [0-9]{2}\ [a-zA-Z]{3}\ [0-9]{4}\ [0-9]{2}:[0-9]{2}:[0-9]{2}\ [a-zA-Z]{3}.+$ ]]
}

@test "get_remote_time outputs UTC time (mocked)" {
    # Redefine the curl function to return the expected output format
    curl() {         echo 'HTTP/1.1 200 OK
Date: Wed, 30 Oct 2024 12:00:00 GMT'
    }

    # Run the test
    run get_remote_time

    # Assertions
    [ "$status" -eq 0 ]
    [ "$output" == "Current time (remote): Wed, 30 Oct 2024 12:00:00 GMT" ]
}

@test "make_api_request returns response" {
  run make_api_request
  echo $output
  [ "$status" -eq 0 ]
  [ "$output" == "Response from server: Not for fake API" ]
}

@test "make_api_request returns JSON response (mocked)" {
  curl() {
          echo "{\"ResponseKey1\": 123, \"ResponseKey2\": 456}"
  }
  run make_api_request
  echo $output
  [ "$status" -eq 0 ]
  [ "$output" == "Response from server: {\"ResponseKey1\": 123, \"ResponseKey2\": 456}" ]
}

@test "file exists and reads content (real file)" {
    result="$(check_file_exist "$TEST_DIR" "testfile.txt")"
    [ "$result" == "This is a test file." ]
}

@test "file does not exist (real file)" {
    result="$(check_file_exist "$TEST_DIR" "nonexistentfile.txt")"
    [ "$result" == "File 'nonexistentfile.txt' does not exist in '$TEST_DIR'." ]
}

# Replacing the test command with the mock version
@test "file exists and reads content (mocked file)" {
    # Override the test command in the current shell
    run bash -c "
        test() { mock_test \"\$@\"; }
        source main.sh
        check_file_exist \"$TEST_DIR\" \"testfile.txt\"
    "
    [ "$status" -eq 0 ]
    [ "${lines[0]}" == "This is a test file." ]
}

@test "file does not exist (mocked_file)" {
    run bash -c "
        test() { mock_test \"\$@\"; }
        source main.sh
        check_file_exist \"$TEST_DIR\" \"nonexistentfile.txt\"
    "
    
    # Check the expected output when the file doesn't exist
    expected_message="File 'nonexistentfile.txt' does not exist in '$TEST_DIR'."
    [ "$status" -eq 0 ]
    [ "${lines[0]}" == "$expected_message" ]
}