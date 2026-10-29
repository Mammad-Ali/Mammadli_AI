import html
import re

MAX_LEN = 3500  # telegram limit is 4096, leaving some room for emojis and closing ```

CODE_FENCE = re.compile(r'^\s*```\s*([\w+#.-]*)')
INLINE_CODE = re.compile(r'`([^`\n]+)`')
CODE_SLOT = re.compile(r'\x00(\d+)\x00')
HEADING = re.compile(r'^#{1,6}\s+(.+)$')
BULLET = re.compile(r'^(\s*)[*+-]\s+')
BOLD_ITALIC = re.compile(r'\*\*\*([^*<>\n]+?)\*\*\*')
BOLD = re.compile(r'\*\*([^<>\n]+?)\*\*')
ITALIC = re.compile(r'(?<![*\w])\*(?![\s*])([^*<>\n]+?)(?<!\s)\*(?![*\w])')
STRIKE = re.compile(r'~~([^<>\n]+?)~~')
LINK = re.compile(r'\[([^\]\n]+)\]\((https?://[^)\s"]+)\)')


def split_message(text, limit=MAX_LEN):
    parts = []
    current = ''
    code_block = None  # the ``` line that opened the code block we're in

    for line in text.split('\n'):
        closing = code_block and CODE_FENCE.match(line)
        chunks = [line[i:i + limit] for i in range(0, len(line), limit)] or ['']

        for chunk in chunks:
            if current and not closing and len(current) + len(chunk) + 1 > limit:
                # close the code block here and open it again in the next message
                if code_block:
                    current += '\n```'
                parts.append(current)
                current = code_block or ''
            current = current + '\n' + chunk if current else chunk

        if CODE_FENCE.match(line):
            code_block = None if code_block else line.strip()

    parts.append(current)
    return [p for p in parts if p.strip()] or [text]


def markdown_to_html(text):
    lines = []
    code = None
    lang = ''

    for line in text.split('\n'):
        fence = CODE_FENCE.match(line)
        if fence and code is None:
            code = []
            lang = fence.group(1)
        elif fence:
            lines.append(code_to_html(code, lang))
            code = None
        elif code is not None:
            code.append(line)
        else:
            lines.append(format_line(line))

    # code block was never closed
    if code is not None:
        lines.append(code_to_html(code, lang))

    return '\n'.join(lines)


def code_to_html(code, lang):
    code = html.escape('\n'.join(code), quote=False)
    if lang:
        return f'<pre><code class="language-{lang}">{code}</code></pre>'
    return f'<pre>{code}</pre>'


def format_line(line):
    # take out `inline code` first so bold/italic don't touch it
    codes = []

    def save_code(m):
        codes.append(m.group(1))
        return f'\x00{len(codes) - 1}\x00'

    line = INLINE_CODE.sub(save_code, line)
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

    # put the inline code back
    return CODE_SLOT.sub(lambda m: '<code>' + html.escape(codes[int(m.group(1))], quote=False) + '</code>', line)
