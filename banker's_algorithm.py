import tkinter as tk
from tkinter import messagebox
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DeadlockToolkit:
    def __init__(self, root):
        self.root = root
        self.root.title("Deadlock Prevention & Recovery Toolkit")
        self.root.geometry("1000x700")

        self.num_processes = 0
        self.num_resources = 0
        self.current_phase = "allocation"
        self.allocation = []
        self.max_demand = []
        self.available = []

        self.frame = tk.Frame(root, padx=20, pady=20)
        self.frame.pack(expand=True)

        self.label = tk.Label(self.frame, text="Enter number of processes:", font=("Arial", 14))
        self.label.grid(row=0, column=0, padx=10, pady=10)

        self.entry = tk.Entry(self.frame, font=("Arial", 14))
        self.entry.grid(row=0, column=1, padx=10, pady=10)

        self.button_next = tk.Button(self.frame, text="Next", font=("Arial", 14), command=self.next_step)
        self.button_next.grid(row=1, columnspan=2, pady=20)

        self.canvas = None

    def next_step(self):
        if self.label.cget("text") == "Enter number of processes:":
            self.num_processes = int(self.entry.get())
            self.label.config(text="Enter number of resources:")
            self.entry.delete(0, tk.END)
        elif self.label.cget("text") == "Enter number of resources:":
            self.num_resources = int(self.entry.get())
            self.label.config(text=f"Enter allocated resources for Process 0 (comma-separated):")
            self.entry.delete(0, tk.END)
            self.allocation = []
        elif self.current_phase == "allocation":
            values = list(map(int, self.entry.get().split(',')))
            if len(values) != self.num_resources:
                messagebox.showerror("Error", "Incorrect number of values.")
                return
            self.allocation.append(values)
            self.entry.delete(0, tk.END)

            if len(self.allocation) < self.num_processes:
                self.label.config(text=f"Enter allocated resources for Process {len(self.allocation)} (comma-separated):")
            else:
                self.label.config(text=f"Enter maximum demand for Process 0 (comma-separated):")
                self.current_phase = "max_demand"
                self.max_demand = []
        elif self.current_phase == "max_demand":
            values = list(map(int, self.entry.get().split(',')))
            if len(values) != self.num_resources:
                messagebox.showerror("Error", "Incorrect number of values.")
                return
            self.max_demand.append(values)
            self.entry.delete(0, tk.END)

            if len(self.max_demand) < self.num_processes:
                self.label.config(text=f"Enter maximum demand for Process {len(self.max_demand)} (comma-separated):")
            else:
                self.label.config(text="Enter available resources (comma-separated):")
                self.current_phase = "available"
        elif self.current_phase == "available":
            self.available = list(map(int, self.entry.get().split(',')))
            if len(self.available) != self.num_resources:
                messagebox.showerror("Error", "Incorrect number of values.")
                return
            self.entry.grid_forget()
            self.button_next.grid_forget()
            self.show_menu()

    def show_menu(self):
        self.label.config(text="Select an operation:")

        self.button_safe = tk.Button(self.frame, text="Check Safety", font=("Arial", 14), command=self.check_safety)
        self.button_safe.grid(row=2, columnspan=2, pady=10)

        self.button_recover = tk.Button(self.frame, text="Recover from Deadlock", font=("Arial", 14), command=self.recover_from_deadlock)
        self.button_recover.grid(row=3, columnspan=2, pady=10)

        self.button_reset = tk.Button(self.frame, text="Restart", font=("Arial", 14), command=self.reset_toolkit)
        self.button_reset.grid(row=4, columnspan=2, pady=10)

        self.draw_graph()

    def check_safety(self):
        allocation = np.array(self.allocation)
        max_demand = np.array(self.max_demand)
        available = np.array(self.available)
        n, m = allocation.shape

        need = max_demand - allocation
        work = available.copy()
        finish = np.zeros(n, dtype=bool)
        safe_sequence = []

        while len(safe_sequence) < n:
            found = False
            for i in range(n):
                if not finish[i] and all(need[i] <= work):
                    work += allocation[i]
                    finish[i] = True
                    safe_sequence.append(i)
                    found = True
                    break
            if not found:
                messagebox.showerror("Result", "Unsafe State. Deadlock possible!")
                return

        messagebox.showinfo("Result", f"Safe State. Safe Sequence: {safe_sequence}")

    def recover_from_deadlock(self):
        allocation = np.array(self.allocation)
        max_demand = np.array(self.max_demand)
        available = np.array(self.available)
        n, m = allocation.shape

        need = max_demand - allocation
        work = available.copy()

        for i in range(n):
            if all(need[i] <= work):
                messagebox.showinfo("Recovery", f"The deadlock is already safe. Process {i} is safe.")
                return

        max_alloc_idx = np.argmax(np.sum(allocation, axis=1))
        available += allocation[max_alloc_idx]
        self.allocation[max_alloc_idx] = [0]*m
        self.available = list(available)
        self.draw_graph()
        messagebox.showinfo("Recovery", f"Recovered from deadlock by preempting Process {max_alloc_idx}.")

    def draw_graph(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        G = nx.DiGraph()

        for i in range(self.num_processes):
            G.add_node(f"P{i}", color='lightblue')
        for j in range(self.num_resources):
            G.add_node(f"R{j}", color='lightgreen')

        for i, alloc in enumerate(self.allocation):
            for j, val in enumerate(alloc):
                if val > 0:
                    G.add_edge(f"R{j}", f"P{i}")

        for i, need in enumerate(np.array(self.max_demand) - np.array(self.allocation)):
            for j, val in enumerate(need):
                if val > 0:
                    G.add_edge(f"P{i}", f"R{j}")

        colors = [G.nodes[n]['color'] for n in G.nodes()]
        pos = nx.spring_layout(G)

        fig, ax = plt.subplots(figsize=(6, 5))
        nx.draw(G, pos, with_labels=True, arrows=True, node_color=colors, ax=ax)
        self.canvas = FigureCanvasTkAgg(fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=7, columnspan=2, pady=20)

    def reset_toolkit(self):
        self.frame.destroy()
        self.__init__(self.root)

root = tk.Tk()
app = DeadlockToolkit(root)
root.mainloop()
