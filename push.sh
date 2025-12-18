#!/bin/bash
cd /Users/jeanbapt/nemotron-nano
git add .github/workflows/deploy.yml README.md
git commit -m "Fix: Use Koyeb REST API directly, bypass buggy CLI action"
git push origin main


