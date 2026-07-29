import customtkinter as ctk

from services.google_maps_scraper import GoogleMapsScraper


class LeadFinder(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)

        self.build_ui()

    def build_ui(self):

        # =====================================
        # TITLE
        # =====================================

        title = ctk.CTkLabel(
            self,
            text="Find New Leads",
            font=("Segoe UI", 28, "bold")
        )

        title.pack(
            anchor="w",
            padx=30,
            pady=(20, 20)
        )

        # =====================================
        # SEARCH FORM
        # =====================================

        form = ctk.CTkFrame(self)
        form.pack(
            fill="x",
            padx=30,
            pady=10
        )

        # Business Category

        ctk.CTkLabel(
            form,
            text="Business Category"
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=15,
            sticky="w"
        )

        self.category = ctk.CTkEntry(
            form,
            width=280,
            placeholder_text="Dentist"
        )

        self.category.grid(
            row=0,
            column=1,
            padx=10,
            pady=10,
            sticky="w"
        )

        # Country

        ctk.CTkLabel(
            form,
            text="Country"
        ).grid(
            row=1,
            column=0,
            padx=15,
            pady=15,
            sticky="w"
        )

        self.country = ctk.CTkEntry(
            form,
            width=280,
            placeholder_text="United States"
        )

        self.country.grid(
            row=1,
            column=1,
            padx=10,
            pady=10,
            sticky="w"
        )

        # State

        ctk.CTkLabel(
            form,
            text="State (Optional)"
        ).grid(
            row=2,
            column=0,
            padx=15,
            pady=15,
            sticky="w"
        )

        self.state = ctk.CTkEntry(
            form,
            width=280,
            placeholder_text="Texas"
        )

        self.state.grid(
            row=2,
            column=1,
            padx=10,
            pady=10,
            sticky="w"
        )

        # City

        ctk.CTkLabel(
            form,
            text="City (Optional)"
        ).grid(
            row=3,
            column=0,
            padx=15,
            pady=15,
            sticky="w"
        )

        self.city = ctk.CTkEntry(
            form,
            width=280,
            placeholder_text="Dallas"
        )

        self.city.grid(
            row=3,
            column=1,
            padx=10,
            pady=10,
            sticky="w"
        )

        # Maximum Results

        ctk.CTkLabel(
            form,
            text="Maximum Results"
        ).grid(
            row=4,
            column=0,
            padx=15,
            pady=15,
            sticky="w"
        )

        self.max_results = ctk.CTkOptionMenu(
            form,
            values=[
                "25",
                "50",
                "100",
                "200",
                "500"
            ]
        )

        self.max_results.set("50")

        self.max_results.grid(
            row=4,
            column=1,
            padx=10,
            pady=10,
            sticky="w"
        )

        # =====================================
        # BUTTONS
        # =====================================

        button_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        button_frame.pack(
            pady=20
        )

        self.start_button = ctk.CTkButton(
            button_frame,
            text="▶ Start Search",
            width=180,
            height=42,
            command=self.start_search
        )

        self.start_button.pack(
            side="left",
            padx=10
        )

        self.stop_button = ctk.CTkButton(
            button_frame,
            text="■ Stop",
            width=120,
            height=42,
            fg_color="red",
            hover_color="#B00020"
        )

        self.stop_button.pack(
            side="left",
            padx=10
        )

        # =====================================
        # PROGRESS BAR
        # =====================================

        self.progress = ctk.CTkProgressBar(self)

        self.progress.pack(
            fill="x",
            padx=30,
            pady=(5,15)
        )

        self.progress.set(0)

        # =====================================
        # STATUS
        # =====================================

        self.status = ctk.CTkLabel(
            self,
            text="Ready",
            font=("Segoe UI", 15)
        )

        self.status.pack(
            pady=10
        )

    # =====================================
    # START SEARCH
    # =====================================

    def start_search(self):

        category = self.category.get().strip()
        country = self.country.get().strip()
        state = self.state.get().strip()
        city = self.city.get().strip()

        if category == "" or country == "":
            self.status.configure(
                text="Please enter Business Category and Country."
            )
            return

        # Build location string
        location_parts = []

        if city:
            location_parts.append(city)

        if state:
            location_parts.append(state)

        location_parts.append(country)

        location = ", ".join(location_parts)

        limit = int(self.max_results.get())

        self.progress.set(0)

        self.status.configure(
            text="Searching Google Maps..."
        )

        self.update()

        scraper = GoogleMapsScraper()

        results = scraper.search_businesses(
            category,
            location,
            limit
        )
        print(results)
        print(len(results))
        
        self.progress.set(1)

        if results.empty:
            self.status.configure(
                text="No businesses found."
            )
            return

        self.app.results_page.load_dataframe(results)

        from ui.results import Results

        self.app.change_page(Results)

        self.status.configure(
            text=f"{len(results)} leads found."
        )