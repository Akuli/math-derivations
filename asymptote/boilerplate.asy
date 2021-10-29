// just for convenience in other files
import graph;

void define_tex_color(string name, pen asy_color) {
    texpreamble("\definecolor{" + name + "}{rgb}{" +
        string(colors(asy_color)[0])
        + "," +
        string(colors(asy_color)[1])
        + "," +
        string(colors(asy_color)[2])
    + "}");
    texpreamble("\newcommand{" + '\\' + name + "}[1]{{ \color{" + name + "}{#1} }}");
}

texpreamble("\usepackage[dvipsnames]{xcolor}");
texpreamble("\newcommand{\Vec}[1]{\overrightarrow{#1}}");
texpreamble("\newcommand{\I}{\vec i}");
texpreamble("\newcommand{\J}{\vec j}");
texpreamble("\newcommand{\K}{\vec k}");
texpreamble("\newcommand{\abs}[1]{\left| {#1} \right|}");
texpreamble("\newcommand{\epsi}{\varepsilon}");
define_tex_color("blue", blue);
define_tex_color("red", deepred);
define_tex_color("green", deepgreen);

// TODO: stop using a weird mixture of mm and raw numbers?
defaultpen(0.8mm + fontsize(25pt));
pen dotpen = defaultpen() + 0.3cm;
pen smalldashes = linetype(new real[] {4, 4});
pen darkorange = rgb(0.9,0.4,0);
real vectorarrowsize = 0.7cm;

path brace_with_space(pair a, pair b, real distance) {
    pair offset = (b-a) / length(b-a) * (0,1) * distance;
    return brace(a+offset, b+offset);
}

void grid(real xmin, real xmax, real ymin, real ymax) {
    pen thingray = defaultpen() + 1pt + gray;
    for (real x = xmin; x <= xmax; x+=1)
        draw((x,ymin-0.5)--(x,ymax+0.5), thingray);
    for (real y = ymin; y <= ymax; y+=1)
        draw((xmin-0.5,y)--(xmax+0.5,y), thingray);
}

void axises(real xmin, real xmax, real ymin, real ymax,
            string xlabel="$x$", string ylabel="$y$",
            pen xpen=defaultpen(), pen ypen=defaultpen(),
            transform T=shift(0,0)) {
    // TODO: come up with a nice way to add numbers along the axises
    // TODO: make labels work with latest asymptote version
    if (xmin != 0 || xmax != 0) {
        draw(T*( (xmin,0)--(xmax,0) ), p=xpen, arrow=Arrow(size=0.7cm));
        //label(T*(xmax,0), p=xpen, L=xlabel, align=E);
    }
    if (ymin != 0 || ymax != 0) {
        draw(T*( (0,ymin)--(0,ymax) ), p=ypen, arrow=Arrow(size=0.7cm));
        //label(T*(0,ymax), p=ypen, L=ylabel, align=(ymin < ymax ? NE : SE));
    }
}

/*
               ,|\
             ,' | \
           ,'   |  \
      3  ,'     |   \
       ,'     b |    \  2
     ,'         |     \
   ,'           |      \
 ,'     a       |  4-a  \
'-------------------------
            4

Pythagorean Theorem:  a^2 + b^2 = 3^2  and  (4-a)^2 + b^2 = 2^2

>>> from sympy import *
>>> a,b = symbols('a b')
>>> solve([Eq(a**2 + b**2, 3**2), Eq((4-a)**2 + b**2, 2**2)], a,b)
[(21/8, -3*sqrt(15)/8), (21/8, 3*sqrt(15)/8)]

this returns { cyclic, vertical_line, line2, line3, line4 }
*/
path[] triangle234 = {
    (4,0)--(21/8,3*sqrt(15)/8)--(0,0)--cycle,
    (21/8,0)--(21/8,3*sqrt(15)/8),
    (4,0)--(21/8,3*sqrt(15)/8),
    (21/8,3*sqrt(15)/8)--(0,0),
    (0,0)--(4,0)
};

// arc with radians
path rarc(pair c, real r, real angle1, real angle2) { return arc(c, r, degrees(angle1), degrees(angle2)); }

// rotate with radians
transform rrotate(real angle) { return rotate(degrees(angle)); }
transform rrotate(real angle, pair z) { return rotate(degrees(angle), z); }

pair cis(real angle) {
    return (cos(angle), sin(angle));
}

// from python
real e = 2.718281828459045;

void filldrawlabel(path p, pen fillpen, Label L) {
    filldraw(p, fillpen);
    label(L, (min(p) + max(p))/2);
}
