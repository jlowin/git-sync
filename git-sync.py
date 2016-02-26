#!/usr/bin/env python
from __future__ import print_function
import click
import os
import shlex
import subprocess
import sys
import time
# try to be py2/3 compatible
try:
     from urllib.parse import urlparse
except ImportError:
     from urlparse import urlparse

# hide tracebacks
sys.excepthook = (
    lambda exctype,exc,traceback : print("{}: {}".format(exctype.__name__,exc)))

def sh(*args, **kwargs):
    """ Get subprocess output"""
    return subprocess.check_output(*args, **kwargs).decode().strip()

def setup_repo(repo, dest, branch):
    """
    Clones `branch` of remote `repo` to `dest`, if it doesn't exist already.
    Raises an error if a different repo or branch is found.
    """
    dest = os.path.expanduser(dest)

    # if no git repo exists at dest, clone the requested repo
    if not os.path.exists(os.path.join(dest, '.git')):
        output = sh(
            ['git', 'clone', '--no-checkout', '-b', branch, repo, dest])
        click.echo('Cloned {repo}: {output}'.format(**locals()))

    else:
        # if there is a repo, make sure it's the right one
        current_remote = sh([
                'bash',
                '-c',
                'git remote show -n origin | grep Fetch | cut -d: -f2-'],
            cwd=dest).lower()
        parsed_remote = urlparse(current_remote)
        repo = repo.lower()
        if not repo.endswith('.git'):
            repo = repo + '.git'
        parsed_repo = urlparse(repo)
        if (    parsed_repo.netloc != parsed_remote.netloc
                or parsed_repo.path != parsed_remote.path):
            raise ValueError(
                'Destination already has a remote repo '
                'cloned: {current_remote}'.format(**locals()))

        # and check that the branches match as well
        current_branch = sh(
            shlex.split('git rev-parse --abbrev-ref HEAD'),
            cwd=dest)
        if branch.lower() != current_branch.lower():
            raise ValueError(
                'Destination is on branch {current_branch}; '
                'requested {branch}'.format(**locals()))

def sync_repo(repo, dest, branch, rev):
    """
    Syncs `branch` of remote `repo` (at `rev`) to `dest`.
    Assumes `dest` has already been cloned.
    """
    # fetch branch
    output = sh(['git', 'fetch', 'origin', branch], cwd=dest)
    click.echo('Fetched {branch}: {output}'.format(**locals()))

    # reset working copy
    if not rev:
        output = sh(['git', 'reset', '--hard', 'origin/' + branch], cwd=dest)
    else:
        output = sh(['git', 'reset', '--hard', rev], cwd=dest)
    click.echo('Reset to {rev}: {output}'.format(**locals()))

    # set file permissions
    sh(['chmod', '-R', '744', dest])

    click.echo('Finished syncing {repo}:{branch}'.format(**locals()))

@click.command()
@click.argument('repo', envvar='GIT_SYNC_REPO')
@click.option('--dest', '-d', envvar='GIT_SYNC_DEST', default=os.getcwd(), help='The destination path (default current working directory; can also be set with envvar GIT_SYNC_DEST).')
@click.option('--branch', '-b', envvar='GIT_SYNC_BRANCH', default='master', help='The branch to sync (default master; can also be set with envvar GIT_SYNC_BRANCH).')
@click.option('--rev', '-r', envvar='GIT_SYNC_REV', default=None, help='The revision to sync (default HEAD; can also be set with envvar GIT_SYNC_REV).')
@click.option('--wait', '-w', envvar='GIT_SYNC_WAIT', default=60, help='The number of seconds to pause after each sync (default 60; can also be set with envvar GIT_SYNC_WAIT)')
@click.option('--run-once', '-1', envvar='GIT_SYNC_RUN_ONCE', is_flag=True, help="Run only once (don't loop) (default off; can also be set with envvar GIT_SYNC_RUN_ONCE).")
def git_sync(repo, dest, branch, rev, wait, run_once):
    """
    Periodically syncs a remote git repository (REPO) to a local directory. The sync
    is one-way; any local changes will be lost.

    The env var GIT_SYNC_REPO can be set to avoid passing arguments.
    """
    setup_repo(repo, dest, branch)
    while True:
        sync_repo(repo, dest, branch, rev)
        if run_once:
            break
        click.echo('Waiting {wait} seconds...'.format(**locals()))
        time.sleep(wait)

if __name__ == '__main__':
    git_sync()
