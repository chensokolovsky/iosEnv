#!/bin/bash

PROJECT_NAME="iosEnv"

log() {
  local level="$1"; shift
  local color reset timestamp script
  timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
  script="$(basename "$0")"
  reset='\033[0m'
  case "$level" in
    INFO)  color='\033[1;34m' ;;  # Blue
    WARN)  color='\033[1;33m' ;;  # Yellow
    ERROR) color='\033[1;31m' ;;  # Red
    *)     color='\033[0m'   ;;
  esac
  echo -e "${color}[$timestamp] [$PROJECT_NAME] [$script] [$level] $*${reset}"
}
