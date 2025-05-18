from typing import List, TypeVar


T = TypeVar('T')
def chunks(l: List[T], n: int) -> List[List[T]]:
    return [l[i:i+n] for i in range(0, len(l), n)]

def list2d_to_str(table: List[List[str]]):
    # find max length for each column using zip and list comprehension
    n = [0]*len(table[0])
    for row in table:
        for i, x in enumerate(row):
            n[i] = max(n[i], len(x))

    text = ""
    for row in table:
        s = "\n"
        for i in range(len(row)):
            s += f'%-{n[i]+2}s'
        text += s % tuple(row)
    return text.lstrip()

def static_init(cls):
    if getattr(cls, "static_init", None):
        cls.static_init()
    return cls


def dict_to_list2d(d: dict):
    return [[k, v] for k, v in d.items()]