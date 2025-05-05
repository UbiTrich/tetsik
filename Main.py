from datetime import datetime, timedelta
import json
import os
from functools import wraps
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_action(func):
    """Decorator for logging actions performed on events"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Calling {func.__name__} with {args[1:]} {kwargs}")
        result = func(*args, **kwargs)
        logging.info(f"Function {func.__name__} completed successfully")
        return result
    return wrapper

def validate_date_format(func):
    """Decorator for validating date formats"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Check if args[1] and/or args[2] are dates in string format
            if len(args) > 1 and isinstance(args[1], str):
                datetime.strptime(args[1], "%Y-%m-%d %H:%M")
            if len(args) > 2 and isinstance(args[2], str):
                datetime.strptime(args[2], "%Y-%m-%d %H:%M")
        except ValueError:
            logging.error("Invalid date format. Use YYYY-MM-DD HH:MM")
            raise ValueError("Invalid date format. Use YYYY-MM-DD HH:MM")
        return func(*args, **kwargs)
    return wrapper

class Event:
    def __init__(self, title, start_time, end_time=None, location="", description="", keywords=None):
        self.title = title
        self.start_time = start_time  # Can be a datetime or date object
        self.end_time = end_time      # Can be None (for all-day), or a datetime/date
        self.location = location
        self.description = description
        self.keywords = keywords if keywords else []
        self.id = None  # Will be set when added to the calendar
    
    def is_all_day(self):
        """Check if the event is an all-day event"""
        if isinstance(self.start_time, str):
            start = datetime.strptime(self.start_time, "%Y-%m-%d %H:%M")
            if not self.end_time:
                return start.hour == 0 and start.minute == 0
            else:
                end = datetime.strptime(self.end_time, "%Y-%m-%d %H:%M")
                return (start.hour == 0 and start.minute == 0 and 
                      end.hour == 23 and end.minute == 59)
        return False
    
    def is_multi_day(self):
        """Check if the event spans multiple days"""
        if not self.end_time:
            return False
            
        if isinstance(self.start_time, str) and isinstance(self.end_time, str):
            start = datetime.strptime(self.start_time, "%Y-%m-%d %H:%M")
            end = datetime.strptime(self.end_time, "%Y-%m-%d %H:%M")
            return start.date() != end.date()
        return False
    
    def to_dict(self):
        """Convert event to dictionary for saving"""
        return {
            "id": self.id,
            "title": self.title,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "location": self.location,
            "description": self.description,
            "keywords": self.keywords
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create event from dictionary"""
        event = cls(
            title=data["title"],
            start_time=data["start_time"],
            end_time=data.get("end_time"),
            location=data.get("location", ""),
            description=data.get("description", ""),
            keywords=data.get("keywords", [])
        )
        event.id = data.get("id")
        return event

class Calendar:
    def __init__(self):
        self.events = []
        self.next_id = 1
        self.filename = "calendar_events.json"
        self.load_events()
    
    def load_events(self):
        """Load events from file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as file:
                    data = json.load(file)
                    self.events = [Event.from_dict(event_data) for event_data in data["events"]]
                    self.next_id = data["next_id"]
            except Exception as e:
                logging.error(f"Error loading events: {e}")
                self.events = []
                self.next_id = 1
    
    def save_events(self):
        """Save events to file"""
        try:
            with open(self.filename, 'w') as file:
                data = {
                    "events": [event.to_dict() for event in self.events],
                    "next_id": self.next_id
                }
                json.dump(data, file, indent=2)
        except Exception as e:
            logging.error(f"Error saving events: {e}")
    
    @log_action
    @validate_date_format
    def add_event(self, title, start_time, end_time=None, location="", description="", keywords=None):
        """Add a new event to the calendar"""
        event = Event(title, start_time, end_time, location, description, keywords)
        event.id = self.next_id
        self.next_id += 1
        self.events.append(event)
        self.save_events()
        return event

    @log_action
    def delete_event(self, event_id):
        """Delete an event by ID"""
        self.events = [event for event in self.events if event.id != event_id]
        self.save_events()
    
    @log_action
    @validate_date_format
    def edit_event(self, event_id, title, start_time, end_time=None, location="", description="", keywords=None):
        """Edit an existing event"""
        for event in self.events:
            if event.id == event_id:
                event.title = title
                event.start_time = start_time
                event.end_time = end_time
                event.location = location
                event.description = description
                event.keywords = keywords if keywords else []
                self.save_events()
                return event
        return None
    
    def get_event(self, event_id):
        """Get an event by ID"""
        for event in self.events:
            if event.id == event_id:
                return event
        return None
    
    def get_upcoming_events(self):
        """Get all upcoming events using comprehension"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        return [event for event in self.events 
                if event.start_time >= now or 
                (event.end_time and event.end_time >= now)]
    
    def get_events_by_keyword(self, keyword):
        """Get events by keyword using comprehension"""
        return [event for event in self.events if keyword.lower() in 
                [kw.lower() for kw in event.keywords]]

# Create a singleton instance of the Calendar
calendar = Calendar()