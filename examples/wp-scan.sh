#!/usr/bin/env sh

#--------------------------------------------------------------------------------------------------------
#
# This example demonstrates how to scan a WordPress site and automatically open a Jira
# when vulnerabilities has been identified.
#
# This script can be ran on a daily basis for example, and will update the issue with a new attahcment
# if the site still contains known vulnerabilities (use crontab for that).
#
# Prerequisites: Docker.
# Note: You can install wpscan locally and remove the Dockerization.
#
#--------------------------------------------------------------------------------------------------------

LOG_PATH="/tmp/wp-scan.txt"

#
# Customize the following in order for this to work.
#
DOMAIN="https://my-super-secure-wp-site.com" # The domain to scan.
SUBJECT="WP vulnerabilities had been identified in ${DOMAIN}" # The subject for new issues.
PROJECT_KEY="PROJ" # The project key in your Jira.
API_TOKEN="WPScan-API-TOKEN(Free-is-just-fine)" # Register at https://wpvulndb.com/ .

# Update WPScan before performing the scan to make sure we are up to date.
updateScanner() {
  echo "Updating WPScan"
  docker pull wpscanteam/wpscan
}

# Perform the actual scan.
scan() {
  echo "Starting scan"
  # Clean old scan file if exists.
  rm -f $LOG_PATH
  # Scan.
  docker run --rm wpscanteam/wpscan --url $DOMAIN --no-update --api-token "${API_TOKEN}"  > $LOG_PATH
}

# Check if vulnerabilities has been identified, and if so - update our Jira.
handleJira() {
  if grep -q -i -e 'vulnerability identified' -e 'vulnerabilities identified' $LOG_PATH; then
    python jtrack.py -i "${DOMAIN}" -p "${PROJECT_KEY}" -s "${SUBJECT}" -a "${LOG_PATH}";
  fi
}

# Call our functions and do the work.
updateScanner
scan
handleJira
