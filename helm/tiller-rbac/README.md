# Tiller with RBAC

```shell
$ kubectl create -f rbac-config.yaml
serviceaccount "tiller" created
clusterrolebinding "tiller" created
$ helm init --service-account tiller --history-max 200
```

source: https://v2.helm.sh/docs/rbac/#example-service-account-with-cluster-admin-role
