import customtkinter as ctk
from src.agent.models.theme import Theme

class AppleButton(ctk.CTkButton):
    """
    Apple iOS style primary button.
    Minimalist, fully rounded, pure solid color without hard borders.
    """
    def __init__(self, master, variant="primary", **kwargs):
        # Determine color based on variant
        if variant == "primary":
            fg_color = Theme.PRIMARY
            hover_color = Theme.PRIMARY_HOVER
        elif variant == "success":
            fg_color = Theme.SUCCESS
            hover_color = Theme.SUCCESS_HOVER
        elif variant == "danger":
            fg_color = Theme.DANGER
            hover_color = Theme.DANGER
        else: # secondary/muted
            fg_color = Theme.CARD
            hover_color = Theme.BORDER

        # Default iOS-style properties
        default_kwargs = {
            "corner_radius": 12,
            "fg_color": fg_color,
            "hover_color": hover_color,
            "text_color": Theme.TEXT,
            "font": ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
            "height": 45,
            "border_width": 0
        }
        default_kwargs.update(kwargs)
        
        super().__init__(master, **default_kwargs)

class AppleInput(ctk.CTkEntry):
    """
    Apple style text input.
    Soft gray background, subtle borders, high padding.
    """
    def __init__(self, master, **kwargs):
        default_kwargs = {
            "corner_radius": 10,
            "fg_color": Theme.INPUT,
            "border_color": Theme.BORDER,
            "border_width": 1,
            "text_color": Theme.TEXT,
            "height": 45,
            "font": ctk.CTkFont(family="Helvetica", size=14)
        }
        default_kwargs.update(kwargs)
        super().__init__(master, **default_kwargs)

class AppleCard(ctk.CTkFrame):
    """
    Apple style container card.
    Minimalist background, rounded corners.
    """
    def __init__(self, master, **kwargs):
        default_kwargs = {
            "corner_radius": 16,
            "fg_color": Theme.CARD,
            "border_width": 1,
            "border_color": Theme.BORDER
        }
        default_kwargs.update(kwargs)
        super().__init__(master, **default_kwargs)

class AppleHeading(ctk.CTkLabel):
    """
    Apple style typography for headings.
    """
    def __init__(self, master, size=24, **kwargs):
        default_kwargs = {
            "font": ctk.CTkFont(family="Helvetica", size=size, weight="bold"),
            "text_color": Theme.TEXT
        }
        default_kwargs.update(kwargs)
        super().__init__(master, **default_kwargs)

class AppleSubText(ctk.CTkLabel):
    """
    Apple style typography for secondary text (muted gray).
    """
    def __init__(self, master, size=13, **kwargs):
        default_kwargs = {
            "font": ctk.CTkFont(family="Helvetica", size=size),
            "text_color": Theme.MUTED
        }
        default_kwargs.update(kwargs)
        super().__init__(master, **default_kwargs)
