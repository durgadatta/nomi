"""Versioned, JSON-safe boundary for the bounded source-analysis producer."""

from dataclasses import asdict, dataclass


RESTRICTIONS = ("known-types", "pure")


@dataclass(frozen=True)
class AnalysisPolicy:
    requirements: tuple[str, ...] = ()
    version: int = 1

    def __post_init__(self):
        if type(self.version) is not int or self.version != 1:
            raise ValueError("unsupported analysis policy version; expected 1")
        if not isinstance(self.requirements, tuple):
            raise TypeError("analysis requirements must be a tuple")
        if any(type(name) is not str or name not in RESTRICTIONS
               for name in self.requirements):
            raise ValueError(f"analysis requirements must be drawn from {RESTRICTIONS}")
        if len(set(self.requirements)) != len(self.requirements):
            raise ValueError("analysis requirements must not be duplicated")


@dataclass(frozen=True)
class AnalysisResult:
    version: int
    source: dict
    analyzer: dict
    scope: str
    facts: tuple[dict, ...]
    obligations: tuple[dict, ...]
    effects: tuple[str, ...]
    latent_functions: tuple[dict, ...]
    restrictions: tuple[dict, ...]
    assumptions: tuple[str, ...]

    @property
    def admitted(self) -> bool:
        return all(item["satisfied"] for item in self.restrictions)

    @property
    def ok(self) -> bool:
        return self.admitted

    def to_dict(self) -> dict:
        result = asdict(self)
        for field in ("facts", "obligations", "effects", "latent_functions",
                      "restrictions", "assumptions"):
            result[field] = list(result[field])
        result["admitted"] = self.admitted
        result["ok"] = self.ok
        return result
