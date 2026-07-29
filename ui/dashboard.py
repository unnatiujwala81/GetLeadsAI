import customtkinter as ctk


class Dashboard(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)

        self.build_ui()

    def build_ui(self):

        # --------------------------
        # Welcome
        # --------------------------
        title = ctk.CTkLabel(
            self,
            text="Welcome to GetLeadsAI",
            font=("Segoe UI", 28, "bold")
        )
        title.pack(anchor="w", padx=25, pady=(25, 5))

        subtitle = ctk.CTkLabel(
            self,
            text="Find businesses without websites and generate high-quality leads.",
            font=("Segoe UI", 15)
        )
        subtitle.pack(anchor="w", padx=25, pady=(0, 25))

        # --------------------------
        # Statistics
        # --------------------------
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(fill="x", padx=20)

        stats = [
            ("Total Leads", "0"),
            ("No Website", "0"),
            ("Emails", "0"),
            ("Phones", "0"),
            ("Exports", "0")
        ]

        for text, value in stats:

            card = ctk.CTkFrame(
                cards,
                width=180,
                height=120
            )

            card.pack(side="left", padx=10)
            card.pack_propagate(False)

            ctk.CTkLabel(
                card,
                text=text,
                font=("Segoe UI", 16, "bold")
            ).pack(pady=(20, 5))

            ctk.CTkLabel(
                card,
                text=value,
                font=("Segoe UI", 34, "bold")
            ).pack()