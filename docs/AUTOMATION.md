# Autonomous site operations

Update ops/sync-request.txt with a unique request to trigger Dropbox sync on main. No manual workflow dispatch is required. Check Actions job logs for OAuth, imported assets and errors. Verify assets/catalog/brand and manifest.json in repository. Branch-based Pages may not rebuild after bot-token pushes; make a normal connector commit after confirming assets, then verify public URLs. Never mark deployment complete before live verification. If Dropbox root is inaccessible, inspect app access scope. Do not expose secrets.
