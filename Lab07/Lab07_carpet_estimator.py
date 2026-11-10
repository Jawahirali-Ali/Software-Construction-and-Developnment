import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

# Predetermined price (Rs. per square foot) for each carpet type
CARPET_PRICES = {
    "Jute": 150,
    "Polyester": 220,
    "Nylon": 300,
    "Wool": 450,
    "Persian": 800,
}

TAX_LIMIT = 30000        # Rs.
TAX_LOW = 0.10           # 10% if cost < 30000
TAX_HIGH = 0.15          # 15% otherwise

SHOP_NAME = "Royal Carpet House"
SHOP_ADDRESS = "Main Bazaar, Muzaffarabad"


# ------------------------------------------------------------------
# Business logic (kept separate from the GUI so it is easy to test)
# ------------------------------------------------------------------
def calculate_estimate(length, width, carpet_type):
    """Return a dict with area, rate, cost, tax rate, tax and final cost."""
    if length <= 0 or width <= 0:
        raise ValueError("Length and width must be greater than zero.")
    if carpet_type not in CARPET_PRICES:
        raise ValueError("Please select a carpet type.")

    area = length * width
    rate = CARPET_PRICES[carpet_type]
    cost = area * rate
    tax_rate = TAX_LOW if cost < TAX_LIMIT else TAX_HIGH
    tax = cost * tax_rate
    return {
        "type": carpet_type,
        "length": length,
        "width": width,
        "area": area,
        "rate": rate,
        "cost": cost,
        "tax_rate": tax_rate,
        "tax": tax,
        "final": cost + tax,
    }


def build_invoice(customer, result, invoice_no, when=None):
    """Return the invoice as plain text."""
    when = when or datetime.now()
    w = 46
    line = "=" * w
    thin = "-" * w

    def row(left, right):
        return f"{left:<26}{right:>{w - 26}}"

    out = [
        line,
        SHOP_NAME.center(w),
        SHOP_ADDRESS.center(w),
        "INVOICE".center(w),
        line,
        row("Invoice No:", f"{invoice_no:05d}"),
        row("Date:", when.strftime("%d-%m-%Y %H:%M")),
        row("Customer:", customer or "Walk-in Customer"),
        thin,
        row("Carpet Type:", result["type"]),
        row("Room Length:", f"{result['length']:g} ft"),
        row("Room Width:", f"{result['width']:g} ft"),
        row("Area:", f"{result['area']:g} sq ft"),
        row("Price per sq ft:", f"Rs. {result['rate']:,.2f}"),
        thin,
        row("Carpet Cost:", f"Rs. {result['cost']:,.2f}"),
        row(f"Tax ({result['tax_rate'] * 100:.0f}%):", f"Rs. {result['tax']:,.2f}"),
        thin,
        row("TOTAL AMOUNT:", f"Rs. {result['final']:,.2f}"),
        line,
        "Thank you for shopping with us!".center(w),
        line,
    ]
    return "\n".join(out)


# ------------------------------------------------------------------
# GUI
# ------------------------------------------------------------------
class CarpetEstimator:
    def __init__(self, root):
        self.root = root
        self.root.title("Carpet Cost Estimator")
        self.root.resizable(False, False)
        self.root.configure(bg="#f3f3f3")

        self.result = None
        self.invoice_no = 0

        title = tk.Label(root, text=SHOP_NAME, font=("Segoe UI", 16, "bold"),
                         bg="#2b4c7e", fg="white", pady=8)
        title.grid(row=0, column=0, columnspan=2, sticky="nsew")

        form = tk.Frame(root, bg="#f3f3f3", padx=15, pady=10)
        form.grid(row=1, column=0, columnspan=2)

        self.name_var = tk.StringVar()
        self.length_var = tk.StringVar()
        self.width_var = tk.StringVar()
        self.type_var = tk.StringVar()

        self._add_row(form, 0, "Customer Name:", tk.Entry(form, textvariable=self.name_var, width=24))
        self._add_row(form, 1, "Room Length (ft):", tk.Entry(form, textvariable=self.length_var, width=24))
        self._add_row(form, 2, "Room Width (ft):", tk.Entry(form, textvariable=self.width_var, width=24))

        combo = ttk.Combobox(
            form, textvariable=self.type_var, state="readonly", width=22,
            values=[f"{k}  (Rs. {v}/sq ft)" for k, v in CARPET_PRICES.items()]
        )
        self._add_row(form, 3, "Carpet Type:", combo)

        btns = tk.Frame(root, bg="#f3f3f3")
        btns.grid(row=2, column=0, columnspan=2, pady=5)
        tk.Button(btns, text="Calculate", width=12, bg="#2b4c7e", fg="white",
                  command=self.calculate).pack(side="left", padx=5)
        self.invoice_btn = tk.Button(btns, text="Generate Invoice", width=14,
                                     state="disabled", command=self.show_invoice)
        self.invoice_btn.pack(side="left", padx=5)
        tk.Button(btns, text="Clear", width=8, command=self.clear).pack(side="left", padx=5)

        # Result area
        res = tk.LabelFrame(root, text=" Estimate ", bg="#f3f3f3", padx=10, pady=8)
        res.grid(row=3, column=0, columnspan=2, padx=15, pady=10, sticky="nsew")
        self.labels = {}
        for i, key in enumerate(["Area", "Carpet Cost", "Tax", "Final Cost"]):
            tk.Label(res, text=key + ":", bg="#f3f3f3", anchor="w", width=14).grid(row=i, column=0, sticky="w")
            lbl = tk.Label(res, text="-", bg="#f3f3f3", anchor="e", width=20,
                           font=("Segoe UI", 10, "bold" if key == "Final Cost" else "normal"))
            lbl.grid(row=i, column=1, sticky="e")
            self.labels[key] = lbl

    @staticmethod
    def _add_row(parent, r, text, widget):
        tk.Label(parent, text=text, bg="#f3f3f3", anchor="w", width=16).grid(row=r, column=0, pady=4, sticky="w")
        widget.grid(row=r, column=1, pady=4)

    def calculate(self):
        try:
            length = float(self.length_var.get())
            width = float(self.width_var.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Length and width must be numbers.")
            return
        carpet = self.type_var.get().split("  (")[0]
        try:
            self.result = calculate_estimate(length, width, carpet)
        except ValueError as e:
            messagebox.showerror("Invalid input", str(e))
            return

        r = self.result
        self.labels["Area"].config(text=f"{r['area']:g} sq ft")
        self.labels["Carpet Cost"].config(text=f"Rs. {r['cost']:,.2f}")
        self.labels["Tax"].config(text=f"Rs. {r['tax']:,.2f} ({r['tax_rate'] * 100:.0f}%)")
        self.labels["Final Cost"].config(text=f"Rs. {r['final']:,.2f}")
        self.invoice_btn.config(state="normal")

    def clear(self):
        for v in (self.name_var, self.length_var, self.width_var, self.type_var):
            v.set("")
        for lbl in self.labels.values():
            lbl.config(text="-")
        self.invoice_btn.config(state="disabled")
        self.result = None

    def show_invoice(self):
        if not self.result:
            return
        self.invoice_no += 1
        text = build_invoice(self.name_var.get().strip(), self.result, self.invoice_no)

        win = tk.Toplevel(self.root)
        win.title(f"Invoice #{self.invoice_no:05d}")
        box = tk.Text(win, font=("Courier New", 10), width=48, height=24, bg="white")
        box.insert("1.0", text)
        box.config(state="disabled")
        box.pack(padx=10, pady=10)

        def save():
            path = filedialog.asksaveasfilename(
                defaultextension=".txt", initialfile=f"invoice_{self.invoice_no:05d}.txt",
                filetypes=[("Text file", "*.txt")])
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text)
                messagebox.showinfo("Saved", "Invoice saved successfully.")

        tk.Button(win, text="Save Invoice", command=save).pack(pady=(0, 10))


if __name__ == "__main__":
    root = tk.Tk()
    CarpetEstimator(root)
    root.mainloop()
