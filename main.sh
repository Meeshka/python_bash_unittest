#!/bin/bash

say_hello() {
    echo "Hello, World!"
}


get_local_time() {

    current_time=$(date +"%Y-%m-%d %H:%M:%S")
    echo "Current time: $current_time"

}

get_remote_time() {
    response=$(curl -I 'https://google.com/' 2>/dev/null | grep -i '^date:' | sed 's/^[Dd]ate: //g')

    # Print the current date and time
    echo "Current time (remote): $response"
}

make_api_request() {
    URL="http://fake-api.url.com"
    AUTH_TOKEN="Bearer ey12345zx"

    # Capture the response in a variable
    response=$(curl -s -X GET "$URL" \
     -H "Authorization: $AUTH_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{ "FakeKey1": "Value1", "FakeKey2": "Value2" }')

    # Echo the response
    if [ -z "$response" ]; then
        echo "Response from server: Not for fake API"
    else
        echo "Response from server: $response"
    fi
}

main() {
    say_hello
    get_local_time
    get_remote_time
    make_api_request
}


if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main
fi