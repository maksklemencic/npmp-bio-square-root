import tellurium as te 
import matplotlib.pyplot as plt

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
        Y -> ; k3 * Y

        X = {X_val}
        Y = 0

        k1 = 1
        k2 = 0.5
        k3 = 0
    """

    model = model_template.format(X_val=x_input)

    rr = te.loadAntimonyModel(model)
    rr.simulate(0, 5, 1000)

    ss = rr.getSteadyStateValues()
    steady_x, steady_y = ss[0], ss[1]

    print(f"\nInput X value: {steady_x:.5f}")
    print(f"Approximated sqrt(X): {steady_y:.5f}")

    rr.plot()
    # plt.savefig("sqrt_result.png")

if __name__ == "__main__":
    main()