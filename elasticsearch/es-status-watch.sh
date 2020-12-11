#!/bin/bash

if [ -z ${ELASTICSEARCH_HOST+x} ]
then
  echo "ELASTICSEARCH_HOST is unset"
  exit 1
fi

while true
do
  curl $ELASTICSEARCH_HOST:9200/_cat/health
  curl $ELASTICSEARCH_HOST:9200/_cat/nodes\?v
  curl $ELASTICSEARCH_HOST:9200/_cat/shards\?v
  curl $ELASTICSEARCH_HOST:9200/_cat/allocation\?v
  echo
  echo
  sleep 5
done
