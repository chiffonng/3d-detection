#!/bin/bash
# Test number of parameters and parameters
echo "Number of parameters:" "$#"
echo "Parameters:" "$@"

# Hand over to bash shell to keep container running interactively
if [ "$#" -eq 0 ] || [ "$1" == "bash" ]; then
    # No command passed, default to bash
    echo "Enter bash shell... (run 'exit' to stop container)"
    exec bash
else
    # Execute passed command
    echo "Executing command: $*@"
    exec "$@"
fi
