import customtkinter as ctk
import threading

from services.google_maps_scraper import GoogleMapsScraper
from services.location_service import LocationService


# =========================================================
# SCROLLABLE DROPDOWN
# =========================================================

class ScrollableDropdown(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        values=None,
        width=280,
        height=40,
        command=None,
        placeholder="Select"
    ):

        super().__init__(
            parent,
            width=width,
            height=height,
            fg_color="transparent"
        )

        self.values = values or []
        self.command = command
        self.placeholder = placeholder
        self.popup = None

        # -------------------------------------------------
        # MAIN BUTTON
        # -------------------------------------------------

        self.button = ctk.CTkButton(
            self,
            text=f"{placeholder}  ▼",
            width=width,
            height=height,
            anchor="w",
            command=self.open_dropdown
        )

        self.button.pack(
            fill="both",
            expand=True
        )

    # =====================================================
    # SET VALUES
    # =====================================================

    def set_values(self, values):

        self.values = list(values or [])

        # Close popup if values are being replaced
        self.close_dropdown()

    # =====================================================
    # SET VALUE
    # =====================================================

    def set(self, value):

        self.button.configure(
            text=f"{value}  ▼"
        )

    # =====================================================
    # GET VALUE
    # =====================================================

    def get(self):

        value = self.button.cget("text")

        if value.endswith("  ▼"):
            value = value[:-3]

        return value.strip()

    # =====================================================
    # OPEN DROPDOWN
    # =====================================================

    def open_dropdown(self):

        # Close an existing popup
        self.close_dropdown()

        if not self.values:
            return

        # Ignore temporary messages
        if len(self.values) == 1 and self.values[0] in [
            "Loading countries...",
            "Loading states...",
            "Loading cities...",
            "Unable to load countries",
            "No states available",
            "No cities available",
            "Select State",
            "Select City"
        ]:
            return

        self.update_idletasks()

        # -------------------------------------------------
        # POSITION
        # -------------------------------------------------

        x = self.winfo_rootx()

        below_y = (
            self.winfo_rooty()
            + self.winfo_height()
        )

        popup_width = max(
            self.winfo_width(),
            280
        )

        popup_height = 320

        screen_height = self.winfo_screenheight()

        # If there isn't enough space below,
        # show popup above the dropdown.
        if below_y + popup_height > screen_height:

            y = (
                self.winfo_rooty()
                - popup_height
            )

        else:

            y = below_y

        # -------------------------------------------------
        # POPUP
        # -------------------------------------------------

        self.popup = ctk.CTkToplevel(
            self
        )

        self.popup.title(
            "Select"
        )

        self.popup.geometry(
            f"{popup_width}x{popup_height}+{x}+{y}"
        )

        self.popup.resizable(
            False,
            False
        )

        # -------------------------------------------------
        # POPUP FRAME
        # -------------------------------------------------

        popup_frame = ctk.CTkFrame(
            self.popup,
            corner_radius=8
        )

        popup_frame.pack(
            fill="both",
            expand=True,
            padx=3,
            pady=3
        )

        # -------------------------------------------------
        # SCROLLABLE FRAME
        # -------------------------------------------------

        scroll_frame = ctk.CTkScrollableFrame(
            popup_frame,
            width=popup_width - 25,
            height=popup_height - 25
        )

        scroll_frame.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        # -------------------------------------------------
        # OPTIONS
        # -------------------------------------------------

        for value in self.values:

            option = ctk.CTkButton(
                scroll_frame,
                text=str(value),
                height=36,
                anchor="w",
                fg_color="transparent",
                hover_color=(
                    "gray80",
                    "gray25"
                ),
                text_color=(
                    "black",
                    "white"
                ),
                command=lambda v=value:
                    self.select_value(v)
            )

            option.pack(
                fill="x",
                padx=2,
                pady=1
            )

        # Focus popup
        self.popup.focus_force()

    # =====================================================
    # SELECT VALUE
    # =====================================================

    def select_value(self, value):

        # Set selected value
        self.set(value)

        # Close popup
        self.close_dropdown()

        # Notify parent
        if self.command:

            self.command(
                value
            )

    # =====================================================
    # CLOSE DROPDOWN
    # =====================================================

    def close_dropdown(self):

        if self.popup is not None:

            try:

                if self.popup.winfo_exists():
                    self.popup.destroy()

            except Exception:
                pass

            self.popup = None


# =========================================================
# LEAD FINDER
# =========================================================

class LeadFinder(ctk.CTkFrame):

    def __init__(
        self,
        parent
    ):

        super().__init__(
            parent
        )

        # -------------------------------------------------
        # LOCATION SERVICE
        # -------------------------------------------------

        self.location_service = (
            LocationService()
        )

        # -------------------------------------------------
        # LOCATION DATA
        # -------------------------------------------------

        self.country_data = []
        self.state_data = []

        self.selected_country_code = ""

        # Used to prevent old API responses
        # from replacing newer selections.
        self.country_request_id = 0
        self.state_request_id = 0
        self.city_request_id = 0

        # -------------------------------------------------
        # BUILD UI
        # -------------------------------------------------

        self.build_ui()

        # -------------------------------------------------
        # LOAD COUNTRIES
        # -------------------------------------------------

        self.load_countries()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        # =================================================
        # TITLE
        # =================================================

        title = ctk.CTkLabel(
            self,
            text="Find New Leads",
            font=(
                "Segoe UI",
                28,
                "bold"
            )
        )

        title.pack(
            anchor="w",
            padx=30,
            pady=(20, 20)
        )

        # =================================================
        # FORM
        # =================================================

        form = ctk.CTkFrame(
            self
        )

        form.pack(
            fill="x",
            padx=30,
            pady=10
        )

        # =================================================
        # BUSINESS CATEGORY
        # =================================================

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

        # =================================================
        # COUNTRY
        # =================================================

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

        self.country = ScrollableDropdown(
            form,
            values=[],
            width=280,
            command=self.country_changed,
            placeholder="Loading countries..."
        )

        self.country.grid(
            row=1,
            column=1,
            padx=10,
            pady=10,
            sticky="w"
        )

        # =================================================
        # STATE
        # =================================================

        ctk.CTkLabel(
            form,
            text="State"
        ).grid(
            row=2,
            column=0,
            padx=15,
            pady=15,
            sticky="w"
        )

        self.state = ScrollableDropdown(
            form,
            values=[],
            width=280,
            command=self.state_changed,
            placeholder="Select State"
        )

        self.state.set(
            "Select State"
        )

        self.state.grid(
            row=2,
            column=1,
            padx=10,
            pady=10,
            sticky="w"
        )

        # =================================================
        # CITY
        # =================================================

        ctk.CTkLabel(
            form,
            text="City"
        ).grid(
            row=3,
            column=0,
            padx=15,
            pady=15,
            sticky="w"
        )

        self.city = ScrollableDropdown(
            form,
            values=[],
            width=280,
            placeholder="Select City"
        )

        self.city.set(
            "Select City"
        )

        self.city.grid(
            row=3,
            column=1,
            padx=10,
            pady=10,
            sticky="w"
        )

        # =================================================
        # MAXIMUM RESULTS
        # =================================================

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
                "10",
                "25",
                "50",
                "100",
                "200",
                "500"
            ]
        )

        self.max_results.set(
            "10"
        )

        self.max_results.grid(
            row=4,
            column=1,
            padx=10,
            pady=10,
            sticky="w"
        )

        # =================================================
        # BUTTONS
        # =================================================

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

        # =================================================
        # PROGRESS
        # =================================================

        self.progress = ctk.CTkProgressBar(
            self
        )

        self.progress.pack(
            fill="x",
            padx=30,
            pady=(5, 15)
        )

        self.progress.set(
            0
        )

        # =================================================
        # STATUS
        # =================================================

        self.status = ctk.CTkLabel(
            self,
            text="Ready",
            font=(
                "Segoe UI",
                15
            )
        )

        self.status.pack(
            pady=10
        )

    # =====================================================
    # LOAD COUNTRIES
    # =====================================================

    def load_countries(self):

        self.status.configure(
            text="Loading countries..."
        )

        self.country.set(
            "Loading countries..."
        )

        self.country_request_id += 1

        request_id = (
            self.country_request_id
        )

        thread = threading.Thread(
            target=self._load_countries_thread,
            args=(request_id,),
            daemon=True
        )

        thread.start()

    # =====================================================
    # COUNTRY API THREAD
    # =====================================================

    def _load_countries_thread(
        self,
        request_id
    ):

        try:

            countries = (
                self.location_service
                .get_countries()
            )

        except Exception as e:

            print(
                f"Country loading error: {e}"
            )

            countries = []

        self.after(
            0,
            lambda:
            self._countries_loaded(
                countries,
                request_id
            )
        )

    # =====================================================
    # COUNTRIES LOADED
    # =====================================================

    def _countries_loaded(
        self,
        countries,
        request_id
    ):

        # Ignore old request
        if request_id != self.country_request_id:
            return

        if not countries:

            self.country_data = []

            self.country.set_values(
                []
            )

            self.country.set(
                "Unable to load countries"
            )

            self.status.configure(
                text="Could not load location data."
            )

            return

        self.country_data = countries

        # -------------------------------------------------
        # EXTRACT COUNTRY NAMES
        # -------------------------------------------------

        country_names = []

        for country in countries:

            if isinstance(
                country,
                dict
            ):

                name = country.get(
                    "name",
                    ""
                )

            else:

                name = str(
                    country
                )

            if name:

                country_names.append(
                    name.strip()
                )

        country_names = sorted(
            list(
                set(country_names)
            ),
            key=lambda x: x.lower()
        )

        if not country_names:

            self.country.set_values(
                []
            )

            self.country.set(
                "Unable to load countries"
            )

            self.status.configure(
                text="Could not load location data."
            )

            return

        # -------------------------------------------------
        # SET COUNTRY LIST
        # -------------------------------------------------

        self.country.set_values(
            country_names
        )

        # -------------------------------------------------
        # AUTOMATICALLY SELECT UNITED STATES
        # -------------------------------------------------

        selected_country = None

        for name in country_names:

            if name.lower() == "united states":

                selected_country = name
                break

        if selected_country is None:

            selected_country = (
                country_names[0]
            )

        self.country.set(
            selected_country
        )

        # -------------------------------------------------
        # LOAD STATES
        # -------------------------------------------------

        self.country_changed(
            selected_country
        )

    # =====================================================
    # COUNTRY CHANGED
    # =====================================================

    def country_changed(
        self,
        selected_country
    ):

        if not selected_country:
            return

        if selected_country in [
            "Select Country",
            "Loading countries...",
            "Unable to load countries"
        ]:
            return

        # -------------------------------------------------
        # FIND COUNTRY CODE
        # -------------------------------------------------

        country_code = ""

        for country in self.country_data:

            if not isinstance(
                country,
                dict
            ):
                continue

            name = country.get(
                "name",
                ""
            )

            if name == selected_country:

                country_code = (
                    country.get(
                        "code",
                        ""
                    )
                )

                break

        if not country_code:

            self.status.configure(
                text="Country code not found."
            )

            return

        self.selected_country_code = (
            country_code
        )

        print(
            "Selected country:",
            selected_country
        )

        print(
            "Country code:",
            country_code
        )

        # -------------------------------------------------
        # CLEAR STATE AND CITY
        # -------------------------------------------------

        self.state.set_values(
            []
        )

        self.state.set(
            "Loading states..."
        )

        self.city.set_values(
            []
        )

        self.city.set(
            "Select City"
        )

        self.status.configure(
            text=(
                f"Loading states for "
                f"{selected_country}..."
            )
        )

        # -------------------------------------------------
        # NEW STATE REQUEST ID
        # -------------------------------------------------

        self.state_request_id += 1

        request_id = (
            self.state_request_id
        )

        thread = threading.Thread(
            target=self._load_states_thread,
            args=(
                country_code,
                request_id
            ),
            daemon=True
        )

        thread.start()

    # =====================================================
    # LOAD STATES THREAD
    # =====================================================

    def _load_states_thread(
        self,
        country_code,
        request_id
    ):

        try:

            states = (
                self.location_service
                .get_states(
                    country_code
                )
            )

        except Exception as e:

            print(
                f"State loading error: {e}"
            )

            states = []

        self.after(
            0,
            lambda:
            self._states_loaded(
                states,
                country_code,
                request_id
            )
        )

    # =====================================================
    # STATES LOADED
    # =====================================================

    def _states_loaded(
        self,
        states,
        country_code,
        request_id
    ):

        # Ignore old response
        if request_id != self.state_request_id:
            return

        # Ignore if user already selected another country
        if country_code != self.selected_country_code:
            return

        self.state_data = (
            states or []
        )

        if not states:

            self.state.set_values(
                []
            )

            self.state.set(
                "No states available"
            )

            self.city.set_values(
                []
            )

            self.city.set(
                "Select City"
            )

            self.status.configure(
                text="No states available."
            )

            return

        # -------------------------------------------------
        # EXTRACT STATE NAMES
        # -------------------------------------------------

        state_names = []

        for state in states:

            if isinstance(
                state,
                dict
            ):

                name = state.get(
                    "name",
                    ""
                )

            else:

                name = str(
                    state
                )

            if name:

                state_names.append(
                    name.strip()
                )

        state_names = sorted(
            list(
                set(state_names)
            ),
            key=lambda x: x.lower()
        )

        if not state_names:

            self.state.set_values(
                []
            )

            self.state.set(
                "No states available"
            )

            self.status.configure(
                text="No states available."
            )

            return

        # -------------------------------------------------
        # SET STATE DROPDOWN
        # -------------------------------------------------

        self.state.set_values(
            state_names
        )

        # Do NOT automatically select a state
        self.state.set(
            "Select State"
        )

        self.city.set_values(
            []
        )

        self.city.set(
            "Select City"
        )

        self.status.configure(
            text="Select a state."
        )

    # =====================================================
    # STATE CHANGED
    # =====================================================

    def state_changed(
        self,
        selected_state
    ):

        if not selected_state:
            return

        if selected_state in [
            "Select State",
            "Loading states...",
            "No states available"
        ]:
            return

        # -------------------------------------------------
        # FIND STATE CODE
        # -------------------------------------------------

        state_code = ""

        for state in self.state_data:

            if not isinstance(
                state,
                dict
            ):
                continue

            name = state.get(
                "name",
                ""
            )

            if name == selected_state:

                state_code = (
                    state.get(
                        "code",
                        ""
                    )
                )

                break

        print(
            "Selected state:",
            selected_state
        )

        print(
            "State code:",
            state_code
        )

        if not state_code:

            self.city.set_values(
                []
            )

            self.city.set(
                "No cities available"
            )

            self.status.configure(
                text="State code not found."
            )

            return

        # -------------------------------------------------
        # CLEAR CITY
        # -------------------------------------------------

        self.city.set_values(
            []
        )

        self.city.set(
            "Loading cities..."
        )

        self.status.configure(
            text="Loading cities..."
        )

        # -------------------------------------------------
        # NEW CITY REQUEST ID
        # -------------------------------------------------

        self.city_request_id += 1

        request_id = (
            self.city_request_id
        )

        country_code = (
            self.selected_country_code
        )

        # -------------------------------------------------
        # LOAD CITIES IN BACKGROUND
        # -------------------------------------------------

        thread = threading.Thread(
            target=self._load_cities_thread,
            args=(
                country_code,
                state_code,
                request_id
            ),
            daemon=True
        )

        thread.start()

    # =====================================================
    # LOAD CITIES THREAD
    # =====================================================

    def _load_cities_thread(
        self,
        country_code,
        state_code,
        request_id
    ):

        try:

            cities = (
                self.location_service
                .get_cities(
                    country_code,
                    state_code
                )
            )

        except Exception as e:

            print(
                f"City loading error: {e}"
            )

            cities = []

        self.after(
            0,
            lambda:
            self._cities_loaded(
                cities,
                request_id,
                country_code
            )
        )

    # =====================================================
    # CITIES LOADED
    # =====================================================

    def _cities_loaded(
        self,
        cities,
        request_id,
        country_code
    ):

        # Ignore old response
        if request_id != self.city_request_id:
            return

        # Ignore if country changed
        if country_code != self.selected_country_code:
            return

        if not cities:

            self.city.set_values(
                []
            )

            self.city.set(
                "No cities available"
            )

            self.status.configure(
                text="No cities available."
            )

            return

        # -------------------------------------------------
        # EXTRACT CITY NAMES
        # -------------------------------------------------

        city_names = []

        for city in cities:

            if isinstance(
                city,
                dict
            ):

                name = city.get(
                    "name",
                    ""
                )

            else:

                name = str(
                    city
                )

            if name:

                city_names.append(
                    name.strip()
                )

        city_names = sorted(
            list(
                set(city_names)
            ),
            key=lambda x: x.lower()
        )

        if not city_names:

            self.city.set_values(
                []
            )

            self.city.set(
                "No cities available"
            )

            self.status.configure(
                text="No cities available."
            )

            return

        # -------------------------------------------------
        # SET CITY DROPDOWN
        # -------------------------------------------------

        self.city.set_values(
            city_names
        )

        # Do NOT automatically select first city
        self.city.set(
            "Select City"
        )

        self.status.configure(
            text="Ready"
        )

    # =====================================================
    # START SEARCH
    # =====================================================

    def start_search(self):

        category = (
            self.category.get()
            .strip()
        )

        country = (
            self.country.get()
            .strip()
        )

        state = (
            self.state.get()
            .strip()
        )

        city = (
            self.city.get()
            .strip()
        )

        # =================================================
        # VALIDATION
        # =================================================

        if not category:

            self.status.configure(
                text="Please enter Business Category."
            )

            return

        if (
            not country
            or country in [
                "Loading countries...",
                "Unable to load countries"
            ]
        ):

            self.status.configure(
                text="Please select a Country."
            )

            return

        # -------------------------------------------------
        # OPTIONAL STATE
        # -------------------------------------------------

        if state in [
            "",
            "Select State",
            "Loading states...",
            "No states available"
        ]:

            state = ""

        # -------------------------------------------------
        # OPTIONAL CITY
        # -------------------------------------------------

        if city in [
            "",
            "Select City",
            "Loading cities...",
            "No cities available"
        ]:

            city = ""

        # =================================================
        # BUILD LOCATION
        # =================================================

        location_parts = []

        if city:

            location_parts.append(
                city
            )

        if state:

            location_parts.append(
                state
            )

        location_parts.append(
            country
        )

        location = ", ".join(
            location_parts
        )

        print(
            "Search location:",
            location
        )

        # =================================================
        # MAX RESULTS
        # =================================================

        limit = int(
            self.max_results.get()
        )

        self.progress.set(
            0
        )

        self.status.configure(
            text="Searching Google Maps..."
        )

        self.update_idletasks()

        # =================================================
        # SCRAPER
        # =================================================

        scraper = GoogleMapsScraper()

        results = (
            scraper.search_businesses(
                category,
                location,
                limit
            )
        )

        print(results)

        print(
            f"Results found: {len(results)}"
        )

        self.progress.set(
            1
        )

        # =================================================
        # NO RESULTS
        # =================================================

        if results.empty:

            self.status.configure(
                text="No businesses found."
            )

            return

        # =================================================
        # LOAD RESULTS
        # =================================================

        self.app.results_page.load_dataframe(
            results
        )

        from ui.results import Results

        self.app.change_page(
            Results
        )

        self.status.configure(
            text=(
                f"{len(results)} "
                f"leads found."
            )
        )

        