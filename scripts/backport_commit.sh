#!/bin/bash

# This script backport a commit to others branches
# Usage: ./backport_commit.sh <COMMIT_ID> <DESTINATION BRANCH> [<OTHER DESTINATION BRANCH> ...]

COMMIT_ID=$1

# remove the first argument (COMMIT_ID) and set the rest of the arguments as a list of branches
shift
BRANCHES="$*"

for BRANCH in $BRANCHES; do
  echo "Backporting commit $COMMIT_ID to branch $BRANCH"
  git checkout "$BRANCH"
  git pull
  git cherry-pick "$COMMIT_ID"
  RC=$?
  if [ "$RC" == 0 ]; then
    echo "Pushing branch $BRANCH"
    git push
  else
    echo "There is some conflict to resolve"
    while true; do
      read -r -p "Enter 'yes' when the conflict is resolved: " key
      if [ "$key" == "yes" ]; then
        echo "Pushing branch $BRANCH"
        git push
        break
      fi
    done
  fi
done
