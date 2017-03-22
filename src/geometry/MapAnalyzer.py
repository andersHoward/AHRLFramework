"""Module full of goodies to test, post-process, and visualize generated maps."""


def is_map_solvable():
    """Is it possible to get from the entrance to the exit?"""
    pass

def mark_rooms():
    """Tag rooms with various qualities so we can key off of our room tags for such things as entity placement.
        Returns:
            seclusion_value: the more off-the-beaten-path a room is, the higher value treasure (see Kyzrati).

    """
    pass

def count_rooms():
    """Count the number of structural(building) and natural(cave) rooms."""
    pass

def gather_map_metrics():
    """Parent function that runs other analysis functions and returns a standardized list of metric to test."""
    pass

def test_map_metrics():
    """Calls gather_map_metrics, then runs comparisons on the data."""
    pass

def run_post_process_rules():
    """Based on test outcome, tweak individual cells based on some rule set."""
    pass
