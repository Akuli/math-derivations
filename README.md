# Math Derivations

[Click here](https://akuli.github.io/math-derivations)
to read the content of this site.
The site contains derivations and proofs for math things
that are used in high school math.

## Commands for writing stuff to this site

Environment setup (I have no idea what you should do if you don't have `apt`):

```
$ sudo apt install asymptote
$ python3 -m pip install --user wheel
$ python3 -m venv env
$ . env/bin/activate
(env) $ pip install -r requirements.txt
(env) $ python3 build.py
```

If you want `build.py` to send F5 to the browser window where math-derivations is open:

```
(env) $ sudo apt install xdotool
(env) $ python3 build.py --reload-browser
```

If you want to check links (also done in Github Actions):

```
(env) $ python3 build.py --check-links
```

To publish, run `git push`, and let Github Actions take care of the rest.

If you create or modify images drawn with asymptote,
you should commit the resulting files in `images/asy/`.
The images are committed to Git, for several reasons:
- This makes `build.py` really fast. Rebuilding images is slow.
- Some images were created with an old, backwards-incompatible version of asymptote.
    If those weren't committed, I would have to upgrade them to work with newer asymptote versions.
- Building 3D images on github actions just doesn't work, because it apparently requires a GPU.
