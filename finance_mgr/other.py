def rupiah(x: float) -> str:
    if x >= 0:
        return "Rp" + f"{abs(x):,.2f}".replace(",", ".")
    else:
        return "(Rp" + f"{abs(x):,.2f}".replace(",", ".") + ")"