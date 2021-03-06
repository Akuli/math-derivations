# Math Derivations

[Click here](https://akuli.github.io/math-derivations)
to read the content of this site.
The site contains derivations and proofs for math things
that are used in high school math.

## Commands for writing stuff to this site

Environment setup (I have no idea what you should do if you don't have `apt`):

```
$ sudo apt install asymptote linkchecker make inotify-tools
$ python3 -m pip install --user wheel
$ python3 -m venv env
$ . env/bin/activate
(env) $ pip install -r requirements.txt
(env) $ ./imagecachesync.sh
```

Run these commands **with the virtualenv activated** as needed:

- Building into `html` directory: `python3 build.py`
- Building automatically when a file is saved in the editor: `make buildloop`
- Checking links: `make linkcheck`
- Publishing to github pages: `python3 publish.py`
