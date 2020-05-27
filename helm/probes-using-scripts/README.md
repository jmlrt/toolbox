# Probes using scripts

This is a sample Helm chart which include a shell script for probes.

This is using Helm `.Files` to create a `ConfigMap` which includes the shell
scripts (see [Accessing Files Inside Templates][] for more details).
The `ConfigMap` can then be mounted on the pod containers as a directory
containing the scripts.

The main goal is to avoid shell in YAML in K8S templates when using Helm.
This allows to use static analysis tool like [shellcheck][] on the shell code
used in K8S templates (for probes or containers commands for example).

[accessing files inside templates]: https://v3.helm.sh/docs/chart_template_guide/accessing_files/
[shellcheck]: https://github.com/koalaman/shellcheck
