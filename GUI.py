import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox
from ttkbootstrap.scrolled import ScrolledFrame
from datetime import datetime, timedelta
import Main

class CalendarApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="cosmo")
        self.title("Event Calendar")
        self.geometry("900x600")
        self.calendar = Main.calendar
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the main UI components"""
        # Create a notebook for different views
        self.notebook = ttk.Notebook(self)
        
        # Create frames for each tab
        self.events_frame = ttk.Frame(self.notebook)
        self.add_event_frame = ttk.Frame(self.notebook)
        self.search_frame = ttk.Frame(self.notebook)
        
        # Add frames to notebook
        self.notebook.add(self.events_frame, text="All Events")
        self.notebook.add(self.add_event_frame, text="Add Event")
        self.notebook.add(self.search_frame, text="Search Events")
        
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Set up each tab
        self.setup_events_tab()
        self.setup_add_event_tab()
        self.setup_search_tab()
    
    def setup_events_tab(self):
        """Set up the events listing tab"""
        # Filter options
        filter_frame = ttk.Frame(self.events_frame)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(filter_frame, text="View:").pack(side="left", padx=5)
        
        self.view_var = ttk.StringVar(value="upcoming")
        ttk.Radiobutton(filter_frame, text="Upcoming Events", variable=self.view_var, 
                       value="upcoming", command=self.refresh_events).pack(side="left", padx=5)
        ttk.Radiobutton(filter_frame, text="All Events", variable=self.view_var, 
                       value="all", command=self.refresh_events).pack(side="left", padx=5)
        
        # Events list
        self.events_container = ScrolledFrame(self.events_frame, autohide=True)
        self.events_container.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Initial load of events
        self.refresh_events()
    
    def setup_add_event_tab(self):
        """Set up the add event form tab"""
        form_frame = ttk.Frame(self.add_event_frame)
        form_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Title
        ttk.Label(form_frame, text="Event Title:").grid(row=0, column=0, sticky="w", pady=5)
        self.title_var = ttk.StringVar()
        ttk.Entry(form_frame, textvariable=self.title_var, width=40).grid(row=0, column=1, sticky="ew", pady=5)
        
        # Start time
        ttk.Label(form_frame, text="Start (YYYY-MM-DD HH:MM):").grid(row=1, column=0, sticky="w", pady=5)
        self.start_var = ttk.StringVar()
        ttk.Entry(form_frame, textvariable=self.start_var, width=40).grid(row=1, column=1, sticky="ew", pady=5)
        
        # End time
        ttk.Label(form_frame, text="End (YYYY-MM-DD HH:MM):").grid(row=2, column=0, sticky="w", pady=5)
        self.end_var = ttk.StringVar()
        ttk.Entry(form_frame, textvariable=self.end_var, width=40).grid(row=2, column=1, sticky="ew", pady=5)
        
        # All day event option
        self.all_day_var = ttk.BooleanVar()
        ttk.Checkbutton(form_frame, text="All day event", variable=self.all_day_var, 
                       command=self.toggle_all_day).grid(row=3, column=0, columnspan=2, sticky="w", pady=5)
        
        # Location
        ttk.Label(form_frame, text="Location:").grid(row=4, column=0, sticky="w", pady=5)
        self.location_var = ttk.StringVar()
        ttk.Entry(form_frame, textvariable=self.location_var, width=40).grid(row=4, column=1, sticky="ew", pady=5)
        
        # Description
        ttk.Label(form_frame, text="Description:").grid(row=5, column=0, sticky="w", pady=5)
        self.description_var = ttk.StringVar()
        ttk.Entry(form_frame, textvariable=self.description_var, width=40).grid(row=5, column=1, sticky="ew", pady=5)
        
        # Keywords
        ttk.Label(form_frame, text="Keywords (comma separated):").grid(row=6, column=0, sticky="w", pady=5)
        self.keywords_var = ttk.StringVar()
        ttk.Entry(form_frame, textvariable=self.keywords_var, width=40).grid(row=6, column=1, sticky="ew", pady=5)
        
        # Add button
        ttk.Button(form_frame, text="Add Event", command=self.add_event, 
                  bootstyle="success").grid(row=7, column=0, columnspan=2, pady=15)
        
        # Hidden event ID for editing
        self.editing_event_id = None
        
        # Form configuration
        form_frame.columnconfigure(1, weight=1)
    
    def setup_search_tab(self):
        """Set up the search tab"""
        search_controls = ttk.Frame(self.search_frame)
        search_controls.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(search_controls, text="Search by Keyword:").pack(side="left", padx=5)
        
        self.search_var = ttk.StringVar()
        ttk.Entry(search_controls, textvariable=self.search_var, width=30).pack(side="left", padx=5)
        
        ttk.Button(search_controls, text="Search", command=self.search_events, 
                  bootstyle="primary").pack(side="left", padx=5)
        
        self.search_results = ScrolledFrame(self.search_frame, autohide=True)
        self.search_results.pack(expand=True, fill="both", padx=10, pady=10)
    
    def refresh_events(self):
        """Refresh the events list"""
        # Clear current events
        for widget in self.events_container.winfo_children():
            widget.destroy()
        
        # Get events based on selected view
        if self.view_var.get() == "upcoming":
            events = self.calendar.get_upcoming_events()
        else:
            events = self.calendar.events
        
        if not events:
            ttk.Label(self.events_container, text="No events found").pack(pady=20)
            return
        
        # Add each event to the container
        for event in events:
            self.create_event_card(self.events_container, event)
    
    def search_events(self):
        """Search events by keyword"""
        keyword = self.search_var.get().strip()
        if not keyword:
            messagebox.showinfo("Search", "Please enter a keyword to search")
            return
        
        # Clear current results
        for widget in self.search_results.winfo_children():
            widget.destroy()
        
        # Get events by keyword
        events = self.calendar.get_events_by_keyword(keyword)
        
        if not events:
            ttk.Label(self.search_results, text=f"No events found for keyword '{keyword}'").pack(pady=20)
            return
        
        # Display found events
        for event in events:
            self.create_event_card(self.search_results, event)
    
    def create_event_card(self, parent, event):
        """Create a card for an event in the specified parent container"""
        card = ttk.Frame(parent, bootstyle="light")
        card.pack(fill="x", padx=10, pady=5, ipadx=10, ipady=5)
        
        # Event title and time
        title_frame = ttk.Frame(card)
        title_frame.pack(fill="x", pady=5)
        
        title_label = ttk.Label(title_frame, text=event.title, font=("TkDefaultFont", 12, "bold"))
        title_label.pack(side="left")
        
        # Format time display
        time_text = f"Start: {event.start_time}"
        if event.end_time:
            time_text += f" - End: {event.end_time}"
        if event.is_all_day():
            time_text += " (All day)"
        elif event.is_multi_day():
            time_text += " (Multi-day)"
        
        time_label = ttk.Label(card, text=time_text)
        time_label.pack(fill="x", anchor="w")
        
        # Location and description
        if event.location:
            location_label = ttk.Label(card, text=f"Location: {event.location}")
            location_label.pack(fill="x", anchor="w")
        
        if event.description:
            desc_label = ttk.Label(card, text=f"Description: {event.description}")
            desc_label.pack(fill="x", anchor="w")
        
        # Keywords
        if event.keywords:
            keywords_text = "Keywords: " + ", ".join(event.keywords)
            keywords_label = ttk.Label(card, text=keywords_text)
            keywords_label.pack(fill="x", anchor="w")
        
        # Buttons for edit and delete
        btn_frame = ttk.Frame(card)
        btn_frame.pack(fill="x", pady=5)
        
        edit_btn = ttk.Button(btn_frame, text="Edit", 
                             command=lambda e=event: self.edit_event(e),
                             bootstyle="info-outline", width=10)
        edit_btn.pack(side="left", padx=5)
        
        delete_btn = ttk.Button(btn_frame, text="Delete", 
                               command=lambda e=event: self.delete_event(e),
                               bootstyle="danger-outline", width=10)
        delete_btn.pack(side="left", padx=5)
    
    def toggle_all_day(self):
        """Handle the all-day checkbox toggle"""
        if self.all_day_var.get():
            # Set to all day format (00:00 to 23:59)
            if self.start_var.get():
                try:
                    start_dt = datetime.strptime(self.start_var.get(), "%Y-%m-%d %H:%M")
                    self.start_var.set(f"{start_dt.date()} 00:00")
                    self.end_var.set(f"{start_dt.date()} 23:59")
                except ValueError:
                    pass
        
    def add_event(self):
        """Add a new event or update existing one"""
        # Validate required fields
        if not self.title_var.get() or not self.start_var.get():
            messagebox.showerror("Error", "Title and start time are required")
            return
        
        try:
            # Prepare the keywords as a list
            keywords = [k.strip() for k in self.keywords_var.get().split(",") if k.strip()]
            
            if self.editing_event_id:
                # Update existing event
                self.calendar.edit_event(
                    self.editing_event_id,
                    self.title_var.get(),
                    self.start_var.get(),
                    self.end_var.get() if self.end_var.get() else None,
                    self.location_var.get(),
                    self.description_var.get(),
                    keywords
                )
                messagebox.showinfo("Success", "Event updated successfully")
                self.editing_event_id = None
            else:
                # Add new event
                self.calendar.add_event(
                    self.title_var.get(),
                    self.start_var.get(),
                    self.end_var.get() if self.end_var.get() else None,
                    self.location_var.get(),
                    self.description_var.get(),
                    keywords
                )
                messagebox.showinfo("Success", "Event added successfully")
            
            # Clear the form
            self.clear_form()
            
            # Refresh events list
            self.refresh_events()
            # Switch to events tab
            self.notebook.select(0)
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def edit_event(self, event):
        """Load event data into the form for editing"""
        self.editing_event_id = event.id
        
        # Populate the form
        self.title_var.set(event.title)
        self.start_var.set(event.start_time)
        self.end_var.set(event.end_time if event.end_time else "")
        self.location_var.set(event.location)
        self.description_var.set(event.description)
        self.keywords_var.set(", ".join(event.keywords))
        
        # Check if it's an all-day event
        self.all_day_var.set(event.is_all_day())
        
        # Switch to add/edit tab and rename it
        self.notebook.tab(1, text="Edit Event")
        self.notebook.select(1)
    
    def delete_event(self, event):
        """Delete an event after confirmation"""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{event.title}'?"):
            self.calendar.delete_event(event.id)
            self.refresh_events()
            messagebox.showinfo("Success", "Event deleted")
    
    def clear_form(self):
        """Clear the event form"""
        self.title_var.set("")
        self.start_var.set("")
        self.end_var.set("")
        self.location_var.set("")
        self.description_var.set("")
        self.keywords_var.set("")
        self.all_day_var.set(False)
        self.editing_event_id = None
        self.notebook.tab(1, text="Add Event")

if __name__ == "__main__":
    app = CalendarApp()
    app.mainloop()