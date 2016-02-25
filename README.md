# git-sync

`git-sync` is a command that periodically syncs a remote git repository to a
local directory.

This Python implementation is inspired by the Kubernetes module found here: https://github.com/kubernetes/contrib/tree/master/git-sync

## Usage

#### Python
To see available arguments:
```
python git-sync.py --help
```
Pass arguments at the command line:
```bash
python git-sync.py repo.git --dest /dest/path --branch branch --wait 30
```
or with environment variables:
```bash
GIT_SYNC_REPO=repo.git GIT_SYNC_DEST=/dest/path python git-sync.py
```

#### Docker
```bash
docker run -v /vol jlowin/git-sync repo.git --dest /vol --wait 100
```

#### Kubernetes
`git-sync` was originally designed as a side-car module that keeps a (shared) container volume in sync with a remote git repository.

For example, in a replication controller definition:
```yaml
# this volume holds the synced repo
volumes:
- name: git_sync_volume
  emptyDir: {}

# this container syncs the repo every 1000 seconds
containers:
- name: git-sync
  image: jlowin/git-sync
  volumeMounts:
  - name: git_sync_volume
    mountPath: /git
  env:
  - name: GIT_SYNC_REPO
    value: <repo>
  - name: GIT_SYNC_DEST
    value: /git
  - name: GIT_SYNC_BRANCH
    value: <branch>
  - name: GIT_SYNC_WAIT
    value: "1000"

# this container can access the synced data
- name: my-container
  volumeMounts:
  - name: git_sync_volume
    mountPath: /synced
```
