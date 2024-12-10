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

prompt_backup_confirmation() {
    read -p "Do you want to create a backup for this device? (yes/no): " confirm
    if [[ "$confirm" == "no" ]]; then
        echo "Backup operation canceled by user."
        exit 0
    elif [[ "$confirm" == "yes" ]]; then
        echo "Backup operation started by user."
        exit 0
    else
        echo "Unknown choice."
        exit 1
    fi
}

check_mysql_service() {
    local result=0
    status=$(sudo monit status mysqld | grep "status" | grep "OK")
    if [ -n "$status" ]; then
      echo "MySQL service is running."
    else
      result=1
      echo "MySQL service is not running. Attempting to start MySQL..."
      sudo monit start mysqld > /dev/null 2>&1
      sleep 5

        status=$(sudo monit status mysqld | grep "status" | grep "OK")
        if [ -n "$status" ]; then
          echo "MySQL service started successfully."
          result=0
        fi
    fi

    exit $result
}

stop_service() {
    service_name=$1
    result=1
    retry_count=10

    status=$(sudo monit status "$service_name" | grep "Not monitored")

    if [ -n "$status" ]; then
        result=0
    else
      while true; do
        ((retry_count-=1))

        if [ $retry_count -le 0 ]; then
          break
        fi

        sudo monit stop "$service_name" > /dev/null 2>&1
        sleep 5

        status=$(sudo monit status "$service_name" | grep "Not monitored")
        if [ -n "$status" ];then
            result=0
            break
        fi
      done
    fi
    exit $result
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