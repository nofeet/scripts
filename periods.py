"""Calculate possible work/break intervals, then optionally pass selection to timer.

USAGE: python work_break_ints.py <finish time> <work-to-break ratio>

  finish time: Time in 24H format when to finish working. (e.g., 18:00)
  work-to-break ratio: (Optional) Number of minutes of work per minute of break
                       Default is 5.
"""

import datetime
import os
import subprocess
import sys

#--- Constants
# Default ratio: How many minutes of work per minute of break?
DEF_RATIO = 5
# Multiply this with the total minutes before calculating intervals.
# I find that I sometimes need a bit more time to wrap up a work or break
# period. Setting this value to something below 1 (like 0.95) tries to
# compensate for that.
FUDGE_FACTOR = 1
# Path to timer program.
WORK_TIMER_EXE = "c:\Program Files\InstantBoss\InstantBoss.exe"


#--- Functions

def calculate_periods(stop_time, work_to_break_ratio):
    """Return a list of work/break interval options

    @param stop_time: When to stop working in 24-hour format. (string)
    @param work_to_break_ratio: Number of work minutes per break minute. (int)

    Each item in list is tuple of (work minutes, break minutes, # of intervals)
    """
    now = datetime.datetime.now()
    endtime = datetime.datetime.strptime(stop_time, "%H:%M")
    delta = endtime - now
    minutes = (delta.seconds / 60) * FUDGE_FACTOR

    choices = []

    # Make 20 passes at finding work/break intervals.
    # Each pass represents 1 work interval.
    for i in range(1, 20):
        numtries = 0
        breaklen = int(round(minutes / (i * work_to_break_ratio + i - 1)))
        worklen = int(round(breaklen * work_to_break_ratio))
        totaltime = worklen * i + breaklen * (i - 1)
        while totaltime > minutes:
            # Total time of these intervals exceeds what we actually have.
            # We'll have to cut back a bit.
            numtries += 1
            if numtries % 3:
                # 2 in 3 tries: reduce work length by 1 minute
                worklen -= 1
            else:
                # 1 in 3 tries: reduce break length by 1 minute
                breaklen -= 1
            totaltime = worklen * i + breaklen * (i - 1)
        if worklen < 19:
            # Give up once we start trying to find work intervals less than
            # 19 minutes.
            break
        choices.append((worklen, breaklen, i))

    return choices


def display_intervals(choices):
    """Display table with the choices for work/break intervals.

    @param choices: sequence of options, each containing (work mins, break mins, # intervals)
    """
    print("CHOICE\tWORK\tBREAK\tPERIODS\tT.WORK\tT.BREAK\tTOTAL TIME")
    for (choice_num, (worklen, breaklen, num_intervals)) in enumerate(choices):
        totaltime = worklen * num_intervals + breaklen * (num_intervals - 1)
        print("%d\t%d\t%d\t%d\t%d\t%d\t%d" % (choice_num + 1,
                                              worklen,
                                              num_intervals - 1 and breaklen,
                                              num_intervals,
                                              num_intervals * worklen,
                                              (num_intervals - 1) * breaklen,
                                              totaltime))


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 1:
        # Only the stop time was given.
        stop_time = sys.argv[1]
        work_to_break_ratio = DEF_RATIO
    elif len(args) == 2:
        # Ratio given, too.
        (stop_time, work_to_break_ratio) = sys.argv[1:3]
    else:
        print("\nERROR: Wrong number of arguments given.\n")
        print(__doc__)
        sys.exit()

    choices = calculate_periods(stop_time, int(work_to_break_ratio))
    display_intervals(choices)
    if os.path.exists(WORK_TIMER_EXE):
        # Instant Boss (or another work timer) is installed.
        # Pass chosen interval values.
        choice = int(input("CHOOSE: ")) - 1
        (work_len, break_len, work_intervals) = choices[choice]
        subprocess.call([WORK_TIMER_EXE, work_len, break_len, work_intervals],
                        shell=True)
