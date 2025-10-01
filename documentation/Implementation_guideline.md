# Implementation Guideline

## Initial Prototyping
* Start with Python base 
* start with a simple function
    * make gradual and minimal modification to introduce new syntax 
    * dynamically change certain semantics to extend/update the behavior
    * map the Nomi AST to Python AST
    * compile and execute the Python AST
* Build other tools around it -
    * syntax highlighting 
    * map to Language Server Protocol in Vscode
* introduce states (objects)
* Logistical Features
    * modules, import and packaging
* utilities
    * interfacing with os, datetime etc.

## Reduce dependency on Implementation Langauge(Python)
* Implement bare-minimum in Python, then the rest on the reduced form of Nomi itself (akin to PyPy/RPython)
    * so that the implementation can be ported easily later on other source language 
        * easily introduce binding to major languages
    * or also implementing efficiency/performance short-circuiting while still preserving the minimal logical structure

## Caveats
* Be mindful to use Python as an intermediate but transient step that can be later plugged with an standalone system
