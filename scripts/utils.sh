#!/bin/bash

# Utility functions for colorcoding messages.
function info() {
    echo -e "\033[1;32mINFO:\033[0m $1"
}
function error() {
    echo -e "\033[1;31mERROR:\033[0m $1"
}
function warning() {
    echo -e "\033[1;33mWARNING:\033[0m $1"
}
