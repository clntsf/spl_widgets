# GENERAL NOTES:

# It is my suggestion (though not enforced by the code) when overriding functions
# to name alternate functions differently to their originals such that multiple alternates
# can be kept in this file and switching between them can be achieved simply by changing the
# line in which the overriding function is set

# It is also recommended to prefix these function names with an underscore (python
# convention for denoting "private" functions, though unenforced) to prevent unwanted
# collision with other functions in these modules.

# The docstrings here are provided mostly for clarity of purpose in their form as
# demonstrations of functionality, but writing them is encouraged when overriding
# functionality as differences between original and alternate functions may be
# subtle (bordering on imperceptible) without explanation


# an example function to demonstrate overriding widget functions programmatically
def _get_second_closest(pool: list, target: float) -> float:
    """
    function _get_second_closest()
    ---
    altered get_closest() function to get the second-closest note to our frequency
    instead, as a demo for overriding functions

    Parameters:
    ---
    pool: list[float] - list of note frequencies to pick from
    target: float - averaged interval frequency to be forced

    Returns:
    ---
    freq: float - the second-closest frequency found in the pool to the target frequency
    """
    return sorted(pool, key=lambda x: abs(x-target))[1]

# here we override spl_widgets.misc_util.get_closest() to patch in our alternate functionality
# NOTE: if we do not want overriding functionality we can comment out or delete this line and
# the program will revert to the original functionality (a restart of the running widget is of course needed)

# get_closest = _get_third_closest


# another example, changing the starting point of our note-to-freq scale to achieve amelodic tuning
def _to_freq_amelodic(note: int) -> float:
    """
    function _to_freq_amelodic()
    ---
    altered to_freq() function which, by changing the base term of
    the geometric series aims to produce amelodic tuned values

    Parameters:
    ---
    note: int - the integer value of a note on the 88-key keyboard, where A1 == 1

    Returns:
    ---
    freq: float - the tuned amelodic frequency
    """
    return 26 * (2 ** ((note - 1) / 12))        # originally 27.5 * (...), see misc_util

# to_freq = _to_freq_amelodic