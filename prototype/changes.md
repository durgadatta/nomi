# Change that only require grammar tweak (but no AST modification)
* simple grammar change (only def -> fun)
    * while this can be done via other text processing within IDE, the idea of modifying the grammar is more important now


# AST modifications
    - Add predicate as annotations to variable; then also to parameters by extension

# Changes Outside Python
    - parameter predicate can be enforced at call time with decorators; this may not apply to variable declaration

