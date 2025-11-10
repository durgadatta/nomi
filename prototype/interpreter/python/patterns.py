import ast

class PatternMixin:
    def match_case(self, case: ast.match_case, subject: Any) -> bool:
        pattern = case.pattern
        if isinstance(pattern, ast.MatchValue):
            return self.eval(pattern.value) == subject
        elif isinstance(pattern, ast.MatchSingleton):
            return subject is pattern.value
        elif isinstance(pattern, ast.MatchSequence):
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
        elif isinstance(pattern, ast.MatchMapping):
            if not isinstance(subject, dict):
                return False
            for key, pat in zip(pattern.keys, pattern.patterns):
                key_val = self.eval(key)
                if key_val not in subject or not self.match_case(ast.match_case(pattern=pat), subject[key_val]):
                    return False
            if pattern.rest:
                self.current_env.set(pattern.rest, {k: v for k, v in subject.items() if k not in [self.eval(k) for k in pattern.keys]})
            return True
        elif isinstance(pattern, ast.MatchClass):
            cls = self.eval(pattern.cls)
            if not isinstance(subject, cls):
                return False
            for attr, pat in zip(pattern.attributes, pattern.patterns):
                if not self.match_case(ast.match_case(pattern=pat), getattr(subject, attr)):
                    return False
            return True
        elif isinstance(pattern, ast.MatchStar):
            if pattern.name:
                self.current_env.set(pattern.name, list(subject))
            return True
        elif isinstance(pattern, ast.MatchAs):
            if pattern.pattern and not self.match_case(ast.match_case(pattern=pattern.pattern), subject):
                return False
            if pattern.name:
                self.current_env.set(pattern.name, subject)
            return True
        elif isinstance(pattern, ast.MatchOr):
            return any(self.match_case(ast.match_case(pattern=p), subject) for p in pattern.patterns)
        return False
    

    def eval_Match(self, node: ast.Match) -> None:
        subject = self.eval(node.subject)
        for case in node.cases:
            if self.match_case(case, subject):
                self.eval(case.body)
                break
