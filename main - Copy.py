import datetime
import uuid

class Event:
    def __init__(self, start_datetime, end_datetime, location, description, keywords, all_day=False, event_id=None):
        self.event_id = event_id if event_id else str(uuid.uuid4())
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.all_day = all_day
        self.location = location
        self.description = description
        self.keywords = keywords

class CalendarManager:
    def __init__(self):
        self.events = []
       
    def add_event(self, event):
        print(f"Pridávam udalosť do pamäte: {event.description}")
        self.events.append(event)

    def edit_event(self, event_id, updated_data):
        print(f"Upravujem udalosť v pamäti s ID: {event_id}")
        event_to_edit = self.get_event_by_id(event_id)

        if event_to_edit:
            event_to_edit.start_datetime = updated_data.get('start_datetime', event_to_edit.start_datetime)
            event_to_edit.end_datetime = updated_data.get('end_datetime', event_to_edit.end_datetime)
            event_to_edit.all_day = updated_data.get('all_day', event_to_edit.all_day)
            event_to_edit.location = updated_data.get('location', event_to_edit.location)
            event_to_edit.description = updated_data.get('description', event_to_edit.description)
            event_to_edit.keywords = updated_data.get('keywords', event_to_edit.keywords)
            print(f"Udalosť {event_id} upravená.")
            return True
        else:
            print(f"Udalosť s ID {event_id} nebola nájdená pre úpravu.")
            return False

    def delete_event(self, event_id):
        print(f"Mažem udalosť z pamäte s ID: {event_id}")
        original_count = len(self.events)
        self.events = [event for event in self.events if event.event_id != event_id]
        if len(self.events) < original_count:
            print(f"Udalosť {event_id} zmazaná.")
            return True
        else:
            print(f"Udalosť s ID {event_id} nebola nájdená pre zmazanie.")
            return False

    def get_event_by_id(self, event_id):
        for event in self.events:
            if event.event_id == event_id:
                return event
        return None

    def get_upcoming_events(self):
        now = datetime.datetime.now()
        upcoming = []
        for event in self.events:
            if event.end_datetime >= now:
                upcoming.append(event)
        upcoming.sort(key=lambda x: x.start_datetime)
        return upcoming

   
    def get_events_by_keyword(self, keyword):
        if not keyword:
            return self.get_upcoming_events()

        keyword_lower = keyword.lower()
        upcoming_events = self.get_upcoming_events()
        filtered_events = []
        for event in upcoming_events:
            found = False
            for kw in event.keywords:
                if kw.lower() == keyword_lower:
                    found = True
                    break 
            if found:
                filtered_events.append(event)

        return filtered_events