#!/usr/bin/env python3

import sys

message = "Hello, world!"

if len(sys.argv) > 1:
    message = "Hello, " + " ".join([str(elem) for elem in sys.argv[1:]])

print(message)
