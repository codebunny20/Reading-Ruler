class DraftingBot:
    def __init__(self):
        self.platforms = {
            'twitter': {'max_length': 280},
            'facebook': {'max_length': 63206},
            'instagram': {'max_length': 2200},
            'linkedin': {'max_length': 1300}
        }

    def generate_post(self, content, platform):
        if platform not in self.platforms:
            raise ValueError("Unsupported platform")
        
        max_length = self.platforms[platform]['max_length']
        content = self._trim_to_platform(content, max_length)
        return content

    def _trim_to_platform(self, content: str, max_length: int, ellipsis: str = "...") -> str:
        """Trim content to max_length, ensuring final length <= max_length."""
        if content is None:
            content = ""
        if max_length <= 0:
            return ""
        if len(content) <= max_length:
            return content
        # Reserve room for ellipsis so we don't exceed max_length
        if len(ellipsis) >= max_length:
            return ellipsis[:max_length]
        return content[: max_length - len(ellipsis)] + ellipsis

    def get_preview(self, content: str, platform: str):
        """Return (draft, max_length, current_length, was_trimmed)."""
        if platform not in self.platforms:
            raise ValueError("Unsupported platform")
        max_length = self.platforms[platform]['max_length']
        draft = self._trim_to_platform(content, max_length)
        return draft, max_length, len(draft), (len(content or "") > max_length)

    def post_to_social_media(self, content, platform):
        draft = self.generate_post(content, platform)
        print(f"Draft for {platform}: {draft}")
        # Simulate posting to the platform
        print(f"Posted to {platform}: {draft}")


def run_tk_app():
    # Prefer CustomTkinter; fall back to tkinter/ttk if not installed.
    try:
        import customtkinter as ctk
        _USE_CTK = True
    except Exception:
        _USE_CTK = False

    if not _USE_CTK:
        import tkinter as tk
        from tkinter import ttk

        bot = DraftingBot()
        root = tk.Tk()
        root.title("Draftyy - Live Preview")

        platform_var = tk.StringVar(value="twitter")

        top = ttk.Frame(root, padding=10)
        top.grid(row=0, column=0, sticky="nsew")

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        top.columnconfigure(1, weight=1)
        top.rowconfigure(2, weight=1)

        ttk.Label(top, text="Platform").grid(row=0, column=0, sticky="w")
        platform_combo = ttk.Combobox(
            top,
            textvariable=platform_var,
            values=list(bot.platforms.keys()),
            state="readonly",
            width=20,
        )
        platform_combo.grid(row=0, column=0, sticky="w", pady=(4, 10))

        counter_var = tk.StringVar(value="0/0")
        trimmed_var = tk.StringVar(value="")
        counter_lbl = ttk.Label(top, textvariable=counter_var)
        counter_lbl.grid(row=0, column=1, sticky="e")
        trimmed_lbl = ttk.Label(top, textvariable=trimmed_var)
        trimmed_lbl.grid(row=1, column=1, sticky="e")

        ttk.Label(top, text="Input").grid(row=1, column=0, sticky="w")
        input_txt = tk.Text(top, height=8, wrap="word")
        input_txt.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(4, 10))

        ttk.Label(top, text="Live Preview (auto-trimmed)").grid(row=3, column=0, sticky="w")
        preview_txt = tk.Text(top, height=8, wrap="word", state="disabled")
        preview_txt.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(4, 10))
        top.rowconfigure(4, weight=1)

        btns = ttk.Frame(top)
        btns.grid(row=5, column=0, columnspan=2, sticky="e")

        status_var = tk.StringVar(value="")
        status_lbl = ttk.Label(top, textvariable=status_var)
        status_lbl.grid(row=6, column=0, columnspan=2, sticky="w", pady=(8, 0))

        def _get_input() -> str:
            return input_txt.get("1.0", "end-1c")

        def _set_preview(text: str):
            preview_txt.configure(state="normal")
            preview_txt.delete("1.0", "end")
            preview_txt.insert("1.0", text)
            preview_txt.configure(state="disabled")

        def update_preview(*_):
            try:
                content = _get_input()
                platform = platform_var.get()
                draft, max_len, cur_len, was_trimmed = bot.get_preview(content, platform)
                _set_preview(draft)
                counter_var.set(f"{cur_len}/{max_len}")
                trimmed_var.set("trimmed" if was_trimmed else "")
                status_var.set("")
            except Exception as e:
                status_var.set(str(e))

        def copy_to_clipboard():
            draft = bot.generate_post(_get_input(), platform_var.get())
            root.clipboard_clear()
            root.clipboard_append(draft)
            root.update()
            status_var.set("Copied draft to clipboard.")

        def simulate_post():
            bot.post_to_social_media(_get_input(), platform_var.get())
            status_var.set("Simulated posting in console.")

        ttk.Button(btns, text="Copy to clipboard", command=copy_to_clipboard).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(btns, text="Simulate post", command=simulate_post).grid(row=0, column=1)

        input_txt.bind("<KeyRelease>", update_preview)
        platform_combo.bind("<<ComboboxSelected>>", update_preview)

        update_preview()
        root.minsize(520, 520)
        root.mainloop()
        return

    # --- CustomTkinter UI
    import tkinter as tk  # StringVar
    bot = DraftingBot()

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Draftyy - Live Preview")

    platform_var = tk.StringVar(value="twitter")
    counter_var = tk.StringVar(value="0/0")
    trimmed_var = tk.StringVar(value="")
    status_var = tk.StringVar(value="")

    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    top = ctk.CTkFrame(root)
    top.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
    top.grid_columnconfigure(0, weight=1)
    top.grid_columnconfigure(1, weight=0)
    top.grid_rowconfigure(3, weight=1)
    top.grid_rowconfigure(5, weight=1)

    ctk.CTkLabel(top, text="Platform").grid(row=0, column=0, sticky="w")
    ctk.CTkLabel(top, textvariable=counter_var).grid(row=0, column=1, sticky="e")

    platform_combo = ctk.CTkComboBox(
        top,
        values=list(bot.platforms.keys()),
        variable=platform_var,
        state="readonly",
        width=180,
    )
    platform_combo.grid(row=1, column=0, sticky="w", pady=(6, 10))
    ctk.CTkLabel(top, textvariable=trimmed_var).grid(row=1, column=1, sticky="e", pady=(6, 10))

    ctk.CTkLabel(top, text="Input").grid(row=2, column=0, sticky="w")
    input_txt = ctk.CTkTextbox(top, wrap="word", height=140)
    input_txt.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(6, 12))

    ctk.CTkLabel(top, text="Live Preview (auto-trimmed)").grid(row=4, column=0, sticky="w")
    preview_txt = ctk.CTkTextbox(top, wrap="word", height=140)
    preview_txt.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=(6, 12))
    preview_txt.configure(state="disabled")

    btns = ctk.CTkFrame(top, fg_color="transparent")
    btns.grid(row=6, column=0, columnspan=2, sticky="e")

    def _get_input() -> str:
        return input_txt.get("1.0", "end-1c")

    def _set_preview(text: str):
        preview_txt.configure(state="normal")
        preview_txt.delete("1.0", "end")
        preview_txt.insert("1.0", text)
        preview_txt.configure(state="disabled")

    def update_preview(*_):
        try:
            content = _get_input()
            platform = platform_var.get()
            draft, max_len, cur_len, was_trimmed = bot.get_preview(content, platform)
            _set_preview(draft)
            counter_var.set(f"{cur_len}/{max_len}")
            trimmed_var.set("trimmed" if was_trimmed else "")
            status_var.set("")
        except Exception as e:
            status_var.set(str(e))

    def copy_to_clipboard():
        draft = bot.generate_post(_get_input(), platform_var.get())
        root.clipboard_clear()
        root.clipboard_append(draft)
        root.update()
        status_var.set("Copied draft to clipboard.")

    def simulate_post():
        bot.post_to_social_media(_get_input(), platform_var.get())
        status_var.set("Simulated posting in console.")

    ctk.CTkButton(btns, text="Copy to clipboard", command=copy_to_clipboard).grid(row=0, column=0, padx=(0, 8))
    ctk.CTkButton(btns, text="Simulate post", command=simulate_post).grid(row=0, column=1)

    ctk.CTkLabel(top, textvariable=status_var).grid(row=7, column=0, columnspan=2, sticky="w", pady=(6, 0))

    input_txt.bind("<KeyRelease>", update_preview)
    platform_combo.bind("<<ComboboxSelected>>", update_preview)

    update_preview()
    root.minsize(560, 620)
    root.mainloop()


# Example usage
if __name__ == "__main__":
    run_tk_app()