#!/usr/bin/env bash
set -euo pipefail

CONTAINER="${KAFKA_CONTAINER:-deriv-kafka-local}"
BOOTSTRAP="${KAFKA_BOOTSTRAP:-localhost:9092}"

topics=(
  workflow.scheduled
  workflow.execute
  workflow.run.status
)

KAFKA_TOPICS_BIN="${KAFKA_TOPICS_BIN:-/opt/kafka/bin/kafka-topics.sh}"

for topic in "${topics[@]}"; do
  docker exec "$CONTAINER" "$KAFKA_TOPICS_BIN" \
    --bootstrap-server "$BOOTSTRAP" \
    --create \
    --if-not-exists \
    --topic "$topic" \
    --partitions 3 \
    --replication-factor 1
  echo "Topic ready: $topic"
done
