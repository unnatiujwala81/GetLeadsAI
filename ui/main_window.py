import customtkinter as ctk

from ui.sidebar import Sidebar
from ui.dashboard import Dashboard
from ui.lead_finder import LeadFinder
from ui.results import Results


class GetLeadsAI(ctk.CTk):

    def __init__(self):
        super().__init__()

        # ----------------------------
        # Window
        # ----------------------------
        self.title("GetLeadsAI")
        self.geometry("1400x800")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ----------------------------
        # Sidebar
        # ----------------------------
        self.sidebar = Sidebar(
            self,
            self.change_page
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        # ----------------------------
        # Right Side
        # ----------------------------
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.pack(
            side="right",
            fill="both",
            expand=True
        )

        # ----------------------------
        # Header
        # ----------------------------
        self.header = ctk.CTkFrame(
            self.right_frame,
            height=60
        )

        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        self.page_title = ctk.CTkLabel(
            self.header,
            text="Dashboard",
            font=("Segoe UI", 24, "bold")
        )

        self.page_title.pack(
            side="left",
            padx=20
        )

        # ----------------------------
        # Content Area
        # ----------------------------
        self.content = ctk.CTkFrame(self.right_frame)
        self.content.pack(
            fill="both",
            expand=True
        )

        # ----------------------------
        # Create ALL Pages Once
        # ----------------------------
        self.dashboard_page = Dashboard(self.content)

        self.leadfinder_page = LeadFinder(self.content)
        self.leadfinder_page.app = self

        self.results_page = Results(self.content)

        # Place every page in same position
        for page in (
            self.dashboard_page,
            self.leadfinder_page,
            self.results_page
        ):
            page.place(
                relx=0,
                rely=0,
                relwidth=1,
                relheight=1
            )

        # Show Dashboard
        self.change_page(Dashboard)

    # ------------------------------------------------
    # Change Page
    # ------------------------------------------------
    def change_page(self, page):

        # Hide all pages
        self.dashboard_page.place_forget()
        self.leadfinder_page.place_forget()
        self.results_page.place_forget()

        # Show selected page
        if page == Dashboard:

            self.dashboard_page.place(
                relx=0,
                rely=0,
                relwidth=1,
                relheight=1
            )

            self.page_title.configure(
                text="Dashboard"
            )

        elif page == LeadFinder:

            self.leadfinder_page.place(
                relx=0,
                rely=0,
                relwidth=1,
                relheight=1
            )

            self.page_title.configure(
                text="Lead Finder"
            )

        elif page == Results:

            self.results_page.place(
                relx=0,
                rely=0,
                relwidth=1,
                relheight=1
            )

            self.page_title.configure(
                text="Results"
            )