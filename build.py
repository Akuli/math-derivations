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

builder.additional_files.append('js')


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
        dropdown("Equations and functions", join([
            link("Inverse functions",
                 'eqs-and-funcs/inverse-funcs'),
            link("How solving equations works",
                 'eqs-and-funcs/how-equations-work'),
            link("Strictly increasing/decreasing functions",
                 'eqs-and-funcs/incdec-funcs'),
            link("How solving inequalities works",
                 'eqs-and-funcs/how-inequations-work'),
        ])),
        dropdown("Vectors", join([
            dropdown("Dot product", join([
                link("Projection", 'vectors/dot-projection'),
                link("Angle between vectors", 'vectors/angle-between-vectors'),
                link("$\I$'s with $\I$'s, $\J$'s with $\J$'s",
                     'vectors/iwi-jwj'),
            ])),
        ])),
        dropdown("Analytic plane geometry", join([
            dropdown("Transforming curves", join([
                link("Reflecting", 'analytic-plane-geometry/reflect'),
                link("Shifting", 'analytic-plane-geometry/shift'),
                link("Stretching", 'analytic-plane-geometry/stretch'),
            ])),
            dropdown("Line", join([
                link("Equation in normal form",
                     'analytic-plane-geometry/line-eq-normal'),
                link("Distance between line and point",
                     'analytic-plane-geometry/distance-line-point'),
                link("Equation with slope",
                     'analytic-plane-geometry/line-eq-slope'),
                link("Equation from known slope and point",
                     'analytic-plane-geometry/line-eq-slope-and-point'),
                link("Angle between lines",
                     'analytic-plane-geometry/angle-between-lines'),
                link("Slope and tan", 'analytic-plane-geometry/slope-tan'),
                link("Equation with determinant",
                     'analytic-plane-geometry/line-eq-determinant'),
            ])),
            dropdown("Parabola", join([
                link("Equation of parabola",
                     'analytic-plane-geometry/parabola'),
            ])),
            dropdown("Hyperbola", join([
                link(r"Why is $y=\frac{1}{x}$ a hyperbola?",
                     'analytic-plane-geometry/why-its-hyperbola'),
            ])),
        ])),
        dropdown("Calculus", join([
            dropdown("Limits", join([
                link("Definition of limit", 'calc/limit-def'),
                link("Limit basics", 'calc/limit-basics'),
                link("Limit properties", 'calc/limit-props'),
                link("One-sided limits", 'calc/limit-1sided'),
                link("Inequality and limit", 'calc/limit-ineq'),
                # I don't like the absolute value thing, commented out for now
                #link("Absolute values in limit proofs", 'calc/limit-abs'),
            ])),
            dropdown("Continuity", join([
                link("Definitions of continuity", 'calc/cont-def'),
                link("Continuity properties", 'calc/cont-props'),
            ])),
            dropdown("Derivative", join([
                link("Definition of derivative", 'calc/derivative-def'),
                link("Notation for derivatives", 'calc/derivative-notation'),
                link("Power rule, part 1", 'calc/derivative-power-rule-1'),
                link("Basic derivative rules", 'calc/derivative-basic-rules'),
                link("Chain rule", 'calc/derivative-chain-rule'),
                link("Power rule, part 2", 'calc/derivative-power-rule-2'),
                link("Product rule and quotient rule",
                     'calc/derivative-product-quotient-rules'),
            ])),
        ])),
    ])


def get_head_extras(filename):
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

            red: [ "\\\\color{darkred}{#1}", 1 ],
            blue: [ "\\\\color{blue}{#1}", 1 ],
            green: [ "\\\\color{green}{#1}", 1 ],

            epsi: [ "\\\\varepsilon", 0 ],
          }
        }
      });
    </script>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs\
/mathjax/2.7.2/MathJax.js"></script>
    <link href="https://fonts.googleapis.com/css?family=Cabin|Quicksand" rel="\
stylesheet">

    <script>
    // mark the selected page and open the menus leading to it
    // this is easier to write in javascript than in python
    document.addEventListener('DOMContentLoaded', () => {
        let thisPage = window.location.href.split('#')[0];
        if (thisPage.endsWith('/')) {
            thisPage += 'index.html';
        }

        const [selectedLink] = [...document.querySelectorAll('#sidebar a')]
            .filter(a => (a.href === thisPage));
        selectedLink.classList.add('this-page-or-section');

        let dropdown = selectedLink.parentElement;
        while (dropdown.classList.contains('dropdown')) {
            const label = dropdown.previousElementSibling;
            const checkbox = label.previousElementSibling;
            label.classList.add('this-page-or-section');
            checkbox.checked = true;

            dropdown = dropdown.parentElement;
        }
    });
    </script>
    '''

    if filename == 'content/vectors/dot-projection.txt':
        result += '''
        <script src="../js/vendor/three.js"></script>
        <script src="../js/common.js"></script>
        <script src="../js/projection-demo.js"></script>
        '''

    return result


builder.get_sidebar_content = get_sidebar_content
builder.get_head_extras = get_head_extras


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


# without this, two underlines in math make the latex code get <ul> tags
@builder.converter.add_inliner(r'\$\$\n[\S\s]*?\n\$\$')
def math_handler(match, filename):
    return match.group(0)


@builder.converter.add_multiliner(r'^insert-function-warning-here\n')
def function_warning(match, filename):
    return '''
    <div class="box redbox">
    <p>
        On this page, the word "function" means a function that
        takes in a real number as its only argument,
        and evaluates to another real number.
        Some real numbers might not be valid inputs of the function;
        for example, square root is a function that
        accepts only nonnegative inputs.
    </p>
    </div>
    '''


@builder.converter.add_multiliner(r'^asymptote(3d)?:(.*)\n')
def asymptote(match, filename):
    format = 'png' if match.group(1) else 'svg'     # 3d svg's dont work :(
    fullcode = ('import boilerplate%s;\n' % (match.group(1) or '')) + (
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

# tell github pages to do the right thing
open(os.path.join(builder.outputdir, '.nojekyll'), 'x').close()
