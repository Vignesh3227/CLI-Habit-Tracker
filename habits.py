from datetime import datetime, timedelta
import json
import os
from contextlib import contextmanager
import time

class PersistenceError(Exception):
    """Raised when saving/loading habits fails."""
    pass

@contextmanager
def timer(label):
    start=time.time()
    try:
        yield
    finally:
        print(f"{label}: {time.time() - start:.2f}s")

class Habit:
    def __init__(self, name, description):
        self.name=name
        self.description=description
        self.__history=[]
    def mark_done(self, date):
        if date not in self.__history:
            self.__history.append(date)
            self.__history.sort(reverse=True)
    def streak(self):
        if not self.__history:
            return 0
        sort_history=sorted([datetime.strptime(d,"%Y-%m-%d") for d in self.__history], reverse=True)
        streak=1
        for i in range(1, len(sort_history)):
            if (sort_history[i-1]-sort_history[i]==timedelta(days=1)):
                streak+=1
            else:
                break
        return streak
    def get_history(self):
        return list(self.__history)
    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "history": self.get_history()
        }
    @classmethod
    def from_dict(cls, data):
        habit=cls(data["name"], data["description"])
        for date in data.get("history", []):
            habit.mark_done(date)
        return habit
    def __str__(self):
        return f"\nHabit: {self.name}\n Description: {self.description}\n Streak: {self.streak()}\n"

class HabitTracker(Habit):
    DATE_FORMAT="%Y-%m-%d"

    def __init__(self):
        self.habits={}
    def add_habit(self, name, desc):
        if name in self.habits:
            print("Already exists")
        else:
            self.habits[name]=Habit(name,desc)
    def remove_habit(self,name):
        if name in self.habits:
            del self.habits[name]
        else:
            print("None found")
    def mark_done(self, name, date):
        if name not in self.habits:
            return
        if not date:
            date= datetime.today().strftime(self.DATE_FORMAT)
        try:
            datetime.strptime(date, self.DATE_FORMAT)
        except ValueError:
            return
        self.habits[name].mark_done(date)
    def list_habits(self):
        return list(self.habits.values())
    def report(self):
        return {name: habit.streak() for name, habit in self.habits.items()}
    def save(self, filename):
        try:
            with open(filename, "w") as f:
                json.dump({name: habit.to_dict() for name, habit in self.habits.items()}, f, indent=2)
        except OSError as e:
            raise PersistenceError(f"Failed to save: {e}")
    def load(self, filename):
        if not os.path.exists(filename):
            print("File not found. Starting with empty tracker.")
            return
        try:
            with open(filename, "r") as f:
                data=json.load(f)
                self.habits={name: Habit.from_dict(h) for name, h in data.items()}
        except json.JSONDecodeError as e:
            raise PersistenceError(f"Failed to load: {e}")
    def __add__(self,other):
        new_tracker=HabitTracker()
        new_tracker.habits={**self.habits}
        for name, habit in other.habits.items():
            if name not in new_tracker.habits:
                new_tracker.habits[name]=habit
            else:
                combined=list(set(
                    new_tracker.habits[name].get_history() +
                    habit.get_history()
                ))
                for date in combined:
                    new_tracker.habits[name].mark_done(date)
        return new_tracker
