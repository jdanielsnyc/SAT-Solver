#!/usr/bin/env python3
"""6.009 Lab 6 -- Boolean satisfiability solving"""

import sys
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS


def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """

    def update_formula(var, val):
        # Creates a new formula based on taking the current formula and setting the variable
        # var to val, or returns None if doing so creates a contradiction
        new_formula = []
        for clause in formula:
            if len(clause) == 1:
                # First, deal with the case where this clause has length 1
                x, b = clause[0]
                if x == var:
                    if b == (not val):
                        # Contradiction, we have (x, val), but clause requires (x, not val)
                        return None
                    else:
                        # Our assumed (var, val) assignment satisfies this clause entirely, so we
                        # don't need to add a modified version of it to our new formula
                        continue
            else:
                old_clause = clause
                clause = []
                for i in old_clause:
                    if i == (var, val):
                        # If our assumption satisfies this clause, we don't need it in our updated formula
                        clause = None
                        break
                    elif not i[0] == var:
                        # If our assumption doesn't satisfy this clause, but the variable we're assuming is
                        # contained in it, we ignore it
                        clause.append(i)
            if clause is not None:
                new_formula.append(clause)
        return new_formula

    def get_assumed_SAT(assumed):
        new = update_formula(assumed[0], assumed[1])  # Update our formula based on the variable we assumed
        #print(new)
        #print(len(new))
        base_solution = {assumed[0]: assumed[1]}
        new_SAT = None
        if new is not None:
            if len(new) == 0:  # the boolean we assumed was the only variable that this formula depended on
                return base_solution
            else:
                new_SAT = satisfying_assignment(new)
        if new_SAT is not None:
            new_SAT.update(base_solution)
            return new_SAT
        else:
            return None

    if not formula:
        return {}

    # Choose a variable to assume True/False, giving priority to variables in clauses of length 1
    assumed_solution = [None, None]
    for i in formula:
        if len(i) == 1 or i == formula[-1]:
            # Assume the case when x is True, and when x is False
            x, b = i[0]
            assumed_solution[0] = x, b
            assumed_solution[1] = x, not b
            break

    # First try x, b, then x, not b if that doesn't work
    try_b = get_assumed_SAT(assumed_solution[0])
    return try_b if try_b is not None else get_assumed_SAT(assumed_solution[1])


def boolify_scheduling_problem(students, sessions):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of session names (strings) that work for that student
    session_capacities: a dictionary mapping each session name to a positive
                        integer for how many students can fit in that session

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up
    We assume no student or session names contain underscores.
    """

    CNF = []
    for stu in students.keys():
        # Every student must be paired to at least one session
        clause = []
        for sesh in students[stu]:
            clause.append((stu + '_' + sesh, True))
        CNF.append(clause)


    keys = list(sessions.keys())
    l = len(keys)
    for stu in students.keys():
        # Every student must be paired to at most one session
        # Translation: For any student, and for any pair of sessions, at least one
        # student-session pair must be False
        for i in range(l):
            sesh1 = keys[i]
            a = stu + '_' + sesh1
            for j in range(i + 1, l):
                sesh2 = keys[j]
                b = stu + '_' + sesh2
                CNF.append([(a, False), (b, False)])


    def all_combinations(size, bound):
        # Creates a list of combinations of unique elements where each one is between zero and bound - 1 inclusive
        assert bound >= size  # Elements can't repeat, so we need at least as many options as we have combo slots

        def build_combos(combo=[]):
            lower = 0
            if combo:  # If combo is not empty
                # The values we choose for the next elements of this combination must be strictly greater than
                # any of the values currently it contains
                lower = combo[-1] + 1
            upper = bound - (size - len(combo) - 1)  # We will be adding size - len(combo) - 1 more elements after
            # this next element, so we need at least size - len(combo) - 1 options guaranteed to be available
            # for addition in those slots
            combos = []
            for val in range(lower, upper):
                new_combo = combo[:] + [val]
                if len(new_combo) == size:
                    # If we've reached our desired size, return this combination
                    combos.append(new_combo)
                else:
                    # Otherwise, build off of it to create all of its derived combinations
                    combos = combos + build_combos(new_combo)
            return combos

        return (i for i in build_combos())


    keys = list(students.keys())
    num_students = len(keys)
    for sesh in sessions.keys():
        # No session can contain more students than its maximum capacity
        # Translation: For any session with capacity N, for every combination of N + 1 students
        # paired with that session, there must be at least one student-session pair that is False
        l = sessions[sesh]
        if l >= num_students:
            # If this session can accommodate all students, we don't need to create a clause for it
            continue
        for student_combo in all_combinations(l + 1, num_students):
            # For each combination of (session capacity) + 1 students, at least one must not be in this session
            clause = []
            for student_index in student_combo:
                student = keys[student_index] + '_' + sesh
                clause.append((student, False))
            CNF.append(clause)

    return CNF


if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
