from regex_solver import RegexSolver
import z3

def solve_regex(regex, minLength=0, maxLength=200):

    trialLength = range(minLength + 1, maxLength)

    for i in trialLength:
        try:
            unknowns = [z3.Int("x_%02d" % i) for i in range(i)]
            expr = RegexSolver(i, regex, unknowns).sat_expr()
            solver = z3.Solver()
            solver.add(expr)
            if solver.check() == z3.sat:
                model = solver.model()
                answer = [model[unknowns[i]].as_long() for i in range(i)]
                return ''.join(map(chr, answer))
        except BaseException as e:
            print(f'exception: {e}')
            pass
    return None

import re
GENERATED_STRING_COUNT_PER_REGEX=1
if __name__ == '__main__':
    regexes = []
    r=r"""^([0-9]{1,3}\.){3}[0-9]{1,3}(\/([0-9]|[1-2][0-9]|3[0-2]))?$"""
    regexes.insert(0,r)
    #print(solve_regex(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$"))
    for i in regexes:
        r = re.compile(i)
        print(i)
        for j in range(GENERATED_STRING_COUNT_PER_REGEX):
            try:
                match = solve_regex(i)
                if not r.match(match):
                    print('FALSE!')
                else:
                    print(f'TRUE!: {match} {i}')
            except:
                print('something bad happened')                    

    print(solve_regex(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9]+\.[a-zA-Z]*$"))