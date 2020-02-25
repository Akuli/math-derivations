#!/usr/bin/env python3
import collections
import functools
import glob
import hashlib
import itertools
import os
import re
import shutil
import subprocess
import tempfile
import textwrap
import xml.etree.ElementTree

from htmlthingy import Builder, tags, linkcheck
from bs4 import BeautifulSoup


# TODO: move these to htmlthingy
os.makedirs('imagecache', exist_ok=True)


def cache_get(filename):
    cached = os.path.join('imagecache', filename)
    if os.path.exists(cached):
        return cached
    return None


def cache_put(tempfilename, cachefilename):
    os.makedirs('imagecache', exist_ok=True)
    shutil.copy(tempfilename, os.path.join('imagecache', cachefilename))


builder = Builder()

builder.infiles = sorted(
    glob.glob('content/*.txt')
    + glob.glob('content/*/*.txt')
    + glob.glob('content/*/*/*.txt')
)

builder.infile2outfile = lambda infile: os.path.join(
    builder.outputdir,
    os.path.splitext(infile.replace('content' + os.sep, '', 1))[0] + '.html')

builder.converter.pygments_style = 'friendly'


def get_sidebar_content(txtfile):
    def link(text, target):
        return '<a href="%s.html">%s</a>' % (
            os.path.relpath(
                target, os.path.dirname(os.path.relpath(txtfile, 'content'))
            ).replace(os.sep, '/'),
            text,
        )

    id_counter = itertools.count()

    def dropdown(title, content):
        checkbox_id = 'sidebar-checkbox-' + str(next(id_counter))
        return '''
        <input type="checkbox" id="%s" />
        <label for="%s">%s</label>
        <div class="dropdown">
            %s
        </div>
        ''' % (checkbox_id, checkbox_id, title, content)

    join = ''.join

#    return '<div id="sidebar">%s</div>' % join([
    return join([
        link("Front page", 'index'),
        dropdown("Analytic plane geometry", join([
            dropdown("Line", join([
                link("Equation in normal form",
                     'analytic-plane-geometry/line-eq-slope'),
                link("Distance between line and point",
                     'analytic-plane-geometry/distance-line-point'),
                link("Equation with slope",
                     'analytic-plane-geometry/line-eq-slope'),
                link("Equation from known slope and point",
                     'analytic-plane-geometry/line-eq-slope-and-point'),
                link("Angle between lines",
                     'analytic-plane-geometry/angle-between-lines'),
                link("Equation with determinant",
                     'analytic-plane-geometry/line-eq-determinant'),
            ])),
            dropdown("Hyperbola", join([
                link("Why is y=1/x a hyperbola?",
                     'analytic-plane-geometry/why-its-hyperbola'),
            ])),
        ])),
    ])


def get_head_extras(filename):
    print(filename)
    result = '''
    <script type="text/x-mathjax-config">
      MathJax.Hub.Config({
        extensions: ["tex2jax.js"],
        jax: ["input/TeX", "output/HTML-CSS"],
        tex2jax: {
          inlineMath: [ ['$','$'] ],
          displayMath: [ ['$$','$$'] ],
        },
        "HTML-CSS": { availableFonts: ["TeX"] },
        TeX: {
          Macros: {
            // awesome, latex inside javascript inside html inside python
            // https://xkcd.com/1638/
            Vec: [ "\\\\overrightarrow{#1}", 1 ],
            abs: [ "\\\\left| {#1} \\\\right|", 1 ],
            I: [ "\\\\vec{i}", 0 ],
            J: [ "\\\\vec{j}", 0 ],
            K: [ "\\\\vec{k}", 0 ],

            red: [ "\\\\color{red}{#1}", 1 ],
            blue: [ "\\\\color{blue}{#1}", 1 ],
            green: [ "\\\\color{green}{#1}", 1 ],
            maroon: [ "\\\\color{maroon}{#1}", 1 ],
            olive: [ "\\\\color{olive}{#1}", 1 ],
            purple: [ "\\\\color{purple}{#1}", 1 ],
            black: [ "\\\\color{black}{#1}", 1 ],
            implies: [ "\\\\Rightarrow", 0 ]
          }
        }
      });
    </script>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs\
/mathjax/2.7.2/MathJax.js"></script>
    <link href="https://fonts.googleapis.com/css?family=Cabin|Quicksand" rel="\
stylesheet">

    <script>
    // this is easier to write in javascript than in python
    </script>
    '''


builder.get_sidebar_content = get_sidebar_content


builder.get_head_extras = lambda filename: '''
'''


@builder.converter.add_inliner(r'\\\*')
def escaped_star(match, filename):
    return r'*'


@builder.converter.add_multiliner(r'^indent2:\n')
def indent2_handler(match, filename):
    markup = textwrap.dedent(match.string[match.end():])
    assert markup, "blank line after 'indent2:'"
    yield '<div class="indent">'
    yield '<div class="indent">'
    yield from builder.converter.convert(markup, filename)
    yield '</div>'
    yield '</div>'


asyboilerplates = collections.defaultdict(str)


@builder.converter.add_multiliner(r'^asyboilerplate(3d)?:(.*)\n')
def add_more_asymptote_boilerplate(match, filename):
    code = textwrap.dedent(match.string[match.end():])
    asyboilerplates[(filename, match.group(1))] += code + '\n'
    return ''


@builder.converter.add_multiliner(r'^asymptote(3d)?:(.*)\n')
def asymptote(match, filename):
    format = 'png' if match.group(1) else 'svg'     # 3d svg's dont work :(
    fullcode = ('import boilerplate%s;\n' % (match.group(1) or '')) + (
        asyboilerplates[(filename, match.group(1))] +
        textwrap.dedent(match.string[match.end():]))
    fullfilename = (hashlib.md5(fullcode.encode('utf-8')).hexdigest()
                    + '.' + format)
    os.makedirs(os.path.join(builder.outputdir, 'asymptote'), exist_ok=True)
    outfile = os.path.join(builder.outputdir, 'asymptote', fullfilename)

    if cache_get(fullfilename) is None:
        with tempfile.TemporaryDirectory() as tmpdir:
            for file in glob.glob('asymptote/*.asy'):
                shutil.copy(file, tmpdir)

            with open(os.path.join(tmpdir, 'image.asy'), 'w') as file:
                file.write(fullcode)

            subprocess.check_call(
                ['asy', '-f', format, '--libgs=', 'image.asy'], cwd=tmpdir)
            cache_put(os.path.join(tmpdir, 'image.' + format), fullfilename)

    shutil.copy(cache_get(fullfilename), outfile)

    if format == 'svg':
        # figure out the correct size (lol)
        attribs = xml.etree.ElementTree.parse(outfile).getroot().attrib
        assert attribs['width'].endswith('pt')
        assert attribs['height'].endswith('pt')
        size = (float(attribs['width'][:-2]),
                float(attribs['height'][:-2]))
        extrainfo = 'width="%.0f" height="%.0f"' % size
    else:
        extrainfo = ''

    htmlfile = builder.infile2outfile(filename)
    relative = os.path.relpath(outfile, os.path.dirname(htmlfile))

    html = tags.image(relative.replace(os.sep, '/'), match.group(2))
    return html.replace('<img', '<img %s class="asymptote"' % extrainfo, 1)


builder.run()

# FIXME: linkcheck doesn't understand relative stuff, it's annoying
#linkcheck.run(builder.outputdir)

# tell github pages to do the right thing
open(os.path.join(builder.outputdir, '.nojekyll'), 'x').close()
