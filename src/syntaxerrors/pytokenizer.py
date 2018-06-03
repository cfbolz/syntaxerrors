import six

from syntaxerrors import automata
from syntaxerrors.parser import Token
from syntaxerrors.pytoken import python_opmap_bytes
from syntaxerrors.pytoken import tokens
from syntaxerrors.error import TokenError, TokenIndentationError
from syntaxerrors.pytokenize import tabsize, whiteSpaceDFA, \
    triple_quoted, endDFAs, single_quoted, pseudoDFA
from syntaxerrors import astconsts

NAMECHARS = b'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
NUMCHARS = b'0123456789'
ALNUMCHARS = NAMECHARS + NUMCHARS
EXTENDED_ALNUMCHARS = ALNUMCHARS + b'-.'
WHITESPACES = b' \t\n\r\v\f'

def indexbyte(b, pos):
    assert isinstance(b, bytes)
    return six.int2byte(six.indexbytes(b, pos))

def match_encoding_declaration(comment):
    """returns the declared encoding or None

    This function is a replacement for :
    >>> py_encoding = re.compile(r"coding[:=]\s*([-\w.]+)")
    >>> py_encoding.search(comment)
    """
    index = comment.find(b'coding')
    if index < 0:
        return None
    next_char = comment[index + 6]
    if next_char not in ':=':
        return None
    end_of_decl = comment[index + 7:]
    index = 0
    for char in end_of_decl:
        if char not in WHITESPACES:
            break
        index += 1
    else:
        return None
    encoding = ''
    for char in end_of_decl[index:]:
        if char in EXTENDED_ALNUMCHARS:
            encoding += char
        else:
            break
    if encoding != '':
        return encoding
    return None


DUMMY_DFA = automata.DFA([], [])

def token_decode(token_type, value, lineno, column, line):
    return Token(
            token_type,
            value.decode("utf-8"), lineno, column,
            line)


def generate_tokens(lines, flags):
    """
    This is a rewrite of pypy.module.parser.pytokenize.generate_tokens since
    the original function is not RPYTHON (uses yield)
    It was also slightly modified to generate Token instances instead
    of the original 5-tuples -- it's now a 4-tuple of

    * the Token instance
    * the whole line as a string
    * the line number (the real one, counting continuation lines)
    * the position on the line of the end of the token.

    Original docstring ::

        The generate_tokens() generator requires one argment, readline, which
        must be a callable object which provides the same interface as the
        readline() method of built-in file objects. Each call to the function
        should return one line of input as a string.

        The generator produces 5-tuples with these members: the token type; the
        token string; a 2-tuple (srow, scol) of ints specifying the row and
        column where the token begins in the source; a 2-tuple (erow, ecol) of
        ints specifying the row and column where the token ends in the source;
        and the line on which the token was found. The line passed is the
        logical line; continuation lines are included.
    """
    token_list = []
    lnum = continued = 0
    namechars = NAMECHARS
    numchars = NUMCHARS
    contstr, needcont = '', 0
    contline = None
    indents = [0]
    last_comment = b''
    parenstack = []

    # make the annotator happy
    endDFA = DUMMY_DFA
    # make the annotator happy
    line = ''
    pos = 0
    lines.append(b"")
    strstart = (0, 0, "")
    for line in lines:
        assert isinstance(line, bytes)
        lnum = lnum + 1
        line = universal_newline(line)
        assert isinstance(line, bytes)
        pos, max = 0, len(line)
        uni_line = line.decode("utf-8")

        if contstr:
            if not line:
                raise TokenError(
                    "end of file (EOF) while scanning triple-quoted string literal",
                    strstart[2], strstart[0], strstart[1]+1,
                    token_list, lnum-1)
            endmatch = endDFA.recognize(line)
            if endmatch >= 0:
                pos = end = endmatch
                tok = token_decode(tokens.STRING, contstr + line[:end], strstart[0],
                       strstart[1], uni_line)
                token_list.append(tok)
                last_comment = b''
                contstr, needcont = '', 0
                contline = None
            elif (needcont and not line.endswith(b'\\\n') and
                               not line.endswith(b'\\\r\n')):
                tok = token_decode(tokens.ERRORTOKEN, contstr + line, strstart[0],
                       strstart[1], uni_line)
                token_list.append(tok)
                last_comment = b''
                contstr = ''
                contline = None
                continue
            else:
                contstr = contstr + line
                contline = contline + line
                continue

        elif not parenstack and not continued:  # new statement
            if not line: break
            column = 0
            while pos < max:                   # measure leading whitespace
                if indexbyte(line, pos) == b' ': column = column + 1
                elif indexbyte(line, pos) == b'\t': column = (column/tabsize + 1)*tabsize
                elif indexbyte(line, pos) == b'\f': column = 0
                else: break
                pos = pos + 1
            if pos == max: break

            if indexbyte(line, pos) in b'#\r\n':
                # skip comments or blank lines
                continue

            if column > indents[-1]:           # count indents or dedents
                indents.append(column)
                token_list.append(token_decode(tokens.INDENT, line[:pos], lnum, 0, uni_line))
                last_comment = b''
            while column < indents[-1]:
                indents.pop()
                token_list.append(token_decode(tokens.DEDENT, b'', lnum, pos, uni_line))
                last_comment = b''
            if column != indents[-1]:
                err = "unindent does not match any outer indentation level"
                raise TokenIndentationError(err, line, lnum, column+1, token_list)

        else:                                  # continued statement
            if not line:
                if parenstack:
                    _, lnum1, start1, line1 = parenstack[0]
                    raise TokenError("parenthesis is never closed", line1,
                                     lnum1, start1 + 1, token_list, lnum)
                raise TokenError("end of file (EOF) in multi-line statement", line,
                                 lnum, 0, token_list) # XXX why is the offset 0 here?
            continued = 0

        while pos < max:
            pseudomatch = pseudoDFA.recognize(line, pos)
            if pseudomatch >= 0:                            # scan for tokens
                # JDR: Modified
                start = whiteSpaceDFA.recognize(line, pos)
                if start < 0:
                    start = pos
                end = pseudomatch

                if start == end:
                    raise TokenError("Unknown character", line,
                                     lnum, start + 1, token_list)

                pos = end
                token, initial = line[start:end], indexbyte(line, start)
                if initial in numchars or \
                   (initial == b'.' and token != b'.'):      # ordinary number
                    token_list.append(token_decode(tokens.NUMBER, token, lnum, start, uni_line))
                    last_comment = b''
                elif initial in b'\r\n':
                    if not parenstack:
                        tok = token_decode(tokens.NEWLINE, last_comment, lnum, start, uni_line)
                        token_list.append(tok)
                    last_comment = b''
                elif initial == b'#':
                    # skip comment
                    last_comment = token
                elif token in triple_quoted:
                    endDFA = endDFAs[token]
                    endmatch = endDFA.recognize(line, pos)
                    if endmatch >= 0:                     # all on one line
                        pos = endmatch
                        token = line[start:pos]
                        tok = token_decode(tokens.STRING, token, lnum, start, uni_line)
                        token_list.append(tok)
                        last_comment = b''
                    else:
                        strstart = (lnum, start, line)
                        contstr = line[start:]
                        contline = line
                        break
                elif initial in single_quoted or \
                    token[:2] in single_quoted or \
                    token[:3] in single_quoted:
                    if indexbyte(token, -1) == b'\n':                  # continued string
                        strstart = (lnum, start, line)
                        endDFA = (endDFAs[initial] or endDFAs[token[1]] or
                                   endDFAs[token[2]])
                        contstr, needcont = line[start:], 1
                        contline = line
                        break
                    else:                                  # ordinary string
                        tok = token_decode(tokens.STRING, token, lnum, start, uni_line)
                        token_list.append(tok)
                        last_comment = b''
                elif initial in namechars:                 # ordinary name
                    token_list.append(token_decode(tokens.NAME, token, lnum, start, uni_line))
                    last_comment = b''
                elif initial == b'\\':                      # continued stmt
                    continued = 1
                else:
                    if initial in b'([{':
                        parenstack.append((initial, lnum, start, line))
                    elif initial in b')]}':
                        if not parenstack:
                            raise TokenError("unmatched '%s'" % initial.decode("utf-8"), line,
                                             lnum, start + 1, token_list)
                        opening, lnum1, start1, line1 = parenstack.pop()
                        if not ((opening == b"(" and initial == b")") or
                                (opening == b"[" and initial == b"]") or
                                (opening == b"{" and initial == b"}")):
                            msg = "closing parenthesis '%s' does not match opening parenthesis '%s'" % (
                                        initial.decode("utf-8"), opening.decode("utf-8"))

                            if lnum1 != lnum:
                                msg += " on line " + str(lnum1)
                            raise TokenError(
                                    msg, line, lnum, start + 1, token_list)
                    if token in python_opmap_bytes:
                        punct = python_opmap_bytes[token]
                    else:
                        punct = tokens.OP
                    token_list.append(token_decode(punct, token, lnum, start, uni_line))
                    last_comment = b''
            else:
                start = whiteSpaceDFA.recognize(line, pos)
                if start < 0:
                    start = pos
                if start<max and indexbyte(line, start) in single_quoted:
                    raise TokenError("end of line (EOL) while scanning string literal",
                             line, lnum, start+1, token_list)
                tok = token_decode(tokens.ERRORTOKEN, indexbyte(line, pos), lnum, pos, uni_line)
                token_list.append(tok)
                last_comment = b''
                pos = pos + 1

    lnum -= 1
    if not (flags & astconsts.PyCF_DONT_IMPLY_DEDENT):
        if token_list and token_list[-1].token_type != tokens.NEWLINE:
            tok = token_decode(tokens.NEWLINE, b'\n', lnum, 0, u'\n')
            token_list.append(tok)
        for indent in indents[1:]:                # pop remaining indent levels
            token_list.append(token_decode(tokens.DEDENT, b'', lnum, pos, uni_line))
    tok = token_decode(tokens.NEWLINE, b'\n', lnum, 0, u'\n')
    token_list.append(tok)

    token_list.append(token_decode(tokens.ENDMARKER, b'', lnum, pos, uni_line))
    return token_list


def universal_newline(line):
    # show annotator that indexes below are non-negative
    line_len_m2 = len(line) - 2
    if line_len_m2 >= 0 and line[-2] == b'\r' and line[-1] == b'\n':
        return line[:line_len_m2] + b'\n'
    line_len_m1 = len(line) - 1
    if line_len_m1 >= 0 and line[-1] == b'\r':
        return line[:line_len_m1] + b'\n'
    return line
