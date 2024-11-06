#!/bin/bash

function say_hello() {
    local testp="${1:-0}"
    echo "Hello, World!"
    if [ "$testp" -eq 1 ]; then
        new_param="Just to see how it works"
        echo "$new_param"  # Optional: Echo the new_param for demonstration
    fi
}


function get_local_time() {
    current_time=$(date +"%Y-%m-%d %H:%M:%S")
    echo "Current time: $current_time"
}

function get_remote_time() {
    response=$(curl -I 'https://google.com/' 2>/dev/null | grep -i '^date:' | sed 's/^[Dd]ate: //g')
    echo "Current time (remote): $response"
}

function make_api_request() {
    URL="http://fake-api.url.com"
    AUTH_TOKEN="Bearer ey12345zx"

    response=$(curl -s -X GET "$URL" \
     -H "Authorization: $AUTH_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{ "FakeKey1": "Value1", "FakeKey2": "Value2" }')

    if [ -z "$response" ]; then
        echo "Response from server: Not for fake API"
    else
        echo "Response from server: $response"
    fi
}

function check_file_exist() {
    local folder="$1"        # First argument is the folder path
    local filename="$2"      # Second argument is the filename

    # Construct the full file path
    local filepath="$folder/$filename"

    # Check if the file exists
    if [[ -f "$filepath" ]]; then
        # If it exists, read and return the content
        cat "$filepath"
    else
        # If it doesn't exist, print a message
        echo "File '$filename' does not exist in '$folder'."
    fi
}

function main() {
    say_hello
    get_local_time
    get_remote_time
    make_api_request
    check_file_exist "/path/to/folder" "filename.txt"
}


if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main
fi