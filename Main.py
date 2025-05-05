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
        # Log only relevant args/kwargs, excluding 'self'
        func_args = args[1:]
        logging.info(f"Calling {func.__name__} with args: {func_args}, kwargs: {kwargs}")
        try:
            result = func(*args, **kwargs)
            logging.info(f"Function {func.__name__} completed successfully")
            return result
        except Exception as e:
            logging.error(f"Error during {func.__name__}: {e}")
            raise # Re-raise the exception after logging
    return wrapper

def validate_date_format(func):
    """Decorator for validating date formats in specific arguments"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Expected positions: self=args[0], title=args[1], start_time=args[2], end_time=args[3]
        start_time_str = None
        end_time_str = None

        # Get start_time from args or kwargs
        if len(args) > 2:
            start_time_str = args[2]
        elif 'start_time' in kwargs:
            start_time_str = kwargs['start_time']

        # Get end_time from args or kwargs
        if len(args) > 3:
            end_time_str = args[3]
        elif 'end_time' in kwargs:
            end_time_str = kwargs['end_time']

        try:
            # Validate start_time if it's a non-empty string
            if start_time_str and isinstance(start_time_str, str):
                datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")

            # Validate end_time if it's a non-empty string
            if end_time_str and isinstance(end_time_str, str):
                 # Allow end_time to be None or empty string, only validate if provided
                if end_time_str:
                    datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")

        except ValueError:
            error_msg = "Invalid date format. Use YYYY-MM-DD HH:MM"
            logging.error(error_msg)
            raise ValueError(error_msg)

        return func(*args, **kwargs)
    return wrapper

class Event:
    def __init__(self, title, start_time, end_time=None, location="", description="", keywords=None):
        if not title:
             raise ValueError("Event title cannot be empty")
        if not start_time:
             raise ValueError("Event start time cannot be empty")

        self.title = title
        self.start_time = start_time  # Store as string as received
        self.end_time = end_time      # Store as string or None
        self.location = location
        self.description = description
        self.keywords = keywords if keywords else []
        self.id = None  # Will be set when added to the calendar

    def is_all_day(self):
        """Check if the event is an all-day event based on string times"""
        # Check fails if start_time is not a string or has wrong format
        try:
            start = datetime.strptime(self.start_time, "%Y-%m-%d %H:%M")
            # Condition 1: Start at 00:00 and no end time (implicit single all-day)
            # Condition 2: Start at 00:00 and end at 23:59 on the same day
            if start.hour == 0 and start.minute == 0:
                 if not self.end_time:
                     # Could be considered all-day for the start date
                     # Let's stick to the explicit 00:00-23:59 convention for now
                     # return True
                     return False # Keep consistent with GUI toggle logic
                 else:
                     try:
                         end = datetime.strptime(self.end_time, "%Y-%m-%d %H:%M")
                         return start.date() == end.date() and end.hour == 23 and end.minute == 59
                     except (ValueError, TypeError):
                         return False # Invalid end time format
            return False
        except (ValueError, TypeError):
             # If start_time is not a valid string, it's not all-day by this definition
            return False

    def is_multi_day(self):
        """Check if the event spans multiple days based on string times"""
        if not self.end_time:
            return False

        try:
            start = datetime.strptime(self.start_time, "%Y-%m-%d %H:%M")
            end = datetime.strptime(self.end_time, "%Y-%m-%d %H:%M")
            # Check if the date part is different
            return start.date() != end.date()
        except (ValueError, TypeError):
             # Invalid date format strings
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
        # Basic validation for essential fields from dict
        if not data.get("title") or not data.get("start_time"):
             logging.warning(f"Skipping event data due to missing title or start_time: {data.get('id', 'N/A')}")
             return None # Indicate failure to create event

        event = cls(
            title=data["title"],
            start_time=data["start_time"],
            end_time=data.get("end_time"),
            location=data.get("location", ""),
            description=data.get("description", ""),
            keywords=data.get("keywords", [])
        )
        event.id = data.get("id") # ID might be missing in older formats or if saving failed
        # Further validation (like date format) could be added here if needed
        try:
            datetime.strptime(event.start_time, "%Y-%m-%d %H:%M")
            if event.end_time:
                datetime.strptime(event.end_time, "%Y-%m-%d %H:%M")
        except ValueError:
            logging.warning(f"Event {event.id} has invalid date format in loaded data.")
            # Decide how to handle: skip event, try to fix, or load as is?
            # Loading as is, validation will happen during edit/use.

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
                    # Handle empty file case
                    content = file.read()
                    if not content:
                        logging.warning(f"Event file '{self.filename}' is empty.")
                        self.events = []
                        self.next_id = 1
                        return

                    data = json.loads(content)
                    loaded_events = []
                    for event_data in data.get("events", []):
                        event = Event.from_dict(event_data)
                        if event: # Only add if from_dict was successful
                            loaded_events.append(event)
                        else:
                            logging.warning(f"Failed to load event from data: {event_data}")

                    self.events = loaded_events
                    # Ensure next_id is at least max(existing_ids) + 1
                    max_id = 0
                    for e in self.events:
                        if e.id is not None and e.id > max_id:
                            max_id = e.id
                    self.next_id = max(data.get("next_id", 1), max_id + 1)

            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON from {self.filename}: {e}")
                self.events = []
                self.next_id = 1
            except Exception as e:
                logging.error(f"Error loading events from {self.filename}: {e}")
                # Consider backing up the corrupted file here
                self.events = []
                self.next_id = 1
        else:
            logging.info(f"Event file '{self.filename}' not found. Starting fresh.")
            self.events = []
            self.next_id = 1

    def save_events(self):
        """Save events to file"""
        try:
            with open(self.filename, 'w') as file:
                # Ensure all events have an ID before saving
                valid_events = []
                for event in self.events:
                    if event.id is None:
                        logging.warning(f"Event '{event.title}' missing ID before saving. Assigning {self.next_id}.")
                        event.id = self.next_id
                        self.next_id += 1
                    valid_events.append(event.to_dict())

                data = {
                    "events": valid_events,
                    "next_id": self.next_id
                }
                json.dump(data, file, indent=2)
        except TypeError as e:
             logging.error(f"Error serializing event data to JSON: {e}")
        except Exception as e:
            logging.error(f"Error saving events to {self.filename}: {e}")

    @log_action
    @validate_date_format
    def add_event(self, title, start_time, end_time=None, location="", description="", keywords=None):
        """Add a new event to the calendar"""
        # Basic validation already done in Event.__init__ and decorator
        # Ensure end time is not earlier than start time if both provided
        if end_time:
            try:
                start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
                end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
                if end_dt < start_dt:
                    raise ValueError("End time cannot be earlier than start time")
            except ValueError as e: # Catch parsing error or comparison error
                 raise ValueError(f"Date validation error: {e}")


        event = Event(title, start_time, end_time, location, description, keywords)
        event.id = self.next_id
        self.next_id += 1
        self.events.append(event)
        # Sort events after adding, e.g., by start time
        self.events.sort(key=lambda x: x.start_time)
        self.save_events()
        return event

    @log_action
    def delete_event(self, event_id):
        """Delete an event by ID"""
        initial_length = len(self.events)
        self.events = [event for event in self.events if event.id != event_id]
        if len(self.events) < initial_length:
            self.save_events()
            logging.info(f"Event with ID {event_id} deleted.")
            return True
        else:
            logging.warning(f"Event with ID {event_id} not found for deletion.")
            return False

    @log_action
    @validate_date_format
    def edit_event(self, event_id, title, start_time, end_time=None, location="", description="", keywords=None):
        """Edit an existing event"""
        # Ensure end time is not earlier than start time if both provided
        if end_time:
             try:
                 start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
                 end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
                 if end_dt < start_dt:
                     raise ValueError("End time cannot be earlier than start time")
             except ValueError as e: # Catch parsing error or comparison error
                 raise ValueError(f"Date validation error: {e}")

        for event in self.events:
            if event.id == event_id:
                event.title = title
                event.start_time = start_time
                event.end_time = end_time
                event.location = location
                event.description = description
                event.keywords = keywords if keywords else []
                # Re-sort events after editing, e.g., by start time
                self.events.sort(key=lambda x: x.start_time)
                self.save_events()
                logging.info(f"Event with ID {event_id} updated.")
                return event
        logging.warning(f"Event with ID {event_id} not found for editing.")
        return None

    def get_event(self, event_id):
        """Get an event by ID"""
        for event in self.events:
            if event.id == event_id:
                return event
        return None

    def get_upcoming_events(self):
        """Get all upcoming events (start or end time is in the future)"""
        # Use string comparison for simplicity, assuming YYYY-MM-DD HH:MM format
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        upcoming = []
        for event in self.events:
            # Event is upcoming if it starts now or later
            is_upcoming = event.start_time >= now_str
            # Or if it has an end time, and that end time is now or later
            # (This includes events that started in the past but are still ongoing)
            if not is_upcoming and event.end_time:
                 is_upcoming = event.end_time >= now_str

            if is_upcoming:
                upcoming.append(event)

        # Events are already sorted by start time due to add/edit logic
        # If not guaranteed, sort here: upcoming.sort(key=lambda x: x.start_time)
        return upcoming

    def get_events_by_keyword(self, keyword):
        """Get events by keyword (case-insensitive)"""
        if not keyword: # Return empty list if keyword is empty
            return []
        keyword_lower = keyword.lower()
        return [event for event in self.events if any(keyword_lower in kw.lower() for kw in event.keywords)]

# Create a singleton instance of the Calendar
calendar = Calendar()