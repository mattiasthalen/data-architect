"""Delimiter escaping and unescaping for keyset identity components.

The keyset format uses @ ~ | as delimiters. Components may contain these
characters, so they must be escaped by doubling:
  @ -> @@
  ~ -> ~~
  | -> ||
"""


def escape_delimiters(s: str) -> str:
    """Escape delimiter characters by doubling them.

    Args:
        s: The string to escape

    Returns:
        String with delimiters escaped: @ -> @@, ~ -> ~~, | -> ||

    Examples:
        >>> escape_delimiters("a@b")
        'a@@b'
        >>> escape_delimiters("a@b~c|d")
        'a@@b~~c||d'
    """
    return s.replace("@", "@@").replace("~", "~~").replace("|", "||")


def unescape_delimiters(s: str) -> str:
    """Unescape delimiter characters by undoubling them.

    Args:
        s: The string to unescape (typically a segment from parse_keyset)

    Returns:
        String with delimiters unescaped: @@ -> @, ~~ -> ~, || -> |

    Examples:
        >>> unescape_delimiters("a@@b")
        'a@b'
        >>> unescape_delimiters("a@@b~~c||d")
        'a@b~c|d'

    Note:
        This works correctly because segments have already been split on
        unescaped delimiters, so they cannot contain single delimiters.
        Multiple consecutive escaped delimiters unescape correctly:
        @@@@ -> @@, ~~~~~~ -> ~~~
    """
    return s.replace("@@", "@").replace("~~", "~").replace("||", "|")
