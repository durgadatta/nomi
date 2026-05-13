import ast
from typing import Any

class PatternMixin:
    _MATCH_PATTERN_DISPATCH = {
        ast.MatchValue: '_match_value',
        ast.MatchSingleton: '_match_singleton',
        ast.MatchSequence: '_match_sequence',
        ast.MatchMapping: '_match_mapping',
        ast.MatchClass: '_match_class',
        ast.MatchStar: '_match_star',
        ast.MatchAs: '_match_as',
        ast.MatchOr: '_match_or',
    }

    def match_case(self, case: ast.match_case, subject: Any) -> bool:
        pattern = case.pattern
        handler = self._MATCH_PATTERN_DISPATCH.get(type(pattern))
        if handler:
            if not getattr(self, handler)(case, subject):
                return False
            if case.guard:
                return bool(self.eval(case.guard))
            return True
        return False

    def _match_value(self, case, subject):
        return self.eval(case.pattern.value) == subject

    def _match_singleton(self, case, subject):
        return subject is case.pattern.value

    def _match_sequence(self, case, subject):
        pattern = case.pattern
        if not hasattr(subject, '__iter__') or isinstance(subject, (str, bytes)):
            return False
        values = list(subject)
        patterns = pattern.patterns
        star_indexes = [
            index for index, pat in enumerate(patterns)
            if isinstance(pat, ast.MatchStar)
        ]

        if not star_indexes:
            if len(values) != len(patterns):
                return False
            return all(
                self.match_case(ast.match_case(pattern=pat), value)
                for pat, value in zip(patterns, values)
            )

        if len(star_indexes) > 1:
            return False

        star_index = star_indexes[0]
        prefix = patterns[:star_index]
        suffix = patterns[star_index + 1:]
        if len(values) < len(prefix) + len(suffix):
            return False

        for pat, value in zip(prefix, values[:len(prefix)]):
            if not self.match_case(ast.match_case(pattern=pat), value):
                return False

        suffix_values = values[len(values) - len(suffix):] if suffix else []
        for pat, value in zip(suffix, suffix_values):
            if not self.match_case(ast.match_case(pattern=pat), value):
                return False

        star_pattern = patterns[star_index]
        if star_pattern.name:
            end = len(values) - len(suffix) if suffix else len(values)
            self.current_env.set(star_pattern.name, values[len(prefix):end])
        return True

    def _match_mapping(self, case, subject):
        pattern = case.pattern
        if not isinstance(subject, dict):
            return False
        for key, pat in zip(pattern.keys, pattern.patterns):
            key_val = self.eval(key)
            if key_val not in subject or not self.match_case(
                ast.match_case(pattern=pat), subject[key_val]
            ):
                return False
        if pattern.rest:
            self.current_env.set(
                pattern.rest,
                {k: v for k, v in subject.items()
                 if k not in [self.eval(k) for k in pattern.keys]}
            )
        return True

    def _match_class(self, case, subject):
        pattern = case.pattern
        cls = self.eval(pattern.cls)
        if not isinstance(subject, cls):
            return False
        for attr, pat in zip(pattern.attributes, pattern.patterns):
            if not self.match_case(ast.match_case(pattern=pat), getattr(subject, attr)):
                return False
        return True

    def _match_star(self, case, subject):
        if case.pattern.name:
            self.current_env.set(case.pattern.name, list(subject))
        return True

    def _match_as(self, case, subject):
        pattern = case.pattern
        if pattern.pattern and not self.match_case(
            ast.match_case(pattern=pattern.pattern), subject
        ):
            return False
        if pattern.name:
            self.current_env.set(pattern.name, subject)
        return True

    def _match_or(self, case, subject):
        return any(
            self.match_case(ast.match_case(pattern=p), subject)
            for p in case.pattern.patterns
        )
    

    def eval_Match(self, node: ast.Match) -> None:
        subject = self.eval(node.subject)
        for case in node.cases:
            if self.match_case(case, subject):
                self.eval(case.body)
                break
