from habits import HabitTracker, PersistenceError
from datetime import datetime

FILENAME="habits.json"

def print_menu():
    print("\nHabit Tracker Menu\n1. Add new habit\n2. Remove habit\n3. Mark habit done\n4. List all habits\n5. Show streak report\n6. Save & Exit")

def get_choice():
    try:
        choice=int(input("Enter choice (1-6): "))
        if choice not in range(1,7):
            raise ValueError
        return choice
    except ValueError:
        print("Invalid choice. Enter number from 1 to 6.")
        return get_choice()

def get_date_input(dte):
    date=input(dte).strip()
    if not date:
        return datetime.today().strftime(HabitTracker.DATE_FORMAT)
    try:
        datetime.strptime(date,HabitTracker.DATE_FORMAT)
        return date
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        return get_date_input(prompt)

    
tracker=HabitTracker()
try:
    tracker.load(FILENAME)
except PersistenceError as e:
    print(f"Load failed: {e}")
while True:
    print_menu()
    choice=get_choice()
    if choice==1:
        name=input("Enter habit name: ").strip()
        desc=input("Enter description: ").strip()
        tracker.add_habit(name,desc)
    elif choice==2:
        name=input("Enter habit name to remove: ").strip()
        tracker.remove_habit(name)
    elif choice==3:
        name=input("Enter habit name to mark done: ").strip()
        date=get_date_input("Enter date (YYYY-MM-DD) or leave blank for today: ")
        tracker.mark_done(name,date)
    elif choice==4:
        habits=tracker.list_habits()
        if not habits:
            print("No habits added.")
        else:
            for h in habits:
                print(h)
    elif choice==5:
        report=tracker.report()
        if not report:
            print("No streaks to report.")
        else:
            for name,streak in report.items():
                print(f"{name}: {streak} day(s)")
    elif choice==6:
        try:
            tracker.save(FILENAME)
            print("Habits saved.")
        except PersistenceError as e:
            print(f"Save failed: {e}")
        break
