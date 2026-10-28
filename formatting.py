import html
import re

# Telegram allows 4096 characters per message. We stay well below that,
# because emoji count as 2 characters and closing a code block adds a few more.
MAX_PART_LENGTH = 3500

FENCE = re.compile(r'^\s*```\s*([\w+#.-]*)')
INLINE_CODE = re.compile(r'`([^`\n]+)`')
PLACEHOLDER = re.compile(r'\x00(\d+)\x00')
HEADING = re.compile(r'^#{1,6}\s+(.+)$')
BULLET = re.compile(r'^(\s*)[*+-]\s+')
BOLD_ITALIC = re.compile(r'\*\*\*([^*<>\n]+?)\*\*\*')
BOLD = re.compile(r'\*\*([^<>\n]+?)\*\*')
ITALIC = re.compile(r'(?<![*\w])\*(?![\s*])([^*<>\n]+?)(?<!\s)\*(?![*\w])')
STRIKE = re.compile(r'~~([^<>\n]+?)~~')
LINK = re.compile(r'\[([^\]\n]+)\]\((https?://[^)\s"]+)\)')


def split_message(text, limit=MAX_PART_LENGTH):
    """Split a long reply into parts that each fit in one Telegram message.

    If a code block gets cut in the middle, it is closed at the end of one part
    and opened again at the start of the next, so every part looks right on its own.
    """
    parts = []
    current = ''
    fence = None  # the line that opened the code block we are inside, if any

    for line in text.split('\n'):
        closes_block = fence is not None and FENCE.match(line)
        # A single line longer than the limit is cut into pieces
        pieces = [line[i:i + limit] for i in range(0, len(line), limit)] or ['']

        for piece in pieces:
            if current and not closes_block and len(current) + len(piece) + 1 > limit:
                if fence:
                    current += '\n```'
                parts.append(current)
                current = fence or ''
            current = current + '\n' + piece if current else piece

        if FENCE.match(line):
            fence = None if fence else line.strip()

    parts.append(current)
    parts = [part for part in parts if part.strip()]
    return parts or [text]


def markdown_to_html(text):
    """Convert the Markdown that Gemini writes into the HTML that Telegram understands."""
    result = []
    code_lines = None  # lines of the code block we are inside, if any
    language = ''

    for line in text.split('\n'):
        fence = FENCE.match(line)
        if fence:
            if code_lines is None:
                code_lines = []
                language = fence.group(1)
            else:
                result.append(_code_block(code_lines, language))
                code_lines = None
        elif code_lines is not None:
            code_lines.append(line)
        else:
            result.append(_format_line(line))

    # The reply ended without closing its code block
    if code_lines is not None:
        result.append(_code_block(code_lines, language))

    return '\n'.join(result)


def _code_block(lines, language):
    code = html.escape('\n'.join(lines), quote=False)
    if language:
        return f'<pre><code class="language-{language}">{code}</code></pre>'
    return f'<pre>{code}</pre>'


def _format_line(line):
    # Hide `inline code` first, so the bold/italic rules don't touch what is inside it
    codes = []

    def hide_code(match):
        codes.append(match.group(1))
        return f'\x00{len(codes) - 1}\x00'

    line = INLINE_CODE.sub(hide_code, line)
    line = html.escape(line, quote=False)

    heading = HEADING.match(line)
    if heading:
        line = heading.group(1).replace('**', '')
    else:
        line = BULLET.sub(r'\1• ', line)

    line = BOLD_ITALIC.sub(r'<b><i>\1</i></b>', line)
    line = BOLD.sub(r'<b>\1</b>', line)
    line = ITALIC.sub(r'<i>\1</i>', line)
    line = STRIKE.sub(r'<s>\1</s>', line)
    line = LINK.sub(r'<a href="\2">\1</a>', line)

    if heading:
        line = f'<b>{line}</b>'

    return PLACEHOLDER.sub(
        lambda match: f'<code>{html.escape(codes[int(match.group(1))], quote=False)}</code>',
        line,
    )
