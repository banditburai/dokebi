from fasthtml.common import *
from fasthtml.svg import *
import pypdf
import io
from functools import partial

fouc_script = Script("""
(function() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = savedTheme || (prefersDark ? 'night' : 'retro');
    document.documentElement.setAttribute('data-theme', theme);
})();
""")
tailwindLink = Link(rel="stylesheet", href="assets/output.css", type="text/css")
interactLink = Script(src="https://cdn.jsdelivr.net/npm/interactjs/dist/interact.min.js")
daisyLink = Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css")

app, rt = fast_app(
    pico=False,    
    hdrs=(fouc_script, tailwindLink, daisyLink, interactLink),
    htmlkw=dict(data_theme="retro") 
)


# ----------------------------------------------------------------------
# Navbar and Theme toggle
# ----------------------------------------------------------------------

MENU_ITEMS = [
    ('Home', '/'),
    ('PDF to SVG', '/pdf-to-svg'),
    ('About', '/about'),
]

NAVBAR_ICON_PATH = 'M4 6h16M4 12h16M4 18h7'
SEARCH_ICON_PATH = 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z'

def create_svg_icon(path, cls='h-5 w-5'):
    return Svg(
        Path(stroke_linecap='round', stroke_linejoin='round', stroke_width='2', d=path),
        fill='none',
        viewBox='0 0 24 24',
        stroke='currentColor',
        cls=cls
    )

def create_menu_items(items):
    return [Li(A(text, href=link)) for text, link in items]

def create_navbar():
    NavbarSection = partial(Div, cls='navbar-start')
    NavbarCenter = partial(Div, cls='navbar-center')
    NavbarEnd = partial(Div, cls='navbar-end')

    return Div(
        NavbarSection(
            Div(
                Div(
                    create_svg_icon(NAVBAR_ICON_PATH),
                    tabindex='0',
                    role='button',
                    cls='btn btn-ghost btn-circle'
                ),
                Ul(
                    *create_menu_items(MENU_ITEMS),
                    tabindex='0',
                    cls='menu menu-sm dropdown-content bg-base-100 rounded-box z-[1] mt-3 w-52 p-2 shadow'
                ),
                cls='dropdown'
            )
        ),
        NavbarCenter(
            A('PDF Tools', cls='btn btn-ghost text-xl', href='/')
        ),
        NavbarEnd(
            Button(
                create_svg_icon(SEARCH_ICON_PATH),
                cls='btn btn-ghost btn-circle'
            ),
            theme_toggle()
        ),
        cls='navbar bg-base-200'
    )
def theme_toggle():
    theme_checkbox = Input(
        type='checkbox',
        value='night',
        cls='theme-controller',
        id='theme-toggle'      
        )  

    return Label(
        theme_checkbox,       
       Svg(
        Path(d='M5.64,17l-.71.71a1,1,0,0,0,0,1.41,1,1,0,0,0,1.41,0l.71-.71A1,1,0,0,0,5.64,17ZM5,12a1,1,0,0,0-1-1H3a1,1,0,0,0,0,2H4A1,1,0,0,0,5,12Zm7-7a1,1,0,0,0,1-1V3a1,1,0,0,0-2,0V4A1,1,0,0,0,12,5ZM5.64,7.05a1,1,0,0,0,.7.29,1,1,0,0,0,.71-.29,1,1,0,0,0,0-1.41l-.71-.71A1,1,0,0,0,4.93,6.34Zm12,.29a1,1,0,0,0,.7-.29l.71-.71a1,1,0,1,0-1.41-1.41L17,5.64a1,1,0,0,0,0,1.41A1,1,0,0,0,17.66,7.34ZM21,11H20a1,1,0,0,0,0,2h1a1,1,0,0,0,0-2Zm-9,8a1,1,0,0,0-1,1v1a1,1,0,0,0,2,0V20A1,1,0,0,0,12,19ZM18.36,17A1,1,0,0,0,17,18.36l.71.71a1,1,0,0,0,1.41,0,1,1,0,0,0,0-1.41ZM12,6.5A5.5,5.5,0,1,0,17.5,12,5.51,5.51,0,0,0,12,6.5Zm0,9A3.5,3.5,0,1,1,15.5,12,3.5,3.5,0,0,1,12,15.5Z'),    
        viewbox='0 0 24 24',
        cls='swap-on h-8 w-8 fill-current'
    ),    
        Svg(
    Path(d='M21.64,13a1,1,0,0,0-1.05-.14,8.05,8.05,0,0,1-3.37.73A8.15,8.15,0,0,1,9.08,5.49a8.59,8.59,0,0,1,.25-2A1,1,0,0,0,8,2.36,10.14,10.14,0,1,0,22,14.05,1,1,0,0,0,21.64,13Zm-9.5,6.69A8.14,8.14,0,0,1,7.08,5.22v.27A10.15,10.15,0,0,0,17.22,15.63a9.79,9.79,0,0,0,2.1-.22A8.11,8.11,0,0,1,12.14,19.73Z'),    
    viewbox='0 0 24 24',
    cls='swap-off h-8 w-8 fill-current'
),       
        cls='text-accent swap swap-rotate '
    )

theme_toggle_script = Script("""
document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;

    function updateTheme(isDark) {
        html.setAttribute('data-theme', isDark ? 'night' : 'retro');
        localStorage.setItem('theme', isDark ? 'night' : 'retro');
        themeToggle.checked = isDark;
    }

    // Set initial theme
    const savedTheme = localStorage.getItem('theme');
    updateTheme(savedTheme === 'night');

    // Listen for toggle changes
    themeToggle.addEventListener('change', function() {
        updateTheme(this.checked);
    });
});
""")

# ----------------------------------------------------------------------
# Temporary fix for PathFT
# ----------------------------------------------------------------------
class ExtendedPathFT(PathFT):
    def l(self, x, y):
        "Relative line to."
        return self._append_cmd(f'l{x} {y}')

    def m(self, dx, dy):
        "Relative move to."
        return self._append_cmd(f'm{dx} {dy}')

    def c(self, dx1, dy1, dx2, dy2, dx, dy):
        "Relative cubic Bézier curve."
        return self._append_cmd(f'c{dx1} {dy1} {dx2} {dy2} {dx} {dy}')

    def s(self, dx2, dy2, dx, dy):
        "Relative smooth cubic Bézier curve."
        return self._append_cmd(f's{dx2} {dy2} {dx} {dy}')

    def q(self, dx1, dy1, dx, dy):
        "Relative quadratic Bézier curve."
        return self._append_cmd(f'q{dx1} {dy1} {dx} {dy}')

    def t(self, dx, dy):
        "Relative smooth quadratic Bézier curve."
        return self._append_cmd(f't{dx} {dy}')

    def a(self, rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, dx, dy):
        "Relative elliptical arc."
        return self._append_cmd(f'a{rx} {ry} {x_axis_rotation} {large_arc_flag} {sweep_flag} {dx} {dy}')

    def h(self, dx):
        "Relative horizontal line to."
        return self._append_cmd(f'h{dx}')

    def v(self, dy):
        "Relative vertical line to."
        return self._append_cmd(f'v{dy}')
    
# Override the original Path function with our extended version
def Path(*args, **kwargs):
    kwargs['ft_cls'] = ExtendedPathFT
    return ft_svg('path', *args, **kwargs)

# ----------------------------------------------------------------------
# Main route
# ----------------------------------------------------------------------
def layout(content):
    return Div(
    create_navbar(),
    Div(content, id="content", cls="container mx-auto p-4"),
    cls="min-h-screen"
    )

@rt('/')
def get_index():
    return layout(
    Div(
H1("PDF Tools", cls="text-3xl font-bold mb-4"),
P("Welcome to PDF Tools. Choose an option from the menu.", cls="mb-4"),
cls="text-center"
)
)

@rt('/pdf-to-svg')
def get():
    return layout(
    Div(
    H1("PDF to SVG Converter", cls="text-3xl font-bold mb-4"),
    Form(
    Input(type="file", name="pdf_file", accept=".pdf", cls="file-input file-input-bordered w-full max-w-xs"),
    Button("Upload and Convert", type="submit", cls="btn btn-primary mt-2"),
    action="/convert",
    method="POST",
    enctype="multipart/form-data",
    cls="mb-4"
    ),
    Div(id="svg-content"),
    cls="text-center"
    )
)

@rt('/about')
def get():
    return layout(
    Div(
H1("About PDF Tools", cls="text-3xl font-bold mb-4"),
P("PDF Tools is a web application for working with PDF files.", cls="mb-4"),
cls="text-center"
)
)
@rt('/convert')
def post(pdf_file):    
    return "SVG content"
    
def is_htmx(request):
    return request.headers.get('HX-Request') == 'true'

serve()
