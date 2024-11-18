#!/usr/bin/env python3
import argparse
import glob
import hashlib
import itertools
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import xml.etree.ElementTree

from htmlthingy import Builder, tags

from linkcheck import check_links


def init_asycache():
    os.makedirs('asycache', exist_ok=True)

    # Move everything from images/asy/ to asycache/
    for name in os.listdir('images/asy'):
        if os.path.exists(f"asycache/{name}"):
            with open(f"asycache/{name}", "rb") as file1:
                with open(f"images/asy/{name}", "rb") as file2:
                    assert file1.read() == file2.read()
            os.remove(f"images/asy/{name}")
        else:
            shutil.move(f"images/asy/{name}", f"asycache/{name}")


init_asycache()


def get_image(name):
    if os.path.exists(f"asycache/{name}"):
        if not os.path.exists(f"images/asy/{name}"):
            shutil.copy(f"asycache/{name}", f"images/asy/{name}")
        return f"images/asy/{name}"
    return None


def put_image(tempfilename, name):
    shutil.copy(tempfilename, f"asycache/{name}")
    shutil.copy(tempfilename, f"images/asy/{name}")


builder = Builder()

builder.infiles = sorted(
    glob.glob('content/*.txt')
    + glob.glob('content/*/*.txt')
    + glob.glob('content/*/*/*.txt')
)
builder.infile2outfile = lambda infile: os.path.join(
    builder.outputdir,
    os.path.splitext(infile.replace('content' + os.sep, '', 1))[0] + '.html')
builder.additional_files = ["css", "js", "images"]


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
                link(r"$\I$'s with $\I$'s, $\J$'s with $\J$'s",
                     'vectors/iwi-jwj'),
            ])),
            dropdown("Cross product", join([
                link("Definition", 'vectors/cross-def'),
            ])),
        ])),

        dropdown("Discrete math", join([
            link("Sum formulas", 'discrete/sums'),
            link("Binomial coefficients", 'discrete/binom'),
        ])),

        dropdown("Plane geometry", join([
            # TODO: explain which things are not proved here
            dropdown("Circle", join([
                link("Inscribed angle theorem",
                     'plane-geometry/inscribed-angle-theorem'),
            ])),
            dropdown("Triangle", join([
                # TODO: sin, cos, tan in triangles
                # TODO: sum of angles
                # TODO: triangle area
                link("Law of sines", 'plane-geometry/law-of-sines'),
                link("Law of cosines", 'plane-geometry/law-of-cosines'),
                link("Inscribed circle", 'plane-geometry/inscribed-circle'),
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
                link('"Definition" by plugging in numbers', 'calc/limit-intro'),
                link("Small functions", 'calc/limit-small'),
                link("Definition of limit", 'calc/limit-def'),
                link("Limit basics", 'calc/limit-basics'),
                link("Limit properties", 'calc/limit-props'),
                link("Limit of division", 'calc/limit-div'),
                link("One-sided limits", 'calc/limit-1sided'),
                link("Inequality and limit", 'calc/limit-ineq'),
                link("Limit of vector", 'calc/limit-vector'),
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
                link("Derivative of vector", 'calc/derivative-vector'),
                link(r"Derivatives of $\sin$, $\cos$ and $\tan$", 'calc/derivative-trig'),
            ])),
            dropdown("Integral", join([
                link("Introduction to integrals", 'calc/integral-intro'),
                link("Refinement of partition", 'calc/integral-refinement'),
                link("Defining the integral", 'calc/integral-def'),
                link("Average", 'calc/integral-average'),
                link("Fundamental theorem of calculus, part 1", 'calc/integral-ftoc1'),
                link("Fundamental theorem of calculus, part 2", 'calc/integral-ftoc2'),
                link("More notation for integrals", 'calc/integral-notation'),
                link("Integral rules", 'calc/integral-rules'),
                link("U substitution", 'calc/integral-usub'),
                link("Volume of solid of revolution", 'calc/integral-sor-volume'),
                link("Area of surface of revolution", 'calc/integral-sor-area'),
            ])),
        ])),

        dropdown("Complex numbers", join([
            link("Introduction", 'complex/intro'),
            link("Angle and length", 'complex/angle-and-len'),
            link("Multiplication", 'complex/mul'),
            link("Division", 'complex/div'),
            link("Square root", 'complex/sqrt'),
            link("Derivative", 'complex/derivative'),
            link("Exponent function", 'complex/exp'),
        ])),
        dropdown("Linear algebra", join([
            dropdown("Vectors and matrices", join([
                link("Introduction (rotating a vector)", "linalg/rotating-intro"),
                link("Matrix times vector", "linalg/matrix-vector"),
                link("Matrix times matrix", "linalg/matrix-matrix"),
                link("Matrix plus matrix", "linalg/matrix-sum"),
                link("Matrix times number", "linalg/matrix-num"),
                link("Defining span and linear (in)dependence", "linalg/span-and-dep-defs"),
                link("Finding span and checking linear (in)dependence", "linalg/span-and-dep-finding"),
                link("Inverse matrices", "linalg/matrix-inverse"),
                link("Transpose", "linalg/transpose"),
                link("Finding inverse matrices", "linalg/inverse-finding"),
                link(r"$2 \times 2$ inverse formula", "linalg/inverse-2x2"),
            ])),
            dropdown("Determinants", join([
                link("Defining determinants", "linalg/det-def"),
                link("Permutations and transpositions", "linalg/det-swaps"),
                link("Calculating determinants with row operations", "linalg/det-row-ops"),
                link("Determinant of transpose", "linalg/det-transpose"),
                link("Determinant and matrix multiplication", "linalg/det-matmul"),
            ])),
            dropdown("Subspace and basis", join([
                link("Defining subspaces and comparing to spans", "linalg/subspace-def"),
                link("Basis", "linalg/subspace-basis"),
            ])),
        ])),
    ])


def get_head_extras(filename):
    result = r'''
    <link href="https://fonts.googleapis.com/css?family=Cabin|Quicksand" rel="stylesheet">

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

    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/tex-mml-chtml.js"></script>
    <script>
    MathJax = {
        tex: {
            inlineMath: [ ['$','$'] ],
            displayMath: [ ['$$','$$'] ],
            macros: {
                span: '\\operatorname{span}',
                rotate: '\\operatorname{rotate}',
                abs: [ "\\left| {#1} \\right|", 1 ],
                bigvec: [ "\\overrightarrow{#1}", 1 ],
                I: '\\vec{i}',
                J: '\\vec{j}',
                K: '\\vec{k}',
                T: '\\operatorname{T}',
                epsi: '\\varepsilon',
                // colors chosen so that they are distinguishable when together
                red: [ "{\\color{##c00}{#1}}", 1 ],
                blue: [ "{\\color{blue}{#1}}", 1 ],
                green: [ "{\\color{green}{#1}}", 1 ],
                magenta: [ "{\\color{magenta}{#1}}", 1 ],
                darkyellow: [ "{\\color{##ac5f00}{#1}}", 1 ],
            }
        }
    };
    </script>
    '''

    htmlfile = builder.infile2outfile(filename)
    relative_path_prefix = os.path.relpath(
        builder.outputdir, os.path.dirname(htmlfile)
    ).replace(os.sep, '/')

    for css_slash_something in sorted(glob.glob('css/*.css')):
        result += f'<link rel="stylesheet" href="{relative_path_prefix}/{css_slash_something}">\n'

    if filename == 'content/vectors/dot-projection.txt':
        result += f'''
        <script src="{relative_path_prefix}/js/vendor/three.js"></script>
        <script src="{relative_path_prefix}/js/common.js"></script>
        <script src="{relative_path_prefix}/js/projection-demo.js"></script>
        '''
    if filename == 'content/vectors/cross-def.txt':
        result += f'''
        <script src="{relative_path_prefix}/js/vendor/three.js"></script>
        <script src="{relative_path_prefix}/js/common.js"></script>
        <script src="{relative_path_prefix}/js/cross-product.js"></script>
        '''
    if filename in ('content/discrete/sums.txt', 'content/linalg/det-swaps.txt'):
        result += f'''
        <script src="{relative_path_prefix}/js/animator.js"></script>
        '''

    return result


builder.get_sidebar_content = get_sidebar_content
builder.get_head_extras = get_head_extras


# Avoid stripping quotes from titles ("Definition" of limit), add "Math Derivations" to end
def get_title(path):
    with open(path, "r") as file:
        return file.readline().strip().strip("#") + " - Math Derivations"

builder.get_title = get_title


# prevent htmlthingy from processing what's between $ or $$
@builder.converter.add_inliner(r' \$[^ ][^$\n]*?[^ ]\$[\s,\.]')
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

    if get_image(fullfilename) is None:
        with tempfile.TemporaryDirectory() as tmpdir:
            for file in glob.glob('asymptote/*.asy'):
                shutil.copy(file, tmpdir)

            with open(os.path.join(tmpdir, 'image.asy'), 'w') as file:
                file.write(fullcode)

            subprocess.check_call(
                ['asy', '-f', format, '--libgs=', 'image.asy'], cwd=tmpdir)
            put_image(os.path.join(tmpdir, 'image.' + format), fullfilename)

    if format == 'svg':
        # figure out the correct size (lol)
        attribs = xml.etree.ElementTree.parse(get_image(fullfilename)).getroot().attrib
        assert attribs['width'].endswith('pt')
        assert attribs['height'].endswith('pt')
        size = (float(attribs['width'][:-2]), float(attribs['height'][:-2]))
        extrainfo = 'width="%.0f" height="%.0f"' % size
    else:
        extrainfo = ''

    htmlfile = builder.infile2outfile(filename)
    relative = os.path.relpath(
        os.path.join(builder.outputdir, get_image(fullfilename)),
        os.path.dirname(htmlfile),
    )

    html = tags.image(relative.replace(os.sep, '/'), match.group(2))
    return html.replace('<img', '<img %s class="asymptote"' % extrainfo, 1)


@builder.converter.add_multiliner(r'^python:\n')
def python(match, filename):
    namespace = {}
    exec("def get_the_string():\n" + match.string[match.end():], namespace)
    return eval("get_the_string()", namespace)


@builder.converter.add_multiliner(r'^animation:(.*)\n')
def animation(match, filename):
    inline_css = match.group(1)
    javascript = match.string[match.end():]
    the_id = "animation-" + hashlib.md5(javascript.encode("utf-8")).hexdigest()
    # TODO: don't put script tags in middle of page, belongs to head
    return f'''
    <div id="{the_id}"></div>
    <script>
        document.addEventListener("DOMContentLoaded", () => {{
            function run() {{
                window.animator.run({json.dumps(the_id)}, {json.dumps(inline_css)}, ...arguments);
            }}
            {javascript}
        }});
    </script>
    '''


builder.run()

# tell github pages to do the right thing
open(os.path.join(builder.outputdir, '.nojekyll'), 'x').close()

parser = argparse.ArgumentParser()
parser.add_argument("--reload-browser", action='store_true')
parser.add_argument("--check-links", action='store_true')
args = parser.parse_args()

if args.reload_browser:
    # https://itectec.com/unixlinux/refresh-reload-active-browser-tab-from-command-line/
    subprocess.call('xdotool search --name "Math Derivations" windowactivate windowfocus key F5', shell=True)

if args.check_links:
    print("Checking links...")
    link_problems = check_links([(f, builder.infile2outfile(f)) for f in builder.infiles])
    if link_problems:
        print("=== link check errors ===")
        print("\n".join(link_problems))
        sys.exit(1)
