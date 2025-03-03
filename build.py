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
from asciimath_to_mathml import asciimath_to_mathml, MathSyntaxError


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
                link("Definition of limit", 'calc/limit-def'),
                link("Uniqueness", 'calc/limit-unique'),
                link("Limit of sum", 'calc/limit-sum'),
                link("Limit of product", 'calc/limit-product'),
                link("Limit of difference", 'calc/limit-diff'),
                link("Limit of division", 'calc/limit-div'),
                link("One-sided limits", 'calc/limit-1sided'),
                link("Inequality and limit", 'calc/limit-ineq'),
                link("Limit of vector", 'calc/limit-vector'),
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


USES_OLD_MATH = [
    "content/analytic-plane-geometry/angle-between-lines.txt",
    "content/analytic-plane-geometry/distance-line-point.txt",
    "content/analytic-plane-geometry/line-eq-determinant.txt",
    "content/analytic-plane-geometry/line-eq-normal.txt",
    "content/analytic-plane-geometry/line-eq-slope-and-point.txt",
    "content/analytic-plane-geometry/line-eq-slope.txt",
    "content/analytic-plane-geometry/parabola.txt",
    "content/analytic-plane-geometry/reflect.txt",
    "content/analytic-plane-geometry/shift.txt",
    "content/analytic-plane-geometry/slope-tan.txt",
    "content/analytic-plane-geometry/stretch.txt",
    "content/analytic-plane-geometry/why-its-hyperbola.txt",
    "content/calc/cont-def.txt",
    "content/calc/cont-props.txt",
    "content/calc/derivative-basic-rules.txt",
    "content/calc/derivative-chain-rule.txt",
#    "content/calc/derivative-def.txt",
    "content/calc/derivative-notation.txt",
    "content/calc/derivative-power-rule-1.txt",
    "content/calc/derivative-power-rule-2.txt",
    "content/calc/derivative-product-quotient-rules.txt",
    "content/calc/derivative-trig.txt",
    "content/calc/derivative-vector.txt",
    "content/calc/integral-average.txt",
    "content/calc/integral-def.txt",
    "content/calc/integral-ftoc1.txt",
    "content/calc/integral-ftoc2.txt",
    "content/calc/integral-intro.txt",
    "content/calc/integral-notation.txt",
    "content/calc/integral-refinement.txt",
    "content/calc/integral-rules.txt",
    "content/calc/integral-sor-area.txt",
    "content/calc/integral-sor-volume.txt",
    "content/calc/integral-usub.txt",
    "content/calc/limit-1sided.txt",
    "content/calc/limit-def.txt",
    "content/calc/limit-diff.txt",
    "content/calc/limit-div.txt",
    "content/calc/limit-ineq.txt",
    "content/calc/limit-intro.txt",
    "content/calc/limit-product.txt",
    "content/calc/limit-sum.txt",
    "content/calc/limit-unique.txt",
    "content/calc/limit-vector.txt",
    "content/complex/angle-and-len.txt",
    "content/complex/derivative.txt",
    "content/complex/div.txt",
    "content/complex/exp.txt",
    "content/complex/intro.txt",
    "content/complex/mul.txt",
    "content/complex/sqrt.txt",
    "content/discrete/binom.txt",
    "content/discrete/sums.txt",
    "content/eqs-and-funcs/how-equations-work.txt",
    "content/eqs-and-funcs/how-inequations-work.txt",
    "content/eqs-and-funcs/incdec-funcs.txt",
    "content/eqs-and-funcs/inverse-funcs.txt",
    "content/index.txt",
    "content/linalg/det-def.txt",
    "content/linalg/det-matmul.txt",
    "content/linalg/det-row-ops.txt",
    "content/linalg/det-sub.txt",
    "content/linalg/det-swaps.txt",
    "content/linalg/det-transpose.txt",
    "content/linalg/inverse-2x2.txt",
    "content/linalg/inverse-finding.txt",
    "content/linalg/matrix-inverse.txt",
    "content/linalg/matrix-matrix.txt",
    "content/linalg/matrix-num.txt",
    "content/linalg/matrix-sum.txt",
    "content/linalg/matrix-vector.txt",
    "content/linalg/rotating-intro.txt",
    "content/linalg/span-and-dep-defs.txt",
    "content/linalg/span-and-dep-finding.txt",
    "content/linalg/subspace-basis.txt",
    "content/linalg/subspace-def.txt",
    "content/linalg/transpose.txt",
    "content/plane-geometry/inscribed-angle-theorem.txt",
    "content/plane-geometry/inscribed-circle.txt",
    "content/plane-geometry/law-of-cosines.txt",
    "content/plane-geometry/law-of-sines.txt",
    "content/vectors/angle-between-vectors.txt",
    "content/vectors/cross-def.txt",
    "content/vectors/dot-projection.txt",
    "content/vectors/iwi-jwj.txt",
]


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
    '''

    if filename in USES_OLD_MATH:
        result += r'''
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
def old_math_handler(match, filename):
    return match.group(0)


@builder.converter.add_multiliner(r'^math:\n')
def big_math(match, filename):
    the_math = match.string[match.end():]
    try:
        return "<div class='math-centering-wrapper'>" + asciimath_to_mathml(the_math, inline=False) + "</div>"
    except MathSyntaxError as e:
        sys.exit(f"math syntax error in {filename}: {e}")


@builder.converter.add_inliner(r'`.+?`')
def inline_math(match, filename):
    the_math = match.group(0).strip('`')
    try:
        return asciimath_to_mathml(the_math, inline=True)
    except MathSyntaxError as e:
        sys.exit(f"math syntax error in {filename}: {e}")


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
