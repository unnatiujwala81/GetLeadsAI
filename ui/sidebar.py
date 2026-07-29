import customtkinter as ctk

from ui.dashboard import Dashboard
from ui.lead_finder import LeadFinder
from ui.results import Results


class Sidebar(ctk.CTkFrame):

    def __init__(self, parent, page_callback):
        super().__init__(parent, width=220)

        self.page_callback = page_callback

        self.build_ui()

    def build_ui(self):

        # Title
        title = ctk.CTkLabel(
            self,
            text="🚀 GetLeadsAI",
            font=("Segoe UI", 24, "bold")
        )
        title.pack(pady=(30, 40))

        # Navigation Buttons
        pages = [
            ("🏠 Dashboard", Dashboard),
            ("🔍 Lead Finder", LeadFinder),
            ("📊 Results", Results),
        ]

        for text, page in pages:

            button = ctk.CTkButton(
                self,
                text=text,
                width=180,
                height=45,
                anchor="w",
                command=lambda p=page: self.page_callback(p)
            )

            button.pack(padx=15, pady=8, fill="x")

        # Status
        ctk.CTkLabel(
            self,
            text="🟢 Ready",
            font=("Segoe UI", 12)
        ).pack(side="bottom", pady=20)