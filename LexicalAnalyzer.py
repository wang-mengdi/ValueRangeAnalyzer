import os
import sys
import re

def delete_comments(lines):
    f = lambda L:L.lstrip(' ')[0]!='#'
    return list(filter(f,lines))

def get_tokens(S):
    print(S)
    re_str = r"int|float|goto|if|else|Function"\
            "|\d+\.\d+[eE][-+]?\d+|\d+\.\d+|[+-]?\d+"\
            "|[a-zA-Z_]\.\d+|[a-zA-Z_]\w*"\
            "|\+|\-|\*|/|="\
            "|<=|<|>=|>|==|!="\
            "|\(|\)|\{|\}|,|;;|;|:|#"
    patterns = re.compile(re_str)
    tokens = patterns.findall(S)
    sum_tokens = sum(list(map(lambda t:len(t),tokens)))
    sum_text = len(S)-S.count(' ')-S.count('\n')
    assert(sum_tokens == sum_text, "regex failed")
    return tokens
