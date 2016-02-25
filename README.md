# git-sync

`git-sync` is a command that periodically syncs a remote git repository to a
local directory.

This Python implementation is inspired by the Kubernetes module found here: https://github.com/kubernetes/contrib/tree/master/git-sync

## Kubernetes
`git-sync` was originally designed as a side-car module that keeps a container
volume in sync with a remote git repository.
