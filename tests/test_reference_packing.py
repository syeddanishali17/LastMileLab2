"""The 34 km packing is a named teaching plan over the backend matrix."""

from app.core.loader import load_and_precheck
from display import packing_from_matrix, path_distance_metres


def test_learning_6_reference_packing_uses_backend_matrix() -> None:
    _precheck, dataset = load_and_precheck("LEARNING_6")
    assert dataset is not None
    matrix = dataset.distance_matrix.model_dump(mode="json")
    customers = [customer.model_dump(mode="json") for customer in dataset.customers]
    packing = packing_from_matrix(matrix, customers)
    assert packing["total_distance_metres"] == 34000
    assert packing["routes"][0]["distance_metres"] == 14000
    assert packing["routes"][1]["distance_metres"] == 20000
    assert packing["routes"][0]["load_totes"] == 10
    assert packing["routes"][1]["load_totes"] == 10
    assert path_distance_metres(matrix, ["DEPOT_L6", "C1"]) == 3000
