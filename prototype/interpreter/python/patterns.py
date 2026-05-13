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
        subject_iter = iter(subject)
        for pat in pattern.patterns:
            try:
                if not self.match_case(ast.match_case(pattern=pat), next(subject_iter)):
                    return False
            except StopIteration:
                return False
        try:
            next(subject_iter)
            return False
        except StopIteration:
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
