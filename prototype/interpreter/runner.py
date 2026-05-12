import ast
from typing import Callable, Dict, Any, Optional
from pathlib import Path


def make_runner(
    generate_ast: Callable,
    interpreter_cls,
    *,
    desugar: Optional[Callable] = None,
    wrap_errors: bool = True,
):
    def run_eval_loop(code=None, file_name=None, tree=None) -> Dict[str, Any]:
        assert code or file_name or tree
        if tree is None:
            if code is None:
                code = Path(file_name).read_text(encoding='utf-8')
            tree = generate_ast(code=code, dump=False)

        if desugar is not None:
            tree = desugar(tree)

        tree = ast.fix_missing_locations(tree)
        interpreter = interpreter_cls()
        try:
            interpreter.eval(tree)
            return interpreter.global_env.bindings
        except Exception as e:
            if wrap_errors:
                raise RuntimeError(f"Execution failed: {str(e)}") from e
            raise
    return run_eval_loop
