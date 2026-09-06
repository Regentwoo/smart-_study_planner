"""
Smart Study Planner
--------------------
A console-based Python programme that helps a student log, review and
analyse study sessions across different subjects over a semester.

Data persists across runs in a plain-text file called 'study_log.txt'.

Author: <Your Name>
"""

import os

# Name of the file used to persist session data between runs.
DATA_FILE = "study_log.txt"

# The delimiter used to separate fields when a session is written to
# the text file. A pipe character is used because it is very unlikely
# to appear naturally inside a subject/topic/date the user types.
DELIMITER = "|"


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------
def classify_session(duration):
    """
    Classify a study session based on its duration (in minutes).

    Rules:
        < 30 minutes         -> "Short"
        30 to 90 minutes     -> "Medium"
        > 90 minutes         -> "Long"

    This function is reused everywhere a session's length needs to be
    labelled, so the classification logic only ever lives in one place.
    """
    if duration < 30:
        return "Short"
    elif duration <= 90:
        return "Medium"
    else:
        return "Long"


# ---------------------------------------------------------------------------
# Persistence: save_sessions() / load_sessions()
# ---------------------------------------------------------------------------
def save_sessions(sessions):
    """
    Save every session in the 'sessions' list to DATA_FILE.
    Each session is written as one line: subject|topic|date|duration
    This function overwrites the file with the current, full list of
    sessions, so it can simply be called once whenever the user exits.
    """
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            for session in sessions:
                line = DELIMITER.join([
                    session["subject"],
                    session["topic"],
                    session["date"],
                    str(session["duration"])
                ])
                file.write(line + "\n")
        print(f"Sessions saved successfully to '{DATA_FILE}'.")
    except OSError as error:
        # Catch file-system errors (e.g. permissions) so the programme
        # never crashes just because it could not write the file.
        print(f"Warning: could not save sessions ({error}).")


def load_sessions():
    """
    Load sessions from DATA_FILE if it exists and return them as a list
    of dictionaries. If the file does not exist yet (e.g. first ever
    run of the programme), simply return an empty list instead of
    crashing.
    """
    sessions = []

    # Guard clause: if there is no saved file yet, there is nothing to
    # load, so we return an empty list straight away.
    if not os.path.exists(DATA_FILE):
        return sessions

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue  # skip any blank lines

                parts = line.split(DELIMITER)
                # Only accept well-formed lines with exactly 4 fields;
                # this protects against a corrupted or hand-edited file.
                if len(parts) != 4:
                    continue

                subject, topic, date, duration_str = parts
                try:
                    duration = float(duration_str)
                except ValueError:
                    continue  # skip lines with an unreadable duration

                sessions.append({
                    "subject": subject,
                    "topic": topic,
                    "date": date,
                    "duration": duration
                })
    except OSError as error:
        print(f"Warning: could not read '{DATA_FILE}' ({error}). "
              "Starting with an empty session list.")

    return sessions


# ---------------------------------------------------------------------------
# Adding sessions
# ---------------------------------------------------------------------------
def get_positive_duration():
    """
    Repeatedly prompt the user for a session duration (in minutes)
    until a valid positive number is entered. Returns the duration
    as a float.
    """
    while True:
        raw_value = input("Duration in minutes: ").strip()
        try:
            duration = float(raw_value)
            if duration > 0:
                return duration
            else:
                print("Duration must be a positive number. Please try again.")
        except ValueError:
            print("That is not a valid number. Please try again.")


def add_session(sessions):
    """
    Prompt the user for the details of a new study session (subject,
    topic, date/day label and duration), validate the duration, and
    append the new session as a dictionary to the 'sessions' list.
    """
    print("\n--- Add a Study Session ---")
    subject = input("Subject: ").strip()
    topic = input("Topic covered: ").strip()
    date = input("Date / day (e.g. 'Mon 12 Aug'): ").strip()
    duration = get_positive_duration()

    session = {
        "subject": subject,
        "topic": topic,
        "date": date,
        "duration": duration
    }
    sessions.append(session)
    print(f"Session added! ({classify_session(duration)} session, "
          f"{duration:.0f} minutes)\n")


# ---------------------------------------------------------------------------
# Viewing sessions
# ---------------------------------------------------------------------------
def print_session_table(sessions):
    """
    Print a neatly formatted table of the given sessions, including
    each one's Short/Medium/Long classification. This helper is used
    by both view_sessions() and search_by_subject() so the table
    formatting only needs to be written once.
    """
    header = f"{'Subject':<15}{'Topic':<20}{'Date':<15}{'Duration':<12}{'Type':<8}"
    print(header)
    print("-" * len(header))

    for session in sessions:
        classification = classify_session(session["duration"])
        print(f"{session['subject']:<15}"
              f"{session['topic']:<20}"
              f"{session['date']:<15}"
              f"{str(session['duration']) + ' min':<12}"
              f"{classification:<8}")


def view_sessions(sessions):
    """
    Display every logged session in a formatted table. Handles the
    case where no sessions have been logged yet.
    """
    print("\n--- All Study Sessions ---")
    if not sessions:
        print("No sessions have been logged yet.\n")
        return

    print_session_table(sessions)
    print()


# ---------------------------------------------------------------------------
# Searching by subject
# ---------------------------------------------------------------------------
def search_by_subject(sessions):
    """
    Ask the user for a subject name and display only the sessions
    recorded for that subject (case-insensitive match), along with
    the total time spent on it. Shows a clear message if nothing is
    found instead of an empty table.
    """
    print("\n--- Search Sessions by Subject ---")
    query = input("Enter subject to search for: ").strip()

    # Case-insensitive comparison: normalise both sides to lower case.
    matches = [s for s in sessions if s["subject"].lower() == query.lower()]

    if not matches:
        print(f"No sessions found for subject '{query}'.\n")
        return

    print_session_table(matches)
    total_minutes = sum(s["duration"] for s in matches)
    print(f"\nTotal time spent on '{query}': "
          f"{total_minutes:.0f} minutes ({total_minutes / 60:.2f} hours)\n")


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------
def study_statistics(sessions):
    """
    Compute and display:
      - total hours studied overall
      - total hours studied per subject
      - the subject with the least total study time (weakest area)
      - the single longest session recorded
    """
    print("\n--- Study Statistics ---")
    if not sessions:
        print("No sessions have been logged yet, so there are no "
              "statistics to show.\n")
        return

    # Build a dictionary mapping subject -> total minutes studied.
    totals_by_subject = {}
    for session in sessions:
        subject = session["subject"]
        totals_by_subject[subject] = totals_by_subject.get(subject, 0) + session["duration"]

    total_minutes_overall = sum(totals_by_subject.values())
    print(f"Total time studied overall: "
          f"{total_minutes_overall:.0f} minutes "
          f"({total_minutes_overall / 60:.2f} hours)\n")

    print("Time studied per subject:")
    for subject, minutes in totals_by_subject.items():
        print(f"  {subject:<15}{minutes:.0f} minutes ({minutes / 60:.2f} hours)")

    # The subject with the least total study time is the weakest area.
    weakest_subject = min(totals_by_subject, key=totals_by_subject.get)
    print(f"\nWeakest area (least total study time): {weakest_subject} "
          f"({totals_by_subject[weakest_subject]:.0f} minutes)")

    # The single longest session recorded, found using max() with a key.
    longest_session = max(sessions, key=lambda s: s["duration"])
    print("Longest single session:")
    print(f"  Subject : {longest_session['subject']}")
    print(f"  Topic   : {longest_session['topic']}")
    print(f"  Date    : {longest_session['date']}")
    print(f"  Duration: {longest_session['duration']:.0f} minutes "
          f"({classify_session(longest_session['duration'])})\n")


# ---------------------------------------------------------------------------
# Menu / main programme loop
# ---------------------------------------------------------------------------
def display_menu():
    """Print the main menu options."""
    print("=" * 40)
    print("        SMART STUDY PLANNER")
    print("=" * 40)
    print("1. Add a study session")
    print("2. View all sessions")
    print("3. Search sessions by subject")
    print("4. View statistics")
    print("5. Save and exit")
    print("=" * 40)


def main():
    """
    Main programme loop. Loads any existing sessions on startup,
    repeatedly shows the menu and routes the user's choice to the
    appropriate function, and saves all sessions before exiting.
    """
    sessions = load_sessions()
    if sessions:
        print(f"Loaded {len(sessions)} saved session(s) from '{DATA_FILE}'.")

    while True:
        display_menu()
        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            add_session(sessions)
        elif choice == "2":
            view_sessions(sessions)
        elif choice == "3":
            search_by_subject(sessions)
        elif choice == "4":
            study_statistics(sessions)
        elif choice == "5":
            save_sessions(sessions)
            print("Goodbye! Keep up the good study habits.")
            break
        else:
            # Invalid choices are handled gracefully instead of crashing.
            print("Invalid choice. Please enter a number from 1 to 5.\n")


if __name__ == "__main__":
    main()
