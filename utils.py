import inspect
import typing as t

from models.employee_options import EmployeeOptions
from espp_state import ESPPState

def get_all_functions(
        module: object
) -> t.List[t.Tuple[str, t.Callable[[EmployeeOptions, ESPPState], t.Tuple[float, float]]]]:
    return [obj for name, obj in inspect.getmembers(module) if inspect.isfunction(obj)]