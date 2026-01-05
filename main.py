from components.square_root import binary_search_sqrt

if __name__ == "__main__":

    print("=" * 70)
    print("SQUARE ROOT WITH ADDER TEST")
    print("=" * 70)

    test_values = [1, 4, 9, 15, 16]

    for n in test_values:
        result = binary_search_sqrt(n, num_bits=4)
        expected = int(n**0.5)
        status = "PASSED" if result == expected else "FAILED"
        print(f"sqrt({n}) = {result} (expected {expected}) [{status}]")
        print("-" * 70)