#!/bin/bash
#
# Source:
# - https://blog.zwindler.fr/2020/01/20/kubectl-tips-and-tricks-n2/

echo -e "Base64 decoding.. \n"
for arg in "\$@"; do
  echo "\$arg :"
  echo -n "\$arg" | base64 -d
  echo
done
