from utils.grn_utils import (
    create_or_gate,
    create_half_adder, create_full_adder,
    create_partial_products, DEFAULT_PARAMS
)

def _sum_inputs_at_bit(grn_object, inputs, output_name, carry_output_name, params=None):
    
    if params is None:
        params = DEFAULT_PARAMS

    n = len(inputs)

    if n == 0:
        return
    elif n == 1:
        create_or_gate(grn_object, [inputs[0]], output_name, params)
        if carry_output_name is not None:
            grn_object.add_species(carry_output_name, 1.0)
    elif n == 2:
        create_half_adder(grn_object, inputs[0], inputs[1], output_name, carry_output_name, params)
    elif n == 3:
        create_full_adder(grn_object, inputs[0], inputs[1], inputs[2], output_name, carry_output_name, params)
    else:
        current_sum = f"{output_name}_INTER_SUM_0"
        carries = []

        if n >= 3:
            inter_carry = f"{output_name}_INTER_CARRY_0"
            grn_object.add_species(inter_carry, 1.0)
            create_full_adder(grn_object, inputs[0], inputs[1], inputs[2], current_sum, inter_carry, params)
            carries.append(inter_carry)

            remaining = 3
        elif n == 2:
            inter_carry = f"{output_name}_INTER_CARRY_0"
            grn_object.add_species(inter_carry, 1.0)
            create_half_adder(grn_object, inputs[0], inputs[1], current_sum, inter_carry, params)
            carries.append(inter_carry)
            remaining = 2
        else:
            remaining = 1

        idx = remaining
        while idx < n:
            next_sum = f"{output_name}_INTER_SUM_{len(carries)}"

            if idx + 1 < n:
                inter_carry = f"{output_name}_INTER_CARRY_{len(carries)}"
                grn_object.add_species(inter_carry, 1.0)
                create_full_adder(grn_object, current_sum, inputs[idx], inputs[idx+1],
                                next_sum, inter_carry, params)
                carries.append(inter_carry)
                idx += 2
            else:
                inter_carry = f"{output_name}_INTER_CARRY_{len(carries)}"
                grn_object.add_species(inter_carry, 1.0)
                create_half_adder(grn_object, current_sum, inputs[idx],
                                next_sum, inter_carry, params)
                carries.append(inter_carry)
                idx += 1

            current_sum = next_sum

        if len(carries) == 0:
            create_or_gate(grn_object, [current_sum], output_name, params)
        elif len(carries) == 1:
            create_or_gate(grn_object, [current_sum], output_name, params)
            if carry_output_name is not None:
                create_or_gate(grn_object, [carries[0]], carry_output_name, params)
        else:
            final_carry_sum = f"{output_name}_CARRY_SUM"
            _sum_inputs_at_bit(grn_object, carries, final_carry_sum, carry_output_name, params)

            create_or_gate(grn_object, [current_sum], output_name, params)


def create_n_by_m_multiplier(grn_object, n_bits, m_bits=None, params=None):
    
    if params is None:
        params = DEFAULT_PARAMS

    if m_bits is None:
        m_bits = n_bits

    # Define all input species
    for i in range(n_bits):
        grn_object.add_input_species(f"A{i}")

    for j in range(m_bits):
        grn_object.add_input_species(f"B{j}")

    # Define all output species
    total_bits = n_bits + m_bits
    for k in range(total_bits):
        grn_object.add_species(f"P{k}", 1.0)

    # Generate partial products matrix
    pp_matrix = create_partial_products(grn_object, "A", "B", n_bits, m_bits, params)


    carries = [None]
    for i in range(1, total_bits + 1):
        carry_name = f"CARRY_{i}"
        carries.append(carry_name)
        grn_object.add_species(carry_name, 1.0)

    for bit_pos in range(total_bits):
        inputs_for_bit = []

        for i in range(n_bits):
            for j in range(m_bits):
                if i + j == bit_pos:
                    inputs_for_bit.append(pp_matrix[i][j])

        if bit_pos > 0 and carries[bit_pos] is not None:
            inputs_for_bit.append(carries[bit_pos])

        if bit_pos < total_bits - 1:
            carry_output = carries[bit_pos + 1]
        else:
            carry_output = None

        if len(inputs_for_bit) == 0:
            continue
        elif len(inputs_for_bit) == 1:
            create_or_gate(grn_object, [inputs_for_bit[0]], f"P{bit_pos}", params)
        else:
            _sum_inputs_at_bit(grn_object, inputs_for_bit, f"P{bit_pos}", carry_output, params)