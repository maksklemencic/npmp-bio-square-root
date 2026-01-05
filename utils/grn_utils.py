DEFAULT_PARAMS = {
    "alpha": 100.0,
    "Kd": 50.0,
    "n": 3
}

def create_and_gate(grn_object, inputs, output_name, params=None):
   
    if params is None:
        params = DEFAULT_PARAMS

    if output_name not in grn_object.species_names:
        grn_object.add_species(output_name, 1.0)

    regulators = [{"name": name, "type": 1, "Kd": params["Kd"], "n": params["n"]} for name in inputs]
    grn_object.add_gene(alpha=params["alpha"], regulators=regulators, products=[{"name": output_name}], logic_type="and")

def create_or_gate(grn_object, inputs, output_name, params=None):
    if params is None:
        params = DEFAULT_PARAMS

    if output_name not in grn_object.species_names:
        grn_object.add_species(output_name, 1.0)

    regulators = [{"name": name, "type": 1, "Kd": params["Kd"], "n": params["n"]} for name in inputs]
    grn_object.add_gene(alpha=params["alpha"], regulators=regulators, products=[{"name": output_name}], logic_type="or")

def create_not_gate(grn_object, input_name, output_name, params=None):
    if params is None:
        params = DEFAULT_PARAMS

    if output_name not in grn_object.species_names:
        grn_object.add_species(output_name, 1.0)

    regulator = {"name": input_name, "type": -1, "Kd": params["Kd"], "n": params["n"]}
    grn_object.add_gene(alpha=params["alpha"], regulators=[regulator], products=[{"name": output_name}], logic_type="")

def create_xor_gate(grn_object, input1, input2, output_name, params=None):

    if params is None:
        params = DEFAULT_PARAMS

    not_a = f"NOT_{input1}"
    not_b = f"NOT_{input2}"
    and1 = f"{input1}_AND_NOT_{input2}"
    and2 = f"NOT_{input1}_AND_{input2}"

    create_not_gate(grn_object, input1, not_a, params)
    create_not_gate(grn_object, input2, not_b, params)

    create_and_gate(grn_object, [input1, not_b], and1, params)
    create_and_gate(grn_object, [not_a, input2], and2, params)

    create_or_gate(grn_object, [and1, and2], output_name, params)

def create_half_adder(grn_object, input1, input2, sum_name, carry_name=None, params=None):
    
    if params is None:
        params = DEFAULT_PARAMS

    create_xor_gate(grn_object, input1, input2, sum_name, params)

    if carry_name is not None:
        create_and_gate(grn_object, [input1, input2], carry_name, params)

def create_full_adder(grn_object, input1, input2, carry_in, sum_name, carry_out=None, params=None):
   
    if params is None:
        params = DEFAULT_PARAMS

    a_xor_b = f"{input1}_XOR_{input2}_FOR_{sum_name}"
    create_xor_gate(grn_object, input1, input2, a_xor_b, params)
    create_xor_gate(grn_object, a_xor_b, carry_in, sum_name, params)

    if carry_out is not None:
        a_and_b = f"{input1}_AND_{input2}_FOR_{carry_out}"
        cin_and_axorb = f"{carry_in}_AND_{a_xor_b}_FOR_{carry_out}"

        create_and_gate(grn_object, [input1, input2], a_and_b, params)
        create_and_gate(grn_object, [carry_in, a_xor_b], cin_and_axorb, params)
        create_or_gate(grn_object, [a_and_b, cin_and_axorb], carry_out, params)

def create_partial_products(grn_object, a_prefix, b_prefix, n_bits, m_bits=None, params=None):
    
    if params is None:
        params = DEFAULT_PARAMS

    if m_bits is None:
        m_bits = n_bits

    pp_matrix = []

    for i in range(n_bits):
        row = []
        for j in range(m_bits):
            # Create partial product A[i] × B[j]
            pp_name = f"PP_{i}_{j}"
            create_and_gate(grn_object, [f"{a_prefix}{i}", f"{b_prefix}{j}"], pp_name, params)
            row.append(pp_name)
        pp_matrix.append(row)

    return pp_matrix