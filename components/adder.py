from utils.grn_utils import create_or_gate, create_full_adder, DEFAULT_PARAMS

def create_n_bit_ripple_carry_adder(grn_object, n, params=None):
    if params is None:
        params = DEFAULT_PARAMS

    for i in range(n):
        grn_object.add_input_species(f"A{i}")
        grn_object.add_input_species(f"B{i}")
    
    grn_object.add_input_species("C0")

    for i in range(1, n+1):
        grn_object.add_species(f"C{i}", 1.0)

    for i in range(n):
        grn_object.add_species(f"S{i}", 1.0)

    grn_object.add_species("Cout_final", 1.0)

    #chain of full adders, one for each bit
    for i in range(n):
        a_bit = f"A{i}"
        b_bit = f"B{i}"
        carry_in = f"C{i}"
        sum_out = f"S{i}"
        carry_out = f"C{i+1}"

        create_full_adder(grn_object, a_bit, b_bit, carry_in, sum_out, carry_out, params)

    create_or_gate(grn_object, [f"C{n}"], "Cout_final", params)