#!/usr/bin/env bash

# Usage: ./create-kubeconfig.sh <k8s master url> <secret token>

# kubernetes master url (`kubectl cluster-info`)
server=$1
# service account token secret name (`kubectl get secrets --show-kind | grep kubernetes.io/service-account-token`)
token_name=$2

sa_name=${token_name%-*-*}
ca=$(kubectl get secret/"$token_name" -o jsonpath='{.data.ca\.crt}')
token=$(kubectl get secret/"$token_name" -o jsonpath='{.data.token}' | base64 --decode)
namespace=$(kubectl get secret/"$token_name" -o jsonpath='{.data.namespace}' | base64 --decode)

echo "apiVersion: v1
kind: Config
clusters:
- name: default-cluster
  cluster:
    certificate-authority-data: ${ca}
    server: ${server}
contexts:
- name: default-context
  context:
    cluster: default-cluster
    namespace: ${namespace}
    user: ${sa_name}
current-context: default-context
users:
- name: ${sa_name}
  user:
    token: ${token}" | tee "${sa_name}.kubeconfig"
