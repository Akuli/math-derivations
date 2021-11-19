#!/usr/bin/env python3
"""build the docs and commit them to the gh-pages branch"""

import os
import pathlib
import shlex
import shutil
import subprocess
import sys
import tempfile


def run(*command, cwd=None):
    command_string = ' '.join(map(shlex.quote, command))
    if cwd:
        print(f"running {command_string!r} in {cwd}")
    else:
        print(f"running {command_string!r}")

    subprocess.check_call(list(command), cwd=cwd)


def main():
    if not os.environ.get('VIRTUAL_ENV'):
        sys.exit(f"{sys.argv[0]}: not running in virtualenv (see README.md)")

    run(sys.executable, 'build.py')

    print("creating a temporary directory for building docs")
    with tempfile.TemporaryDirectory() as tmpdir:
        run('git', 'clone', '--depth=1', '--branch=gh-pages', 'https://github.com/Akuli/math-derivations', cwd=tmpdir)
        temp_git_dir = pathlib.Path(tmpdir) / 'math-derivations'
        run('git', 'checkout', 'gh-pages', cwd=temp_git_dir)

        for subpath in temp_git_dir.iterdir():
            if subpath.name not in {'.git', '.gitignore'}:
                print(f"deleting {subpath}")
                try:
                    shutil.rmtree(subpath)
                except NotADirectoryError:
                    subpath.unlink()

        # TODO: do this in a simpler way?
        temp_html_path = pathlib.Path(tmpdir) / 'html'
        print(f"copying: html --> {temp_html_path}")
        shutil.copytree('html', temp_html_path)
        for subpath in temp_html_path.iterdir():
            new_path = temp_git_dir / subpath.name
            print(f"moving: {subpath} --> {new_path}")
            subpath.rename(new_path)

        run('git', 'add', '--all', '.', cwd=temp_git_dir)
        run('git', 'commit', '-m', f'publishing with {__file__}', cwd=temp_git_dir)
        run('git', 'push', 'origin', 'gh-pages', cwd=temp_git_dir)


if __name__ == '__main__':
    main()
