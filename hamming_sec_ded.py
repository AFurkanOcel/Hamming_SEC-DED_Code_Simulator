import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage

# Arka plan rengi
color = "#008165"

# Hamming SEC-DED Kodlama Fonksiyonu
def calculate_parity_bits(data_bits):
    n = len(data_bits)
    r = 0
    while (2 ** r) < (n + r + 1):
        r += 1

    j = 0
    k = 1
    m = len(data_bits)
    res = ''

    for i in range(1, m + r + 1):
        if i == 2 ** j:
            res = res + '0'
            j += 1
        else:
            res = res + data_bits[-1 * k]
            k += 1

    res = res[::-1]

    # Parity bitlerini hesapla
    n = len(res)
    for i in range(r):
        val = 0
        for j in range(1, n + 1):
            if j & (2 ** i) == (2 ** i):
                val = val ^ int(res[-1 * j])
        res = res[:n - (2 ** i)] + str(val) + res[n - (2 ** i) + 1:]

    return res

# Hata tespiti yapan fonksiyon
def detect_error(received):
    n = len(received)
    r = 0
    while (2 ** r) < n:
        r += 1

    binary_syndrome = ''
    for i in range(r):
        val = 0
        for j in range(1, n + 1):
            if j & (2 ** i) == (2 ** i):
                val ^= int(received[-1 * j])
        binary_syndrome = str(val) + binary_syndrome

    decimal_syndrome = int(binary_syndrome, 2)
    return decimal_syndrome, binary_syndrome

# Bit çevirici (hata eklemek için)
def flip_bit(data, pos):
    data = list(data)
    index = len(data) - pos
    if index < 0 or index >= len(data):
        return ''.join(data)
    data[index] = '1' if data[index] == '0' else '0'
    return ''.join(data)

# Ana GUI sınıfı
class HammingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hamming SEC-DED Code Simulator")
        self.root.geometry("570x480")
        self.root.minsize(460, 400)
        self.root.configure(bg=color)

        self.data_length = tk.IntVar(value=8)

        self.init_ui()

        try:
            icon = PhotoImage(file="settings.ico")
            root.iconphoto(True, icon)
        except:
            pass

    def init_ui(self):
        self.center_frame = tk.Frame(self.root, bg=color)
        self.center_frame.pack(expand=True)

        tk.Label(self.center_frame, text="Select Data Length:", font=("Arial", 14), bg=color, fg="white").pack(pady=10)

        frame = tk.Frame(self.center_frame, bg=color)
        frame.pack()

        for length in [4, 8, 16, 32, 64]:
            tk.Radiobutton(
                frame, text=f"{length} bits", variable=self.data_length,
                value=length, bg=color, fg="white", font=("Arial", 12),
                selectcolor=color
            ).pack(side=tk.LEFT, padx=10)

        tk.Label(self.center_frame, text="Enter Binary Data", font=("Arial", 12), bg=color, fg="white").pack(pady=10)
        self.entry = tk.Entry(self.center_frame, width=40, font=("Courier", 12))
        self.entry.pack()

        self.encode_button = tk.Button(self.center_frame, text="Generate Hamming Code", font=("Arial", 12), command=self.encode_data)
        self.encode_button.pack(pady=15)

        tk.Label(self.center_frame, text="Flip bit at position", font=("Arial", 12), bg=color, fg="white").pack()
        self.error_entry = tk.Entry(self.center_frame, width=10, font=("Courier", 12))
        self.error_entry.pack()

        self.error_button = tk.Button(self.center_frame, text="Inject Error and Correct", font=("Arial", 12), command=self.add_error)
        self.error_button.pack(pady=15)

        self.result_label = tk.Label(self.center_frame, text="", bg=color, fg="black", font=("Courier", 12), justify="left")
        self.result_label.pack(pady=10)

        # Sağ üst köşeye kare şekilli yardım butonu (30x30 px)
        help_button = tk.Button(
            self.root,
            text="?",
            font=("Arial", 16),
            fg="black",
            bg="white",
            relief="raised",
            bd=2,
            command=self.show_help
        )
        help_button.place(relx=1.0, rely=0.0, x=-10, y=10, width=30, height=30, anchor="ne")

    def encode_data(self):
        data = self.entry.get()
        expected_len = self.data_length.get()

        if len(data) != expected_len or not all(c in '01' for c in data):
            messagebox.showerror("Error", f"Please enter exactly {expected_len} bits of binary data.")
            return

        self.encoded_data = calculate_parity_bits(data)
        self.result_label.config(text=f"Hamming Code: {self.encoded_data}")

        with open("hamming_log.txt", "a") as f:
            f.write("=== Hamming Code Generation ===\n")
            f.write(f"Original Data: {data}\n")
            f.write(f"Generated Hamming Code: {self.encoded_data}\n\n")

    def add_error(self):
        if not hasattr(self, 'encoded_data'):
            messagebox.showerror("Error", "Please generate Hamming code first.")
            return

        try:
            bit_pos = int(self.error_entry.get())
        except:
            messagebox.showerror("Error", "Please enter a valid bit position.")
            return

        self.corrupted_data = flip_bit(self.encoded_data, bit_pos)
        syndrome_decimal, syndrome_binary = detect_error(self.corrupted_data)

        if syndrome_decimal != 0:
            corrected = flip_bit(self.corrupted_data, syndrome_decimal)
            message = (
                f"Corrupted Data: {self.corrupted_data}\n"
                f"Syndrome (binary): {syndrome_binary}\n"
                f"Syndrome (position): {syndrome_decimal}\n"
                f"Corrected Data: {corrected}"
            )
        else:
            message = (
                f"No Error Detected:\n"
                f"Data: {self.corrupted_data}\n"
                f"Syndrome (binary): {syndrome_binary}"
            )

        self.result_label.config(text=message)

        with open("hamming_log.txt", "a") as f:
            f.write("=== Error Injection & Correction ===\n")
            f.write(f"Injected Error at Bit Position: {bit_pos}\n")
            f.write(f"Corrupted Data: {self.corrupted_data}\n")
            f.write(f"Syndrome (binary): {syndrome_binary}\n")
            f.write(f"Syndrome (decimal): {syndrome_decimal}\n")
            if syndrome_decimal != 0:
                f.write(f"Corrected Data: {corrected}\n")
            f.write("\n")

    def show_help(self):
        messagebox.showinfo(
            "Help",
            "This application simulates Hamming SEC-DED coding.\n\n"
            "1. Select the length of your binary data.\n"
            "2. Enter your binary data accordingly.\n"
            "3. Click 'Generate Hamming Code' to get the encoded data.\n"
            "4. Optionally, flip a bit by entering its position (1 = rightmost) and inject an error.\n"
            "5. The program will detect and correct the error if possible."
        )

# Uygulamayı başlat
if __name__ == "__main__":
    root = tk.Tk()
    app = HammingApp(root)
    root.mainloop()