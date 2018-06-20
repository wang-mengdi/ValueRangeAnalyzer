import os
import sys
import re

def delete_empty_lines(lines):
    f = lambda L:L.rstrip(' \n')!=""
    return list(filter(f,lines))

def get_tokens(S):
    #print(S)
    re_str = r"PHI|int|float|goto|if|else|Function|return"\
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
