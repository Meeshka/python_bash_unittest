#!/bin/bash

LOG_FILE=/home/tech/technician.log

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

log_message() {
    local message="$1"
    local type="$2"
    local color="$NC"

    case "$type" in
        "info")
            color="$LIGHT_GREEN"
            ;;
        "warning")
            color="$YELLOW"
            ;;
        "error")
            color="$RED"
            ;;
    esac

    # Log to the console with color
    echo -e "${color}[${type^^}] $message${NC}"

    # Log to the log file without color
    echo "$(date +%D_%T) : [${type^^}] $message" >> $LOG_FILE
}

main() {
  printf "## 'h': say hello world                       ##\n"
  printf "## 't': show local time                       ##\n"
  printf "## 'o': show online time                      ##\n"
  printf "## 'b': simulate backup request               ##\n"
  printf "## 'c': simulate validation of mysql service  ##\n"
  printf "## 's': simulate service stop                 ##\n"
  printf "## 'l': simulate log message                  ##\n"
  read -e -p "Enter your command : "  testcommand
  while [ "$testcommand" != "q" ];

  do
    case $testcommand in
        h)  say_hello                         ;;
        t)  get_local_time                    ;;
        o)  get_remote_time                   ;;
        b)  prompt_backup_confirmation        ;;
        c)  check_mysql_service               ;;
        s)  stop_service "mysql"              ;;
        l)  log_message "test message" "info" ;;
        *) printf "\n## Command doesn't exist. ##\n" ;;
    esac
    read -e -p "Enter your command : "  testcommand
  done

  printf "##      Thanks for using  testcommand see you next time...!        ##\n" # ------------------------------------------------------------|

}

if [[ "${BASH_SOURCE[0]}" == "${0}" || "${0}" == "/bin/bash" ]]; then
    main
fi