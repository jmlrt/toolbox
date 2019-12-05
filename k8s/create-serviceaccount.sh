#!/usr/bin/env bash
#
# Generate serviceaccount with full access into a defined namespace
#
# Usage: ./create-serviceaccount.sh <serviceaccount name> <namespace> [apply]

sa_name=$1
namespace=$2
apply=$3

echo "---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: $sa_name
  namespace: $namespace

---
kind: Role
apiVersion: rbac.authorization.k8s.io/v1beta1
metadata:
  name: ${sa_name}-role
  namespace: $namespace
rules:
  - apiGroups: [\"\", \"extensions\", \"apps\"]
    resources: [\"*\"]
    verbs: [\"*\"]
  - apiGroups: [\"batch\"]
    resources:
      - jobs
      - cronjobs
    verbs: [\"*\"]

---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1beta1
metadata:
  name: ${sa_name}-rolebinding
  namespace: $namespace
subjects:
- kind: ServiceAccount
  name: $sa_name
  namespace: $namespace
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: ${sa_name}-role" | tee "${sa_name}.yml"

test "$apply" == "apply" && kubectl create -f "${sa_name}.yml"
