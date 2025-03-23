import tkinter as tk
from tkinter import messagebox
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

class DeadlockToolkit:
    def __init__(self, root):
        self.root = root
        self.root.title("Deadlock Prevention & Recovery Toolkit")
        self.root.geometry("800x600")

        self.num_processes = 0
        self.num_resources = 0
        self.current_process = 0
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

        self.button_graph = tk.Button(self.frame, text="Show Resource Graph", font=("Arial", 14), command=self.show_graph)
        self.button_graph.grid(row=3, columnspan=2, pady=10)

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

    def show_graph(self):
        G = nx.DiGraph()
        for i in range(self.num_processes):
            G.add_node(f"P{i}", color='blue')

        for j in range(self.num_resources):
            G.add_node(f"R{j}", color='red')

        allocation = np.array(self.allocation)
        for i in range(self.num_processes):
            for j in range(self.num_resources):
                if allocation[i][j] > 0:
                    G.add_edge(f"R{j}", f"P{i}")

        need = np.array(self.max_demand) - allocation
        for i in range(self.num_processes):
            for j in range(self.num_resources):
                if need[i][j] > 0:
                    G.add_edge(f"P{i}", f"R{j}")

        colors = [G.nodes[node]['color'] for node in G.nodes]
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color=colors, node_size=2000, font_size=12)
        plt.show()

root = tk.Tk()
app = DeadlockToolkit(root)
root.mainloop()
