import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import datetime

from main import CalendarManager, Event

class CalendarApp:
    def __init__(self, root_window):
        self.window = root_window
        self.style = ttkb.Style(theme="litera")
        self.window.title("Jednoduchý Kalendár")
        self.window.geometry("750x600")

        self.manager = CalendarManager()
        self.selected_event_id = None

        # --- Hlavný rámec (Frame) ---
        main_frame = ttkb.Frame(self.window, padding=15)
        main_frame.pack(fill=BOTH, expand=YES)

        # --- Horný panel (Filtrovanie) ---
        filter_frame = ttkb.Frame(main_frame)
        filter_frame.pack(fill=X, pady=(0, 10))

        ttkb.Label(filter_frame, text="Filter (kľ. slovo):").pack(side=LEFT, padx=(0, 5))
        self.filter_entry = ttkb.Entry(filter_frame, width=25)
        self.filter_entry.pack(side=LEFT, padx=5, fill=X, expand=YES)
        self.filter_entry.bind("<Return>", self.filter_events)

        filter_button = ttkb.Button(filter_frame, text="Filtrovať", command=self.filter_events, bootstyle=INFO, width=10)
        filter_button.pack(side=LEFT, padx=5)
        show_all_button = ttkb.Button(filter_frame, text="Všetky nadch.", command=self.show_upcoming_events, bootstyle=SECONDARY, width=15)
        show_all_button.pack(side=LEFT, padx=5)

        # --- Panel so zoznamom udalostí (Treeview) ---
        list_frame = ttkb.LabelFrame(main_frame, text="Udalosti", padding=10)
        list_frame.pack(fill=BOTH, expand=YES, pady=10)

        columns = ("id", "start", "description", "location")
        self.tree = ttkb.Treeview(
            master=list_frame,
            columns=columns,
            show="headings",
            height=10,
            bootstyle=PRIMARY
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("start", text="Začiatok")
        self.tree.heading("description", text="Popis")
        self.tree.heading("location", text="Miesto")

        self.tree.column("id", width=0, stretch=NO)
        self.tree.column("start", width=150, anchor=W)
        self.tree.column("description", width=250, anchor=W)
        self.tree.column("location", width=120, anchor=W)

        scrollbar = ttkb.Scrollbar(list_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.pack(side=LEFT, fill=BOTH, expand=YES)
        self.tree.bind("<<TreeviewSelect>>", self.show_event_details)

        # --- Panel s formulárom pre pridanie/úpravu ---
        form_frame = ttkb.LabelFrame(main_frame, text="Detail / Nová udalosť", padding=15)
        form_frame.pack(fill=X, pady=(0, 10))

        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

        self.start_date_var = tk.StringVar()
        self.start_time_var = tk.StringVar(value="09:00")
        self.end_date_var = tk.StringVar()
        self.end_time_var = tk.StringVar(value="17:00")
        self.all_day_var = tk.BooleanVar()
        self.location_var = tk.StringVar()
        self.keywords_var = tk.StringVar()

        # === ZMENA: Aktualizácia Label textu pre formát dátumu ===
        ttkb.Label(form_frame, text="Začiatok Dátum (DD-MM-YY):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.start_date_entry = ttkb.Entry(form_frame, textvariable=self.start_date_var, width=12)
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttkb.Label(form_frame, text="Čas (HH:MM):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.start_time_entry = ttkb.Entry(form_frame, textvariable=self.start_time_var, width=8)
        self.start_time_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        # === ZMENA: Použitie formátu DD-MM-YY pre predvolený dátum ===
        self.start_date_var.set(datetime.date.today().strftime("%d-%m-%y"))

        # === ZMENA: Aktualizácia Label textu pre formát dátumu ===
        ttkb.Label(form_frame, text="Koniec Dátum (DD-MM-YY):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.end_date_entry = ttkb.Entry(form_frame, textvariable=self.end_date_var, width=12)
        self.end_date_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttkb.Label(form_frame, text="Čas (HH:MM):").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.end_time_entry = ttkb.Entry(form_frame, textvariable=self.end_time_var, width=8)
        self.end_time_entry.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        # === ZMENA: Použitie formátu DD-MM-YY pre predvolený dátum ===
        self.end_date_var.set(datetime.date.today().strftime("%d-%m-%y"))

        self.all_day_check = ttkb.Checkbutton(form_frame, text="Celý deň", variable=self.all_day_var, bootstyle="primary", command=self.toggle_time_fields)
        self.all_day_check.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        ttkb.Label(form_frame, text="Miesto:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.location_entry = ttkb.Entry(form_frame, textvariable=self.location_var)
        self.location_entry.grid(row=2, column=3, padx=5, pady=5, sticky="ew")

        ttkb.Label(form_frame, text="Kľ. slová (čiarka):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.keywords_entry = ttkb.Entry(form_frame, textvariable=self.keywords_var)
        self.keywords_entry.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        ttkb.Label(form_frame, text="Popis:").grid(row=4, column=0, padx=5, pady=5, sticky="nw")
        from ttkbootstrap.scrolled import ScrolledText
        self.description_text = ScrolledText(form_frame, height=4, width=40, autohide=True)
        self.description_text.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        # --- Panel s tlačidlami akcií ---
        button_frame = ttkb.Frame(main_frame)
        button_frame.pack(fill=X, pady=(10, 0))

        self.delete_button = ttkb.Button(button_frame, text="Zmazať vybrané", command=self.delete_selected_event, bootstyle=DANGER, width=15, state=DISABLED)
        self.delete_button.pack(side=RIGHT, padx=5)

        self.clear_button = ttkb.Button(button_frame, text="Vyčistiť / Nová", command=self.clear_form, bootstyle=SECONDARY, width=15)
        self.clear_button.pack(side=RIGHT, padx=5)

        self.save_button = ttkb.Button(button_frame, text="Pridať udalosť", command=self.add_or_update_event, bootstyle=SUCCESS, width=15)
        self.save_button.pack(side=RIGHT, padx=5)

        # --- Inicializácia ---
        self.refresh_events_list()
        self.clear_form()

    # Metóda na naplnenie Treeview udalosťami
    def refresh_events_list(self, events_to_show=None):
        self.tree.delete(*self.tree.get_children())
        self.selected_event_id = None

        if events_to_show is None:
            events_to_display = self.manager.get_upcoming_events()
        else:
            events_to_display = events_to_show

        # === ZMENA: Formát dátumu pre Treeview ===
        date_format = "%d-%m-%y"
        time_format = "%H:%M"

        for event in events_to_display:
            start_str = ""
            if event.all_day:
                start_str = event.start_datetime.strftime(date_format) + " (Celý deň)"
            else:
                start_str = event.start_datetime.strftime(f"{date_format} {time_format}")

            values = (
                event.event_id,
                start_str,
                event.description,
                event.location
            )
            self.tree.insert("", tk.END, values=values, iid=event.event_id)

        self.update_button_states()

    # Metóda volaná pri výbere riadku v Treeview
    def show_event_details(self, event_arg=None):
        selected_items = self.tree.selection()
        if not selected_items:
            if self.selected_event_id:
                 self.clear_form()
            return

        self.selected_event_id = selected_items[0]
        event_obj = self.manager.get_event_by_id(self.selected_event_id)

        if event_obj:
            # === ZMENA: Použitie formátu DD-MM-YY pri zobrazení ===
            self.start_date_var.set(event_obj.start_datetime.strftime("%d-%m-%y"))
            self.start_time_var.set(event_obj.start_datetime.strftime("%H:%M"))

            if event_obj.all_day:
                end_display_date = event_obj.end_datetime.date() - datetime.timedelta(days=1)
                # === ZMENA: Použitie formátu DD-MM-YY pri zobrazení ===
                self.end_date_var.set(end_display_date.strftime("%d-%m-%y"))
                self.end_time_var.set("00:00")
            else:
                # === ZMENA: Použitie formátu DD-MM-YY pri zobrazení ===
                self.end_date_var.set(event_obj.end_datetime.strftime("%d-%m-%y"))
                self.end_time_var.set(event_obj.end_datetime.strftime("%H:%M"))

            self.all_day_var.set(event_obj.all_day)
            self.location_var.set(event_obj.location)
            self.keywords_var.set(", ".join(event_obj.keywords))

            self.description_text.delete("1.0", tk.END)
            self.description_text.insert("1.0", event_obj.description)

            self.update_button_states()
            self.toggle_time_fields()
        else:
            messagebox.showerror("Chyba", "Vybraná udalosť už neexistuje.", parent=self.window)
            self.clear_form()
            self.refresh_events_list()

    # Metóda na vyčistenie formulára a resetovanie stavu
    def clear_form(self):
        self.selected_event_id = None
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])

        # === ZMENA: Použitie formátu DD-MM-YY pre predvolený dátum ===
        self.start_date_var.set(datetime.date.today().strftime("%d-%m-%y"))
        self.start_time_var.set("09:00")
        # === ZMENA: Použitie formátu DD-MM-YY pre predvolený dátum ===
        self.end_date_var.set(datetime.date.today().strftime("%d-%m-%y"))
        self.end_time_var.set("17:00")
        self.all_day_var.set(False)
        self.location_var.set("")
        self.keywords_var.set("")
        self.description_text.delete("1.0", tk.END)

        self.update_button_states()
        self.toggle_time_fields()

    # Metóda na zapnutie/vypnutie polí pre čas podľa stavu 'Celý deň'
    def toggle_time_fields(self):
        state = tk.DISABLED if self.all_day_var.get() else tk.NORMAL
        self.start_time_entry.config(state=state)
        self.end_time_entry.config(state=state)
        if self.all_day_var.get():
            self.start_time_var.set("00:00")
            self.end_time_var.set("00:00")

    # Metóda na aktualizáciu textu a stavu tlačidiel (Save, Delete)
    def update_button_states(self):
        if self.selected_event_id:
            self.save_button.config(text="Uložiť zmeny")
            self.delete_button.config(state=NORMAL)
        else:
            self.save_button.config(text="Pridať udalosť")
            self.delete_button.config(state=DISABLED)

    # Metóda na pridanie alebo úpravu udalosti (volaná tlačidlom Save)
    def add_or_update_event(self):
        try:
            start_date_str = self.start_date_var.get()
            end_date_str = self.end_date_var.get()
            start_time_str = self.start_time_var.get() if not self.all_day_var.get() else "00:00"
            end_time_str = self.end_time_var.get() if not self.all_day_var.get() else "00:00"

            # === ZMENA: Parsovanie formátu DD-MM-YY ===
            start_date = datetime.datetime.strptime(start_date_str, "%d-%m-%y").date()
            end_date = datetime.datetime.strptime(end_date_str, "%d-%m-%y").date()
            start_hour, start_min = map(int, start_time_str.split(':'))
            end_hour, end_min = map(int, end_time_str.split(':'))

            start_dt = datetime.datetime.combine(start_date, datetime.time(start_hour, start_min))

            if self.all_day_var.get():
                start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
                end_dt = datetime.datetime.combine(end_date + datetime.timedelta(days=1), datetime.time(0, 0))
            else:
                end_dt = datetime.datetime.combine(end_date, datetime.time(end_hour, end_min))

            if end_dt <= start_dt:
                messagebox.showerror("Chyba dátumu", "Koniec udalosti musí byť po jej začiatku.", parent=self.window)
                return

            location = self.location_var.get().strip()
            description = self.description_text.get("1.0", tk.END).strip()
            keywords_raw = self.keywords_var.get().split(',')
            keywords = [kw.strip().lower() for kw in keywords_raw if kw.strip()]

            if not description:
                messagebox.showwarning("Chýbajúci popis", "Zadajte popis udalosti.", parent=self.window)
                return

            event_data = {
                'start_datetime': start_dt,
                'end_datetime': end_dt,
                'all_day': self.all_day_var.get(),
                'location': location,
                'description': description,
                'keywords': keywords
            }

            if self.selected_event_id:
                success = self.manager.edit_event(self.selected_event_id, event_data)
                if success:
                    messagebox.showinfo("Úspech", "Udalosť bola úspešne upravená.", parent=self.window)
                else:
                    messagebox.showerror("Chyba", "Nepodarilo sa upraviť udalosť.", parent=self.window)
            else:
                new_event = Event(**event_data)
                self.manager.add_event(new_event)
                messagebox.showinfo("Úspech", "Udalosť bola úspešne pridaná.", parent=self.window)

            self.refresh_events_list()
            self.clear_form()

        except ValueError as e:
            # === ZMENA: Aktualizácia chybovej hlášky pre formát ===
            messagebox.showerror("Chyba vstupu", f"Neplatný formát dátumu (DD-MM-YY) alebo času (HH:MM).\n{e}", parent=self.window)
        except Exception as e:
            messagebox.showerror("Chyba", f"Vyskytla sa neočakávaná chyba: {e}", parent=self.window)

    # Metóda na zmazanie vybranej udalosti
    def delete_selected_event(self):
        if not self.selected_event_id:
            messagebox.showwarning("Žiadny výber", "Najprv vyberte udalosť na zmazanie.", parent=self.window)
            return

        event_obj = self.manager.get_event_by_id(self.selected_event_id)
        desc = event_obj.description if event_obj else "vybranú udalosť"

        confirm = messagebox.askyesno(f"Naozaj chcete zmazať udalosť '{desc}'?", "Potvrdenie", parent=self.window)

        if confirm:
            success = self.manager.delete_event(self.selected_event_id)
            if success:
                messagebox.showinfo("Úspech", "Udalosť bola zmazaná.", parent=self.window)
                self.refresh_events_list()
                self.clear_form()
            else:
                messagebox.showerror("Chyba", "Nepodarilo sa zmazať udalosť (možno už neexistuje).", parent=self.window)

    # Metóda na filtrovanie udalostí podľa kľúčového slova z Entry poľa
    def filter_events(self, event=None):
        keyword = self.filter_entry.get().strip()
        filtered = self.manager.get_events_by_keyword(keyword)
        self.refresh_events_list(filtered)
        self.clear_form()

    # Metóda na zobrazenie všetkých nadchádzajúcich udalostí (reset filtra)
    def show_upcoming_events(self):
        self.filter_entry.delete(0, tk.END)
        self.refresh_events_list()
        self.clear_form()

# --- Hlavná časť programu ---
if __name__ == "__main__":
    try:
        import ttkbootstrap
    except ImportError:
         print("Chyba: Knižnica 'ttkbootstrap' nie je nainštalovaná.")
         print("Nainštalujte ju pomocou príkazu: pip install ttkbootstrap")
         exit()

    app_root = ttkb.Window(themename="litera")
    app = CalendarApp(app_root)
    app_root.mainloop()