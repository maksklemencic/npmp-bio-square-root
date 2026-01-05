import tellurium as te
import matplotlib.pyplot as plt
import math

def main():
    while True:
        try:
            x_input = float(input("Enter a positive number to compute its approximate square root: "))
            if x_input <= 0:
                print("Please enter a positive number greater than zero.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

    model_template = """
        X -> X + Y; k1 * X
        Y + Y -> ; k2 * Y * Y

        X = {X_val}
        Y = 0

        k1 = 0.01
        k2 = 0.005
    """

    model = model_template.format(X_val=x_input)

    rr = te.loadAntimonyModel(model)
    result =rr.simulate(0, 200, 1000)

    ss = rr.getSteadyStateValues()
    steady_x, steady_y = ss[0], ss[1]

    print(f"\nInput X value: {steady_x:.5f}")
    print(f"Approximated sqrt(X): {steady_y:.5f}")

    plt.plot(result[:, 0], result[:, 2], linewidth=1.5, label='Y')

    actual_sqrt = math.sqrt(x_input)
    plt.axhline(y=actual_sqrt, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
    plt.text(result[-1, 0] * 0.05, actual_sqrt, f'{actual_sqrt:.5f}',
             color='red', va='bottom')

    plt.xlabel("Čas")
    plt.ylabel("Koncentracija")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()