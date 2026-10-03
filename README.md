# Legis Archive updater connectivity test

This repository contains only a bounded test of two public legis.md endpoints.
It contains no archive corpus, credentials, cookies or private project source.

The manually dispatched workflow uses standard GitHub-hosted Ubuntu runners in
a public repository. It has a five-minute limit, read-only repository permission,
no recurring schedule and no artifact upload. It does not update any archive.
It stops on a blocked source and never solves challenges or rotates proxies.

Successful HTTP access establishes connectivity from the runner, not a working
unattended updater or complete source coverage.
