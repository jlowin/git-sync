"""
Based on the Kubernetes git-sync sidecar module:
https://github.com/kubernetes/contrib/tree/master/git-sync
"""
import click
import os
import subprocess
import time

def sh(*args, **kwargs):
    return subprocess.check_output(*args, **kwargs).decode()

@click.command()
@click.option('--repo', '-r', envvar='GIT_SYNC_REPO', help='The git repo url to sync (can also be set with envvar GIT_SYNC_REPO).')
@click.option('--dest', '-d', envvar='GIT_SYNC_DEST', default=os.getcwd(), help='The destination path (default current working directory; can also be set with envvar GIT_SYNC_DEST).')
@click.option('--branch', '-b', envvar='GIT_SYNC_BRANCH', default='master', help='The branch to sync (default master; can also be set with envvar GIT_SYNC_BRANCH).')
@click.option('--rev', '-r', envvar='GIT_SYNC_REV', default=None, help='The revision to sync (default HEAD; can also be set with envvar GIT_SYNC_REV).')
@click.option('--wait', '-w', envvar='GIT_SYNC_WAIT', default=60, help='The number of seconds to pause after each sync (default 60; can also be set with envvar GIT_SYNC_WAIT)')
@click.option('--run-once', '-1', envvar='GIT_SYNC_RUN_ONCE', is_flag=True, help="Run only once (don't loop) (default off; can also be set with envvar GIT_SYNC_RUN_ONCE).")
def git_sync(repo, dest, branch, rev, wait, run_once):
    """
    Periodically syncs a remote git repository to a local folder. The sync is
    one-way; any local changes will be lost.
    """
    while True:
        sync_repo(repo, dest, branch, rev)
        if run_once:
            break
        click.echo('Waiting {wait} seconds...'.format(**locals()))
        time.sleep(wait)

def sync_repo(repo, dest, branch, rev):
    dest = os.path.expanduser(dest)

    # clone repo
    if not os.path.exists(os.path.join(dest, '.git')):
        output = sh(
            ['git', 'clone', '--no-checkout', '-b', branch, repo, dest])
        click.echo('Clone {repo}: {output}'.format(**locals()))

    # fetch branch
    output = sh(['git', 'fetch', 'origin', branch], cwd=dest)
    click.echo('Fetch {branch}: {output}'.format(**locals()))

    # reset working copy
    if not rev:
        output = sh(['git', 'reset', '--hard', 'origin/' + branch], cwd=dest)
    else:
        output = sh(['git', 'reset', '--hard', rev], cwd=dest)
    click.echo('Reset {rev}: {output}'.format(**locals()))

    # set file permissions
    sh(['chmod', '-R', '744', dest])

    click.echo('Finished syncing {repo}:{branch}'.format(**locals()))

if __name__ == '__main__':
    git_sync()
