import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'GReNMlin'))

from GReNMlin.grn import grn
from utils.grn_utils import DEFAULT_PARAMS
from components.adder import create_n_bit_ripple_carry_adder
from components.multiplier import create_n_by_m_multiplier
from components.right_shifter import create_n_bit_right_shifter

import simulator as simulator


def biological_add(adder_grn, a, b, num_bits):

    input_values = {"C0": 0.0}
    for i in range(num_bits):
        input_values[f"A{i}"] = 100.0 if (a >> i) & 1 else 0.0
        input_values[f"B{i}"] = 100.0 if (b >> i) & 1 else 0.0

    IN = [input_values.get(name, 0.0) for name in adder_grn.input_species_names]
    _, results = simulator.simulate_single(adder_grn, IN, t_end=5000, plot_on=False)

    final = results[-1]
    species_to_conc = {name: final[i] for i, name in enumerate(adder_grn.species_names)}

    sum_result = 0
    for i in range(num_bits):
        if species_to_conc[f"S{i}"] > 10.0:
            sum_result |= (1 << i)

    if species_to_conc["Cout_final"] > 10.0:
        sum_result |= (1 << num_bits)

    return sum_result


def biological_shift_right(shifter_grn, value, n_bits):
    input_values = {}
    for i in range(n_bits + 1):
        input_values[f"IN{i}"] = 100.0 if (value >> i) & 1 else 0.0

    IN = [input_values.get(name, 0.0) for name in shifter_grn.input_species_names]
    _, results = simulator.simulate_single(shifter_grn, IN, t_end=3000, plot_on=False)

    final = results[-1]
    species_to_conc = {name: final[i] for i, name in enumerate(shifter_grn.species_names)}

    result = 0
    for i in range(n_bits):
        if species_to_conc[f"OUT{i}"] > 10.0:
            result |= (1 << i)

    return result


def biological_multiply(multiplier_grn, a, num_bits):
    
    input_values = {}
    for i in range(num_bits):
        val = 100.0 if (a >> i) & 1 else 0.0
        input_values[f"A{i}"] = val
        input_values[f"B{i}"] = val

    IN = [input_values.get(name, 0.0) for name in multiplier_grn.input_species_names]
    _, results = simulator.simulate_single(multiplier_grn, IN, t_end=5000, plot_on=False)

    final = results[-1]
    species_to_conc = {name: final[i] for i, name in enumerate(multiplier_grn.species_names)}

    product_result = 0
    for i in range(2 * num_bits):
        if species_to_conc.get(f"P{i}", 0) > 50.0:
            product_result |= (1 << i)

    return product_result


def binary_search_sqrt(target, num_bits=4, params=None):
    
    if params is None:
        params = DEFAULT_PARAMS

    print(f"\nComputing sqrt({target}) using {num_bits}-bit operations (adder + multiplier)...")

    # Create all GRNs once (reuse across iterations)
    print("Creating biological circuits...")
    adder_grn = grn()
    create_n_bit_ripple_carry_adder(adder_grn, num_bits)

    shifter_grn = grn()
    create_n_bit_right_shifter(shifter_grn, num_bits, params)

    multiplier_grn = grn()
    create_n_by_m_multiplier(multiplier_grn, num_bits, num_bits, params)

    low = 0
    high = min(target, (1 << num_bits) - 1)
    iterations = 0
    max_iterations = num_bits

    print(f"Search range: [{low}, {high}]")
    print(f"Max iterations: {max_iterations}\n")

    while low <= high and iterations < max_iterations:
        iterations += 1
        print(f"Iteration {iterations}:")

        # Step 1: Biological addition (low + high)
        print(f"  Computing {low} + {high} using biological adder...")
        sum_result = biological_add(adder_grn, low, high, num_bits)
        print(f"  Biological adder result: {sum_result}")

        # Step 2: Biological division by 2 (right shift)
        # mid = sum_result >> 1
        mid = biological_shift_right(shifter_grn, sum_result, num_bits)
        print(f"  mid = {mid}")

        # Step 3: Biological multiplication (mid × mid)
        print(f"  Computing {mid} * {mid} using biological multiplier...")
        square_result = biological_multiply(multiplier_grn, mid, num_bits)
        print(f"  Biological multiplier result: {square_result}")

        # Step 4: Python comparison and update
        if square_result == target:
            print(f"  Exact match found! sqrt({target}) = {mid}\n")
            return mid
        elif square_result < target:
            low = mid + 1
            print(f"  {mid}² = {square_result} < {target}, guess too low")
            print(f"  Updating low = {low}\n")
        else:
            high = mid - 1
            print(f"  {mid}² = {square_result} > {target}, guess too high")
            print(f"  Updating high = {high}\n")

    result = high if high >= 0 and high * high <= target else low
    print(f"Final result: sqrt({target}) ≈ {result}\n")
    return result