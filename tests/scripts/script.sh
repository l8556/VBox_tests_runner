#!/usr/bin/bash
cd ~/scripts/oo_desktop_testing
git pull
source ~/scripts/oo_desktop_testing/.venv/bin/activate
inv desktop -v 7.4.0.163