#!/bin/sh
# Vercel build step for project "dormant-yield" (team Nordic MarTech) until GitHub is connected to Vercel.
# The deployment uploads only this file and vercel.json. The build fetches the site at a pinned commit
# from the public GitHub repo, runs the launch gate, then serves public/.
# To ship a new version: commit and push, set SHA to the new commit, redeploy.
set -e
SHA=86f3177e2dc66badd36697ff957b29ec68a6e4a5
curl -fsSL "https://codeload.github.com/fkaada/frankfurterNM/tar.gz/$SHA" -o src.tgz
mkdir -p src
tar xzf src.tgz -C src --strip-components=1
node src/sites/dormant-yield/tests/check.mjs --launch
rm -rf public
cp -r src/sites/dormant-yield/public public
