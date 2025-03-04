"""Model component base classes."""

from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Type,
    Union,
    cast,
)

from pandera.api.checks import Check

CheckArg = Union[Check, List[Check]]
AnyCallable = Callable[..., Any]


def to_checklist(checks: Optional[CheckArg]) -> List[Check]:
    """Convert value to list of checks."""
    checks = checks or []
    return [checks] if isinstance(checks, Check) else checks


class BaseFieldInfo:
    """Captures extra information about a field.

    *new in 0.5.0*
    """

    __slots__ = (
        "checks",
        "nullable",
        "unique",
        "coerce",
        "regex",
        "check_name",
        "alias",
        "original_name",
        "dtype_kwargs",
        "title",
        "description",
    )

    def __init__(
        self,
        checks: Optional[CheckArg] = None,
        nullable: bool = False,
        unique: bool = False,
        coerce: bool = False,
        regex: bool = False,
        alias: Any = None,
        check_name: Optional[bool] = None,
        dtype_kwargs: Optional[Dict[str, Any]] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        self.checks = to_checklist(checks)
        self.nullable = nullable
        self.unique = unique
        self.coerce = coerce
        self.regex = regex
        self.alias = alias
        self.check_name = check_name
        self.original_name = cast(str, None)  # always set by BaseModel
        self.dtype_kwargs = dtype_kwargs
        self.title = title
        self.description = description

    @property
    def name(self) -> str:
        """Return the name of the field used in the data container object."""
        if self.alias is not None:
            return self.alias
        return self.original_name

    def __set_name__(self, owner: Type, name: str) -> None:
        self.original_name = name

    def __get__(self, instance: Any, owner: Type) -> str:
        return self.name

    def __str__(self):
        return f'{self.__class__}("{self.name}")'

    def __repr__(self):
        cls = self.__class__
        return (
            f'<{cls.__module__}.{cls.__name__}("{self.name}") '
            f"object at {hex(id(self))}>"
        )

    def __hash__(self):
        return str(self.name).__hash__()

    def __eq__(self, other):
        return self.name == other

    def __ne__(self, other):
        return self.name != other

    def __set__(self, instance: Any, value: Any) -> None:  # pragma: no cover
        raise AttributeError(f"Can't set the {self.original_name} field.")


class BaseCheckInfo:  # pylint:disable=too-few-public-methods
    """Captures extra information about a Check."""

    def __init__(self, check_fn: AnyCallable, **check_kwargs: Any):
        self.check_fn = check_fn
        self.check_kwargs = check_kwargs

    def to_check(self, model_cls: Type) -> Check:
        """Create a Check from metadata."""
        name = self.check_kwargs.pop("name", None)
        if not name:
            name = getattr(
                self.check_fn, "__name__", self.check_fn.__class__.__name__
            )

        def _adapter(arg: Any) -> Union[bool, Iterable[bool]]:
            return self.check_fn(model_cls, arg)

        return Check(_adapter, name=name, **self.check_kwargs)
