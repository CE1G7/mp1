#!/bin/sh
set -e

: "${MQTT_USERNAME:?MQTT_USERNAME is required}"
: "${MQTT_PASSWORD:?MQTT_PASSWORD is required}"

# Regenerated on every start, so changing .env and recreating the container updates the user
mosquitto_passwd -b -c /mosquitto/passwd "$MQTT_USERNAME" "$MQTT_PASSWORD"
chown mosquitto:mosquitto /mosquitto/passwd
chmod 0600 /mosquitto/passwd

# Hand off to the image's original entrypoint, which fixes permissions and runs the CMD
exec /docker-entrypoint.sh "$@"
