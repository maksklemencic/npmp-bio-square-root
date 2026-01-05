from utils.grn_utils import DEFAULT_PARAMS

def create_n_bit_right_shifter(grn_object, n, params=None):
    if params is None:
        params = DEFAULT_PARAMS

    for i in range(n + 1):
        grn_object.add_input_species(f"IN{i}")

    for i in range(n):
        grn_object.add_species(f"OUT{i}", 1.0)

    for i in range(n):
        grn_object.add_gene(
            alpha=params["alpha"],
            regulators=[
                {
                    "name": f"IN{i+1}",
                    "type": 1,
                    "Kd": params["Kd"],
                    "n": params["n"],
                }
            ],
            products=[{"name": f"OUT{i}"}],
            logic_type=""
        )
