import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox
from ttkbootstrap.scrolled import ScrolledFrame
from datetime import datetime, timedelta
import Main  # Assuming Main.py is in the same directory and provides 'calendar' instance

class CalendarApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="cosmo")
        self.title("Event Calendar")
        self.geometry("900x600")
        # Use the singleton calendar instance from Main
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
        self.notebook.add(self.events_frame, text="Events") # Changed tab name slightly
        self.notebook.add(self.add_event_frame, text="Add Event")
        self.notebook.add(self.search_frame, text="Search Events")

        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Set up each tab
        self.setup_events_tab()
        self.setup_add_event_tab()
        self.setup_search_tab()

        # Add status bar (optional but good practice)
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.set_status("Ready")

    def set_status(self, message):
        """Update the status bar message"""
        self.status_var.set(message)

    def setup_events_tab(self):
        """Set up the events listing tab"""
        # Filter options
        filter_frame = ttk.Frame(self.events_frame)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="View:").pack(side="left", padx=5)

        self.view_var = ttk.StringVar(value="upcoming")
        # Use ttk.Radiobutton for consistency with ttkbootstrap
        rb_upcoming = ttk.Radiobutton(filter_frame, text="Upcoming/Ongoing", variable=self.view_var,
                           value="upcoming", command=self.refresh_events, bootstyle="toolbutton")
        rb_upcoming.pack(side="left", padx=5)
        rb_all = ttk.Radiobutton(filter_frame, text="All Events", variable=self.view_var,
                       value="all", command=self.refresh_events, bootstyle="toolbutton")
        rb_all.pack(side="left", padx=5)

        # Events list using ScrolledFrame
        self.events_container = ScrolledFrame(self.events_frame, autohide=True)
        self.events_container.pack(expand=True, fill="both", padx=10, pady=10)

        # Initial load of events
        self.refresh_events()

    def setup_add_event_tab(self):
        """Set up the add/edit event form tab"""
        # Use a ScrolledFrame in case the window is small
        sf = ScrolledFrame(self.add_event_frame, autohide=True)
        sf.pack(expand=True, fill="both")
        form_frame = ttk.Frame(sf) # Put the form inside the scrolled area
        form_frame.pack(expand=True, fill="x", padx=20, pady=20) # Allow horizontal fill

        # Title
        ttk.Label(form_frame, text="Event Title:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.title_var = ttk.StringVar()
        self.title_entry = ttk.Entry(form_frame, textvariable=self.title_var, width=40)
        self.title_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        # Start time
        ttk.Label(form_frame, text="Start (YYYY-MM-DD HH:MM):").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.start_var = ttk.StringVar()
        self.start_entry = ttk.Entry(form_frame, textvariable=self.start_var, width=40)
        self.start_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        # End time
        ttk.Label(form_frame, text="End (YYYY-MM-DD HH:MM):").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.end_var = ttk.StringVar()
        self.end_entry = ttk.Entry(form_frame, textvariable=self.end_var, width=40)
        self.end_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=5)
        self.end_entry.config(state='normal') # Ensure it's enabled by default

        # All day event option
        self.all_day_var = ttk.BooleanVar()
        self.all_day_check = ttk.Checkbutton(form_frame, text="All day event", variable=self.all_day_var,
                       command=self.toggle_all_day)
        self.all_day_check.grid(row=3, column=0, columnspan=2, sticky="w", pady=5, padx=5)

        # Location
        ttk.Label(form_frame, text="Location:").grid(row=4, column=0, sticky="w", pady=5, padx=5)
        self.location_var = ttk.StringVar()
        self.location_entry = ttk.Entry(form_frame, textvariable=self.location_var, width=40)
        self.location_entry.grid(row=4, column=1, sticky="ew", pady=5, padx=5)

        # Description
        ttk.Label(form_frame, text="Description:").grid(row=5, column=0, sticky="nw", pady=5, padx=5) # Use nw for alignment
        self.description_var = tk.StringVar() # Use tk.StringVar for Text widget
        # Use Text widget for multiline description
        self.description_text = tk.Text(form_frame, height=4, width=40, wrap=tk.WORD)
        self.description_text.grid(row=5, column=1, sticky="ew", pady=5, padx=5)
        # Add scrollbar for description text
        desc_scroll = ttk.Scrollbar(form_frame, orient=tk.VERTICAL, command=self.description_text.yview)
        desc_scroll.grid(row=5, column=2, sticky="nsw", pady=5)
        self.description_text['yscrollcommand'] = desc_scroll.set


        # Keywords
        ttk.Label(form_frame, text="Keywords (comma separated):").grid(row=6, column=0, sticky="w", pady=5, padx=5)
        self.keywords_var = ttk.StringVar()
        self.keywords_entry = ttk.Entry(form_frame, textvariable=self.keywords_var, width=40)
        self.keywords_entry.grid(row=6, column=1, sticky="ew", pady=5, padx=5)

        # Buttons Frame
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=15) # Span all columns

        # Add/Update button
        self.submit_button = ttk.Button(button_frame, text="Add Event", command=self.add_or_update_event,
                  bootstyle="success")
        self.submit_button.pack(side=tk.LEFT, padx=10)

        # Clear button
        self.clear_button = ttk.Button(button_frame, text="Clear Form", command=self.clear_form,
                  bootstyle="secondary")
        self.clear_button.pack(side=tk.LEFT, padx=10)


        # Hidden event ID for editing
        self.editing_event_id = None

        # Form configuration
        form_frame.columnconfigure(1, weight=1) # Allow entry column to expand

    def setup_search_tab(self):
        """Set up the search tab"""
        search_controls = ttk.Frame(self.search_frame)
        search_controls.pack(fill="x", padx=10, pady=10)

        ttk.Label(search_controls, text="Search by Keyword:").pack(side="left", padx=5)

        self.search_var = ttk.StringVar()
        search_entry = ttk.Entry(search_controls, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=5)
        # Bind Enter key to search action
        search_entry.bind("<Return>", lambda event: self.search_events())


        search_button = ttk.Button(search_controls, text="Search", command=self.search_events,
                  bootstyle="primary")
        search_button.pack(side="left", padx=5)

        clear_button = ttk.Button(search_controls, text="Clear", command=self.clear_search,
                                  bootstyle="secondary-outline")
        clear_button.pack(side="left", padx=5)

        self.search_results = ScrolledFrame(self.search_frame, autohide=True)
        self.search_results.pack(expand=True, fill="both", padx=10, pady=10)

    def clear_search(self):
        """Clear search input and results"""
        self.search_var.set("")
        # Clear current results
        for widget in self.search_results.winfo_children():
            widget.destroy()
        ttk.Label(self.search_results, text="Enter a keyword to search.").pack(pady=20)
        self.set_status("Search cleared")


    def refresh_events(self):
        """Refresh the events list based on the selected view"""
        self.set_status("Refreshing events...")
        # Clear current events
        # Use self.events_container.interior for ScrolledFrame content
        for widget in self.events_container.winfo_children():
            widget.destroy()

        # Get events based on selected view
        view = self.view_var.get()
        if view == "upcoming":
            events = self.calendar.get_upcoming_events()
            if not events:
                 ttk.Label(self.events_container, text="No upcoming or ongoing events.").pack(pady=20)
            else:
                 ttk.Label(self.events_container, text="Upcoming & Ongoing Events:", font="-weight bold").pack(pady=(5,10), anchor='w')
        else:
            events = self.calendar.events # Assumes events are sorted by date in Calendar
            if not events:
                 ttk.Label(self.events_container, text="No events found.").pack(pady=20)
            else:
                 ttk.Label(self.events_container, text="All Events:", font="-weight bold").pack(pady=(5,10), anchor='w')


        if not events:
            self.set_status("No events to display.")
            return

        # Add each event to the container
        count = 0
        for event in events:
            self.create_event_card(self.events_container, event)
            count += 1

        self.set_status(f"Displayed {count} event(s).")

    def search_events(self, event=None): # Added event=None for binding
        """Search events by keyword"""
        keyword = self.search_var.get().strip()
        if not keyword:
            messagebox.showwarning("Search", "Please enter a keyword to search.")
            return

        self.set_status(f"Searching for '{keyword}'...")
        # Clear current results
        for widget in self.search_results.winfo_children():
            widget.destroy()

        # Get events by keyword
        events = self.calendar.get_events_by_keyword(keyword)

        if not events:
            ttk.Label(self.search_results, text=f"No events found for keyword '{keyword}'").pack(pady=20)
            self.set_status(f"No results found for '{keyword}'.")
            return

        # Display found events
        count = 0
        for event in events:
            # Pass search_results as parent
            self.create_event_card(self.search_results, event)
            count += 1
        self.set_status(f"Found {count} event(s) for '{keyword}'.")


    def create_event_card(self, parent, event):
        """Create a card for an event in the specified parent container's interior"""
        # Important: Add card to parent directly (ScrolledFrame handles interior placement)
        card = ttk.Frame(parent, borderwidth=1, relief="solid", padding=10) # Added border and padding
        card.pack(fill="x", padx=5, pady=5) # Use pack inside ScrolledFrame

        # Event title and time frame
        header_frame = ttk.Frame(card)
        header_frame.pack(fill="x", pady=(0, 5))

        title_label = ttk.Label(header_frame, text=event.title, font=("TkDefaultFont", 12, "bold"))
        title_label.pack(side="left", anchor="w")

        # Format time display more clearly
        start_dt_str = event.start_time
        end_dt_str = event.end_time if event.end_time else ""
        time_text = f"Start: {start_dt_str}"
        if end_dt_str:
            time_text += f"  End: {end_dt_str}"

        tags = []
        if event.is_all_day():
            tags.append("All day")
        if event.is_multi_day():
             tags.append("Multi-day")

        if tags:
            time_text += f" ({', '.join(tags)})"


        time_label = ttk.Label(card, text=time_text)
        time_label.pack(fill="x", anchor="w")

        # Location and description if they exist
        if event.location:
            location_label = ttk.Label(card, text=f"Location: {event.location}")
            location_label.pack(fill="x", anchor="w")

        if event.description:
            # Limit description length on card for brevity
            desc_short = (event.description[:75] + '...') if len(event.description) > 75 else event.description
            desc_label = ttk.Label(card, text=f"Description: {desc_short.replace(chr(10), ' ')}") # Replace newlines
            desc_label.pack(fill="x", anchor="w")

        # Keywords if they exist
        if event.keywords:
            keywords_text = "Keywords: " + ", ".join(event.keywords)
            keywords_label = ttk.Label(card, text=keywords_text, foreground="grey") # Style keywords
            keywords_label.pack(fill="x", anchor="w")

        # Buttons for edit and delete
        btn_frame = ttk.Frame(card)
        btn_frame.pack(fill="x", pady=(10, 0)) # Add padding top

        edit_btn = ttk.Button(btn_frame, text="Edit",
                             command=lambda e=event: self.edit_event(e),
                             bootstyle="info-outline", width=8) # Smaller width
        edit_btn.pack(side="right", padx=(5,0)) # Align right

        delete_btn = ttk.Button(btn_frame, text="Delete",
                               command=lambda e=event: self.delete_event(e),
                               bootstyle="danger-outline", width=8) # Smaller width
        delete_btn.pack(side="right", padx=(0,5)) # Align right

    def toggle_all_day(self):
        """Handle the all-day checkbox toggle, enabling/disabling end time"""
        if self.all_day_var.get():
            # Disable end time entry
            self.end_entry.config(state='disabled')
            self.end_var.set("") # Clear end time when disabled

            # Set start time to 00:00 of the date in start_var or today
            try:
                # Try parsing existing start time to keep the date
                start_dt = datetime.strptime(self.start_var.get(), "%Y-%m-%d %H:%M")
                start_date_str = start_dt.strftime("%Y-%m-%d")
            except ValueError:
                # If start_var is empty or invalid, use today's date
                start_date_str = datetime.now().strftime("%Y-%m-%d")

            # Set start to 00:00 and end to 23:59 for internal logic (Main.py)
            # We will rely on the add/update logic to handle the empty end_var
            # But we set the start_var for clarity in the UI
            self.start_var.set(f"{start_date_str} 00:00")
            # The actual end time (23:59) is implicitly handled by Main.py when end_time is None/empty
            # and start is 00:00 based on is_all_day logic, but let's set it explicitly
            # for the add/update function to receive it correctly.
            # Correction: The add/update function needs the end time if it's meant to be 23:59
            self.end_var.set(f"{start_date_str} 23:59")


        else:
            # Enable end time entry
            self.end_entry.config(state='normal')
            # Optionally clear or restore previous end time? For now, just enable.


    def add_or_update_event(self):
        """Add a new event or update existing one based on editing_event_id"""
        # Validate required fields
        title = self.title_var.get().strip()
        start_time = self.start_var.get().strip()
        end_time = self.end_var.get().strip() if not self.all_day_var.get() else self.end_var.get().strip() # Get end time only if not all-day

        if not title or not start_time:
            messagebox.showerror("Error", "Title and Start time are required.")
            return

        # Get description from Text widget
        description = self.description_text.get("1.0", tk.END).strip()

        try:
            # Prepare the keywords as a list of non-empty strings
            keywords = [k.strip() for k in self.keywords_var.get().split(",") if k.strip()]

            # Use the correct end_time based on all_day checkbox
            # If all_day is checked, toggle_all_day should have set end_var to "YYYY-MM-DD 23:59"
            final_end_time = end_time if end_time else None


            if self.editing_event_id is not None:
                # Update existing event
                updated_event = self.calendar.edit_event(
                    self.editing_event_id,
                    title,
                    start_time,
                    final_end_time, # Pass potentially None end_time
                    self.location_var.get().strip(),
                    description,
                    keywords
                )
                if updated_event:
                     messagebox.showinfo("Success", "Event updated successfully.")
                     self.set_status("Event updated.")
                else:
                     # This case should ideally not happen if ID is set, but handle defensively
                     messagebox.showerror("Error", "Failed to find event to update.")
                     self.set_status("Error updating event.")
                     return # Stop further processing

            else:
                # Add new event
                new_event = self.calendar.add_event(
                    title,
                    start_time,
                    final_end_time, # Pass potentially None end_time
                    self.location_var.get().strip(),
                    description,
                    keywords
                )
                messagebox.showinfo("Success", "Event added successfully.")
                self.set_status("Event added.")

            # Clear the form and reset state
            self.clear_form()

            # Refresh events list in the "Events" tab
            self.refresh_events()
            # Switch back to events tab
            self.notebook.select(0)

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            self.set_status(f"Error: {e}")
        except Exception as e:
             # Catch unexpected errors during add/edit
             messagebox.showerror("Error", f"An unexpected error occurred: {e}")
             self.set_status(f"Unexpected error: {e}")
             logging.exception("Unexpected error during add/update event")


    def edit_event(self, event):
        """Load event data into the form for editing"""
        self.clear_form() # Clear form before loading new data
        self.editing_event_id = event.id
        self.set_status(f"Editing event: {event.title}")

        # Populate the form fields
        self.title_var.set(event.title)
        self.start_var.set(event.start_time)
        self.end_var.set(event.end_time if event.end_time else "")
        self.location_var.set(event.location if event.location else "")

        # Populate Text widget for description
        self.description_text.delete("1.0", tk.END) # Clear existing text
        if event.description:
            self.description_text.insert("1.0", event.description)

        self.keywords_var.set(", ".join(event.keywords) if event.keywords else "")

        # Check if it's an all-day event and set checkbox/end time state
        is_all_day = event.is_all_day()
        self.all_day_var.set(is_all_day)
        if is_all_day:
            self.end_entry.config(state='disabled')
            # Ensure end_var reflects the 23:59 used by is_all_day if it was set
            if event.end_time and event.end_time.endswith("23:59"):
                 self.end_var.set(event.end_time)
            else:
                 # If loaded data has start 00:00 but no end time, reconstruct end time for consistency
                 try:
                     start_dt = datetime.strptime(event.start_time, "%Y-%m-%d %H:%M")
                     self.end_var.set(f"{start_dt.strftime('%Y-%m-%d')} 23:59")
                 except ValueError:
                     self.end_var.set("") # Fallback if start time is invalid
        else:
            self.end_entry.config(state='normal')


        # Switch to add/edit tab and update button/tab text
        self.notebook.tab(1, text="Edit Event")
        self.submit_button.config(text="Update Event", bootstyle="info") # Change button
        self.notebook.select(1)
        self.title_entry.focus() # Set focus to title field

    def delete_event(self, event):
        """Delete an event after confirmation"""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the event '{event.title}'?", icon='warning'):
            if self.calendar.delete_event(event.id):
                 self.set_status(f"Event '{event.title}' deleted.")
                 messagebox.showinfo("Success", "Event deleted successfully.")
                 # Refresh events list in the current view (Events tab or Search tab)
                 current_tab_index = self.notebook.index(self.notebook.select())
                 if current_tab_index == 0: # Events tab
                     self.refresh_events()
                 elif current_tab_index == 2: # Search tab
                     # Re-run search to update results, or simply refresh the main list?
                     # Re-running search seems more appropriate
                     self.search_events()
                 # If the deleted event was being edited, clear the form
                 if self.editing_event_id == event.id:
                     self.clear_form()
            else:
                 messagebox.showerror("Error", f"Could not delete event '{event.title}'. It might have already been removed.")
                 self.set_status("Error deleting event.")


    def clear_form(self):
        """Clear the event form and reset to 'Add Event' state"""
        self.title_var.set("")
        self.start_var.set("")
        self.end_var.set("")
        self.location_var.set("")
        # Clear Text widget
        self.description_text.delete("1.0", tk.END)
        self.keywords_var.set("")
        self.all_day_var.set(False)
        self.end_entry.config(state='normal') # Ensure end time is enabled

        # Reset editing state
        self.editing_event_id = None
        self.notebook.tab(1, text="Add Event")
        self.submit_button.config(text="Add Event", bootstyle="success") # Reset button
        self.set_status("Form cleared. Ready to add new event.")

if __name__ == "__main__":
    # Ensure Main.py has run and initialized 'calendar'
    if hasattr(Main, 'calendar'):
        app = CalendarApp()
        app.mainloop()
    else:
        print("Error: Could not find 'calendar' instance in Main.py")
        # Optionally show an error dialog
        root = tk.Tk()
        root.withdraw() # Hide the main Tk window
        messagebox.showerror("Startup Error", "Failed to initialize calendar data from Main.py.")
