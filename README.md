# deadlockdetector
# Banker’s Algorithm — Detection & Prevention of Deadlocks
The Banker’s Algorithm is used in operating systems to avoid deadlocks by making sure the system always stays in a safe state.
It was designed by Edsger Dijkstra and works similar to a bank giving out loans—hence the name.
# Why Deadlocks Happen
Deadlocks occur when processes are waiting on each other and none of them can proceed.
To avoid this, the OS must check before allocating resources whether the system will remain safe.
# Deadlock Prevention Using Banker’s Algorithm
To prevent deadlock, the algorithm checks safety before allocation.
🔹 Key Data Structures
Let:
Max → Maximum demand of each process
Allocation → Currently allocated resources
Need = Max − Allocation → How much more the process may ask for
Available → Resources currently free
# Deadlock Detection Using Banker’s Algorithm
Deadlock detection uses a similar idea but applied after allocation, not before.
🔹 How Detection Works
Pretend all current allocations have already happened.
Run the same safety algorithm.
If some processes cannot finish → those processes are in deadlock.
✔ Outcome:
You detect which processes are stuck and cannot proceed.
