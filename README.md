# git-sync

`git-sync` is a command that periodically syncs a remote git repository to a
local directory.

This Python implementation is inspired by the Kubernetes module found here: https://github.com/kubernetes/contrib/tree/master/git-sync

## Usage

#### Python
Install/setup
```bash
pip install click
git clone https://github.com/jlowin/git-sync.git
cd git-sync && chmod +x git-sync.py
```
To see available arguments:
```bash
./git-sync.py --help
```
Pass arguments at the command line:
```bash
./git-sync.py repo.git --dest /dest/path --branch branch --wait 30
```
or with environment variables:
```bash
GIT_SYNC_REPO=repo.git GIT_SYNC_DEST=/dest/path ./git-sync.py
```

#### Docker
By default, the docker container syncs to an internal directory `/git`.
```bash
docker run -v /vol jlowin/git-sync repo.git --dest /vol --wait 100
```
(This is a spectacularly useless example; you probably want to connect another container to the synced volume.)

#### Kubernetes
`git-sync` was originally designed as a side-car module that keeps a (shared) container volume in sync with a remote git repository.

For example, in a replication controller definition:
```yaml
# this volume holds the synced repo
volumes:
- name: git-sync-volume
  emptyDir: {}

# this container syncs the repo every 1000 seconds
containers:
- name: git-sync
  image: jlowin/git-sync
  volumeMounts:
  - name: git-sync-volume
    mountPath: /git
  env:
  - name: GIT_SYNC_REPO
    value: <repo>
  - name: GIT_SYNC_DEST
    value: /git
  - name: GIT_SYNC_WAIT
    value: "1000"

# this container can access the synced data in /synced
- name: my-container
  volumeMounts:
  - name: git-sync-volume
    mountPath: /synced
```
