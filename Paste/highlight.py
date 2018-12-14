import misaka
from django.template.defaultfilters import escape
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.lexers.python import PythonLexer
from pygments.util import ClassNotFound
from docutils.core import publish_parts
from pygments_lexer_solidity import SolidityLexer


class NakedHtmlFormatter(HtmlFormatter):
    def wrap(self, source, outfile):
        return self._wrap_code(source)

    def _wrap_code(self, source):
        for i, t in source:
            yield i, t


def pygmentize(code_string, lexer_name='_code'):
    if lexer_name == '_code':
        return '\n'.join(
            [
                '<span class="plain">{}</span>'.format(escape(l) or '&#8203;')
                for l in code_string.splitlines()
            ]
        )
    if lexer_name == '_text':
        pass
    if lexer_name == '_markdown':
        extensions = (
            'tables',
            'fenced-code',
            'footnotes',
            'autolink,',
            'strikethrough',
            'underline',
            'quote',
            'superscript',
            'math',
            'math-explicit',
        )
        render_flags = ('skip-html',)
        return mark_safe(
            misaka.html(
                code_string, extensions=extensions, render_flags=render_flags
            )
        )
    if lexer_name == '_rst':
        rst_part_name = 'html_body'
        publish_args = {
            'writer_name': 'html5_polyglot',
            'settings_overrides': {
                'raw_enabled': False,
                'file_insertion_enabled': False,
                'halt_level': 5,
                'report_level': 2,
                'warning_stream': '/dev/null',
            },
        }

        publish_args['source'] = code_string
        parts = publish_parts(**publish_args)
        return mark_safe(parts[rst_part_name])
    if lexer_name == 'solidity':
        return SolidityLexer()

    lexer = None
    try:
        lexer = get_lexer_by_name(lexer_name)
    except ClassNotFound as e:
        pass

    if not lexer:
        lexer = PythonLexer()

    formatter = NakedHtmlFormatter()

    return highlight(code_string, lexer, formatter)


def TEXT_FORMATTER():
    return [
        ('_text', 'Plain Text'),
        ('_markdown', 'Markdown'),
        ('_rst', 'reStructuredText'),
    ]


def CODE_FORMATTER():
    return [
        ('_code', 'Plain Code'),
        ('abap', 'ABAP'),
        ('apacheconf', 'ApacheConf'),
        ('applescript', 'AppleScript'),
        ('as', 'ActionScript'),
        ('bash', 'Bash'),
        ('bbcode', 'BBCode'),
        ('c', 'C'),
        ('cpp', 'C++'),
        ('csharp', 'C#'),
        ('clojure', 'Clojure'),
        ('cobol', 'COBOL'),
        ('css', 'CSS'),
        ('cuda', 'CUDA'),
        ('dart', 'Dart'),
        ('delphi', 'Delphi'),
        ('diff', 'Diff'),
        ('django', 'Django'),
        ('erlang', 'Erlang'),
        ('fortran', 'Fortran'),
        ('go', 'Go'),
        ('groovy', 'Groovy'),
        ('haml', 'Haml'),
        ('haskell', 'Haskell'),
        ('html', 'HTML'),
        ('http', 'HTTP'),
        ('ini', 'INI'),
        ('irc', 'IRC'),
        ('java', 'Java'),
        ('js', 'JavaScript'),
        ('json', 'JSON'),
        ('lua', 'Lua'),
        ('make', 'Makefile'),
        ('mako', 'Mako'),
        ('mason', 'Mason'),
        ('matlab', 'Matlab'),
        ('modula2', 'Modula'),
        ('monkey', 'Monkey'),
        ('mysql', 'MySQL'),
        ('numpy', 'NumPy'),
        ('objc', 'Obj-C'),
        ('ocaml', 'OCaml'),
        ('perl', 'Perl'),
        ('php', 'PHP'),
        ('postscript', 'PostScript'),
        ('powershell', 'PowerShell'),
        ('prolog', 'Prolog'),
        ('properties', 'Properties'),
        ('puppet', 'Puppet'),
        ('python', 'Python'),
        ('r', 'R'),
        ('rb', 'Ruby'),
        ('rst', 'reStructuredText'),
        ('rust', 'Rust'),
        ('sass', 'Sass'),
        ('scala', 'Scala'),
        ('scheme', 'Scheme'),
        ('scilab', 'Scilab'),
        ('scss', 'SCSS'),
        ('smalltalk', 'Smalltalk'),
        ('smarty', 'Smarty'),
        ('solidity', 'Solidity'),
        ('sql', 'SQL'),
        ('tcl', 'Tcl'),
        ('tcsh', 'Tcsh'),
        ('tex', 'TeX'),
        ('vb.net', 'VB.net'),
        ('vim', 'VimL'),
        ('xml', 'XML'),
        ('xquery', 'XQuery'),
        ('xslt', 'XSLT'),
        ('yaml', 'YAML'),
    ]


# ---------------------------------------------------
# ---------------------------------------------------

LEXER_CHOICES = (
    ('Metin', [i[:2] for i in TEXT_FORMATTER()]),
    ('Kod', [i[:2] for i in CODE_FORMATTER()]),
)

LEXER_KEYS = [i[0] for i in TEXT_FORMATTER()] + [
    i[0] for i in CODE_FORMATTER()
]
