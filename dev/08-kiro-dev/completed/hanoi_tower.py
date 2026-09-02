"""
Tower of Hanoi puzzle solving Agent

This module implements an AI Agent that solves the Tower of Hanoi puzzle using the Strands SDK.
"""

import os
from typing import List, Tuple
from strands import Agent
from strands.tools import tool
from strands.telemetry import StrandsTelemetry


# OTLP configuration
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4318"

strands_telemetry = StrandsTelemetry()
strands_telemetry.setup_otlp_exporter()


# Global variable holding the Tower of Hanoi state
hanoi_state = {
    "A": [],
    "B": [],
    "C": [],
    "moves": []
}


@tool
def initialize_hanoi(n: int) -> str:
    """
    Initializes the Tower of Hanoi.

    Args:
        n: Number of disks (1-10)

    Returns:
        Initialization result message
    """
    if n < 1 or n > 10:
        return "The number of disks must be between 1 and 10."

    global hanoi_state
    hanoi_state = {
        "A": list(range(n, 0, -1)),  # [n, n-1, ..., 2, 1]
        "B": [],
        "C": [],
        "moves": []
    }

    return f"Tower of Hanoi initialized. Rod A has {n} disks.\nCurrent state: {get_current_state()}"


@tool
def move_disk(from_rod: str, to_rod: str) -> str:
    """
    Moves a disk from one rod to another.

    Args:
        from_rod: Source rod (one of A, B, C)
        to_rod: Destination rod (one of A, B, C)

    Returns:
        Move result message
    """
    global hanoi_state

    # Validate input
    if from_rod not in ["A", "B", "C"] or to_rod not in ["A", "B", "C"]:
        return "A rod must be one of A, B, C."

    if from_rod == to_rod:
        return "Cannot move to the same rod."

    # Check whether the source rod is empty
    if not hanoi_state[from_rod]:
        return f"Rod {from_rod} has no disks."

    # Disk to move
    disk = hanoi_state[from_rod][-1]

    # Check whether the destination rod holds a smaller disk
    if hanoi_state[to_rod] and hanoi_state[to_rod][-1] < disk:
        return f"Cannot place a larger disk on top of a smaller one. (Tried to place disk {disk} on disk {hanoi_state[to_rod][-1]} of rod {to_rod})"

    # Move the disk
    hanoi_state[from_rod].pop()
    hanoi_state[to_rod].append(disk)
    hanoi_state["moves"].append((from_rod, to_rod))

    move_count = len(hanoi_state["moves"])
    return f"Move {move_count}: Moved disk {disk} from rod {from_rod} to rod {to_rod}.\nCurrent state: {get_current_state()}"


@tool
def get_current_state() -> str:
    """
    Returns the current state of the Tower of Hanoi.

    Returns:
        A string representing the current state
    """
    global hanoi_state

    state_str = f"""
Rod A: {hanoi_state['A']}
Rod B: {hanoi_state['B']}
Rod C: {hanoi_state['C']}
Total moves: {len(hanoi_state['moves'])}
"""
    return state_str.strip()


@tool
def check_solution() -> str:
    """
    Checks whether the puzzle has been solved.

    Returns:
        Solution status message
    """
    global hanoi_state

    # Check that all disks are on rod C in the correct order
    if not hanoi_state["C"]:
        return "Not solved yet. Rod C is empty."

    if hanoi_state["A"] or hanoi_state["B"]:
        return "Not solved yet. All disks must be moved to rod C."

    # Check that the disks are in the correct order (largest to smallest)
    disks = hanoi_state["C"]
    if disks == sorted(disks, reverse=True):
        total_moves = len(hanoi_state["moves"])
        n = len(disks)
        optimal_moves = 2**n - 1
        return f"Congratulations! You solved the puzzle in {total_moves} moves. (Optimal: {optimal_moves} moves)"

    return "The disks are not in the correct order."


@tool
def get_hint(n: int) -> str:
    """
    Provides a hint for solving the Tower of Hanoi puzzle.

    Args:
        n: Number of disks

    Returns:
        Hint message
    """
    optimal_moves = 2**n - 1
    hint = f"""
Tower of Hanoi solving strategy:
1. Moving n disks takes at least {optimal_moves} moves.
2. Recursive approach:
   - Move n-1 disks to the auxiliary rod
   - Move the largest disk to the target rod
   - Move the n-1 disks to the target rod
3. Rule: a larger disk cannot be placed on top of a smaller one.
"""
    return hint.strip()


def main():
    """Runs the Tower of Hanoi Agent."""

    # Create the Agent
    agent = Agent(
        name="hanoi_tower_solver",
        model="us.anthropic.claude-sonnet-4-20250514-v1:0",
        system_prompt="""You are an expert AI assistant that solves the Tower of Hanoi puzzle.

Tower of Hanoi rules:
- There are three rods (A, B, C)
- Initially all disks are stacked on rod A in size order (largest at the bottom)
- The goal is to move all disks to rod C
- Only one disk can be moved at a time
- A larger disk cannot be placed on top of a smaller one

When the user specifies the number of disks:
1. Initialize the puzzle with initialize_hanoi
2. Move disks using move_disk
3. Check the state after each move
4. Verify completion with check_solution

Use a recursive algorithm to find the optimal solution.
Explain each step clearly as you go.""",
        tools=[
            initialize_hanoi,
            move_disk,
            get_current_state,
            check_solution,
            get_hint
        ]
    )

    try:
        print("=" * 60)
        print("Tower of Hanoi Puzzle Solving Agent")
        print("=" * 60)

        # User input
        n = int(input("\nEnter the number of disks (1-10): "))

        if n < 1 or n > 10:
            print("The number of disks must be between 1 and 10.")
            return

        print(f"\nStarting the Tower of Hanoi puzzle with {n} disks...\n")

        # Run the Agent
        response = agent(f"Please solve the Tower of Hanoi puzzle with {n} disks. Explain each step as you go.")

        print("\n" + "=" * 60)
        print("Agent response:")
        print("=" * 60)
        print(response)

    except KeyboardInterrupt:
        print("\n\nProgram interrupted.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    main()
