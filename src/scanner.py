import enum
import string


TokenType = enum.IntEnum(
    value="TokenType",
    names=(
        # Parenthesis
        "LEFT_PAREN",
        "RIGHT_PAREN",
        "LEFT_BRACE",
        "RIGHT_BRACE",

        # Single character operations
        "COMMA",
        "DOT",
        "MINUS",
        "PLUS",
        "SEMICOLON",
        "SLASH",
        "STAR",

        # Assignment \ comparison operations
        "BANG",
        "BANG_EQUAL",
        "EQUAL",
        "EQUAL_EQUAL",
        "GREATER",
        "GREATER_EQUAL",
        "LESS",
        "LESS_EQUAL",

        # Variable content multi-character lexemes
        "IDENTIFIER",
        "STRING",
        "NUMBER",

        # Keywords
        "AND",
        "CLASS",
        "ELSE",
        "FALSE",
        "FUN",
        "FOR",
        "IF",
        "NIL",
        "OR",
        "PRINT",
        "RETURN",
        "SUPER",
        "THIS",
        "TRUE",
        "VAR",
        "WHILE",

        # Misc
        "EOF"
    )
)


KEYWORDS = (
    TokenType.AND,
    TokenType.CLASS,
    TokenType.ELSE,
    TokenType.FALSE,
    TokenType.FUN,
    TokenType.FOR,
    TokenType.IF,
    TokenType.NIL,
    TokenType.OR,
    TokenType.PRINT,
    TokenType.RETURN,
    TokenType.SUPER,
    TokenType.THIS,
    TokenType.TRUE,
    TokenType.VAR,
    TokenType.WHILE,
)


class Token:
    def __init__(self, type_, lexeme, value=None):
        self.type = type_
        self.lexeme = lexeme
        self.value = value

    def __repr__(self):
        return f"Token(type={self.type.name}, lexeme=\"{self.lexeme}\", value={self.value})"


class ScanningError(Exception):
    pass


class Scanner:
    def __init__(self, stream):
        self._stream = stream
        self._offset = 0

    def _scan_single_char_token(self):
        char = self._stream[self._offset]
        match char:
            case "(" : return Token(TokenType.LEFT_PAREN, char)
            case ")" : return Token(TokenType.RIGHT_PAREN, char)
            case "{" : return Token(TokenType.LEFT_BRACE, char)
            case "}" : return Token(TokenType.RIGHT_BRACE, char)
            case "," : return Token(TokenType.COMMA, char)
            case "-" : return Token(TokenType.MINUS, char)
            case "+" : return Token(TokenType.PLUS, char)
            case ";" : return Token(TokenType.SEMICOLON, char)
            case "*" : return Token(TokenType.STAR, char)
            case _: return None

    def _scan_assignment_or_comparison_tokens(self):
        view = self._stream[self._offset : self._offset + 2]
        match tuple(view):
            case ("=", "="): return Token(TokenType.EQUAL_EQUAL, view)
            case ("!", "="): return Token(TokenType.BANG_EQUAL, view)
            case ("<", "="): return Token(TokenType.LESS_EQUAL, view)
            case (">", "="): return Token(TokenType.GREATER_EQUAL, view)
            case ("=", *chars): return Token(TokenType.EQUAL, view[0])
            case ("!", *chars): return Token(TokenType.BANG, view[0])
            case ("<", *chars): return Token(TokenType.LESS, view[0])
            case (">", *chars): return Token(TokenType.GREATER, view[0])
            case _: return None

    def _scan_identifier_or_keyword(self):
        if not self._stream[self._offset].isalpha():
            return None

        length = 0
        while (
            len(self._stream) != self._offset + length and
            self._stream[self._offset + length].isalnum()
        ):
            length += 1

        lexeme = self._stream[self._offset : self._offset + length]
        match lexeme:
            case "and": return Token(TokenType.AND, lexeme)
            case "class": return Token(TokenType.CLASS, lexeme)
            case "else": return Token(TokenType.ELSE, lexeme)
            case "false": return Token(TokenType.FALSE, lexeme)
            case "fun": return Token(TokenType.FUN, lexeme)
            case "for": return Token(TokenType.FOR, lexeme)
            case "if": return Token(TokenType.IF, lexeme)
            case "nil": return Token(TokenType.NIL, lexeme)
            case "or": return Token(TokenType.OR, lexeme)
            case "print": return Token(TokenType.PRINT, lexeme)
            case "return": return Token(TokenType.RETURN, lexeme)
            case "super": return Token(TokenType.SUPER, lexeme)
            case "this": return Token(TokenType.THIS, lexeme)
            case "true": return Token(TokenType.TRUE, lexeme)
            case "var": return Token(TokenType.VAR, lexeme)
            case "while": return Token(TokenType.WHILE, lexeme)
            case _: return Token(TokenType.IDENTIFIER, lexeme, lexeme)

    def _scan_string(self):
        def _get_character(offset):
            view = self._stream[offset : offset + 2]
            if 0 == len(view):
                # Reached end of stream
                return None, None

            match tuple(view):
                case ("\\", "\\"): return ("\\", True)
                case ("\\", "\""): return ("\"", True)
                case ("\\", "t"): return ("\t", True)
                case ("\\", "v"): return ("\v", True)
                case ("\\", "r"): return ("\r", True)
                case ("\\", "n"): return ("\n", True)
                case ("\\", "b"): return ("\b", True)
                case _: return (view[0], False)

        if "\"" != self._stream[self._offset]:
            return None

        value = ""
        length = 1

        while True:
            character, is_escape_sequence = _get_character(self._offset + length)
            match (character, is_escape_sequence):
                case (None, None): return None
                case ("\"", False):
                    length += 1
                    break
                case char, escape:
                    length += 1 if not escape else 2
                    value += char

        return Token(TokenType.STRING, self._stream[self._offset : self._offset + length], value)

    def _scan_number(self):
        if not self._stream[self._offset].isnumeric():
            return None

        length = 0
        while (
            len(self._stream) != self._offset + length and
            self._stream[self._offset + length].isnumeric()
        ):
            length += 1

        if (
            not len(self._stream) == self._offset + length and
            "." == self._stream[self._offset + length]
        ):
            while (
                len(self._stream) != self._offset + length and
                self._stream[self._offset + length].isnumeric()
            ):
                length += 1

        lexeme = self._stream[self._offset : self._offset + length]
        return Token(TokenType.NUMBER, lexeme, float(lexeme))

    def _scan_comment(self):
        # TODO: Implement
        return None

    def _scan_single_token(self):
        # NOTE: Order determines scanning priority
        scan_attempts = (
            self._scan_single_char_token(),
            self._scan_assignment_or_comparison_tokens(),
            self._scan_identifier_or_keyword(),
            self._scan_string(),
            self._scan_number(),
            self._scan_comment(),
        )

        if not any(scan_attempts):
            raise ScanningError(f"Unrecognized token at offset {self._offset}")

        return next(attempt for attempt in scan_attempts if attempt is not None)

    def tokens(self):
        while self._offset < len(self._stream):
            if self._stream[self._offset] in string.whitespace:
                self._offset += 1
            else:
                token = self._scan_single_token()
                yield token
                self._offset += len(token.lexeme)

        yield Token(TokenType.EOF, None)
