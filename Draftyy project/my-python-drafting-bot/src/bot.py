class DraftingBot:
    def __init__(self):
        self.platforms = {
            'twitter': {
                'max_length': 280,
                'tco_url_length': 23,
                'media_short_url_length': 23,
                'count_links_as_tco': True,
            },
            'facebook': {
                'max_length': 63206,
                'see_more_cutoff': 480,
            },
            'instagram': {
                'max_length': 2200,
                'hashtag_limit': 30,
            },
            'linkedin': {
                'max_length': 1300,
                'see_more_cutoff': 210,
                'normalize_line_breaks': True,
            }
        }

    def generate_post(self, content, platform, *, enforce_rules: bool = True):
        if platform not in self.platforms:
            raise ValueError("Unsupported platform")

        rules = self.platforms[platform]
        content = (content or "")

        content, _warnings = self._apply_platform_rules(content, platform, rules, enforce=enforce_rules)
        content = self._trim_to_platform_effective(content, platform, rules)
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

    def _trim_to_platform_effective(self, content: str, platform: str, rules: dict, ellipsis: str = "...") -> str:
        """Trim content so that effective length (platform rules) <= max_length."""
        max_length = int(rules.get("max_length", 0))
        if max_length <= 0:
            return ""
        if self._effective_length(content, platform, rules) <= max_length:
            return content

        # Ensure the final string (with ellipsis) fits by effective length, not raw length.
        if self._effective_length(ellipsis, platform, rules) >= max_length:
            # Worst-case safe fallback
            return ellipsis

        lo, hi = 0, len(content)
        best = ""
        budget = max_length - self._effective_length(ellipsis, platform, rules)
        while lo <= hi:
            mid = (lo + hi) // 2
            candidate = content[:mid]
            if self._effective_length(candidate, platform, rules) <= budget:
                best = candidate
                lo = mid + 1
            else:
                hi = mid - 1
        return best + ellipsis

    def _effective_length(self, content: str, platform: str, rules: dict) -> int:
        """Compute platform-specific effective length (e.g., Twitter link counting)."""
        content = content or ""
        if platform != "twitter" or not rules.get("count_links_as_tco", False):
            return len(content)

        import re
        # Replace URLs with fixed-length t.co counts; extremely simplified but useful.
        url_re = re.compile(r"https?://\S+")
        tco_len = int(rules.get("tco_url_length", 23))

        effective = 0
        last = 0
        for m in url_re.finditer(content):
            effective += len(content[last:m.start()])
            effective += tco_len
            last = m.end()
        effective += len(content[last:])
        return effective

    def _apply_platform_rules(self, content: str, platform: str, rules: dict, enforce: bool) -> tuple[str, list[str]]:
        """Apply non-length constraints and return (content, warnings)."""
        warnings: list[str] = []
        text = content or ""

        if platform == "linkedin" and rules.get("normalize_line_breaks", False):
            # Normalize CRLF -> LF so preview matches common rendering expectations
            text = text.replace("\r\n", "\n").replace("\r", "\n")

        if platform == "instagram":
            hashtag_limit = rules.get("hashtag_limit")
            if hashtag_limit is not None:
                import re
                hashtags = re.findall(r"(?<!\w)#\w+", text)
                if len(hashtags) > int(hashtag_limit):
                    warnings.append(f"Instagram hashtag limit exceeded: {len(hashtags)}/{hashtag_limit}.")
                    if enforce:
                        # Remove extra hashtags after the first N (preserve non-hashtag text).
                        keep = set(hashtags[: int(hashtag_limit)])
                        def _strip_extra_hashtags(s: str) -> str:
                            def repl(m):
                                tag = m.group(0)
                                return tag if tag in keep else ""
                            out = re.sub(r"(?<!\w)#\w+", repl, s)
                            # Clean double spaces introduced by removals
                            out = re.sub(r"[ \t]{2,}", " ", out)
                            out = re.sub(r"\n{3,}", "\n\n", out)
                            return out.strip()
                        text = _strip_extra_hashtags(text)
                        warnings.append("Extra hashtags were removed to fit the limit (first 30 kept).")

        # "See more" style hints (preview-only warning)
        cutoff = rules.get("see_more_cutoff")
        if cutoff is not None and len(text) > int(cutoff):
            warnings.append(f"Likely to collapse behind “see more” after ~{cutoff} chars.")

        return text, warnings

    def _truncate_for_see_more_preview(
        self,
        content: str,
        *,
        cutoff: int | None,
        indicator: str = "... (see more...)",
    ) -> tuple[str, bool]:
        """Preview-only truncation that mimics 'see more' collapse behavior."""
        text = content or ""
        if cutoff is None:
            return text, False
        cutoff_i = int(cutoff)
        if cutoff_i <= 0 or len(text) <= cutoff_i:
            return text, False

        # Keep within cutoff, reserving space for indicator.
        if len(indicator) >= cutoff_i:
            return indicator[:cutoff_i], True
        return text[: cutoff_i - len(indicator)] + indicator, True

    def get_preview(self, content: str, platform: str, *, auto_trim: bool = True):
        """Return (draft, max_length, effective_length, was_trimmed, warnings)."""
        if platform not in self.platforms:
            raise ValueError("Unsupported platform")
        rules = self.platforms[platform]
        max_length = int(rules.get("max_length", 0))

        base = (content or "")
        processed, warnings = self._apply_platform_rules(base, platform, rules, enforce=False)

        # Preview-only: simulate 'see more' collapsed rendering when over cutoff.
        collapsed, did_collapse = self._truncate_for_see_more_preview(
            processed, cutoff=rules.get("see_more_cutoff")
        )

        # Separately: optional max-length trimming for the preview.
        draft = self._trim_to_platform_effective(collapsed, platform, rules) if auto_trim else collapsed

        eff_len = self._effective_length(draft, platform, rules)
        was_over_max = self._effective_length(collapsed, platform, rules) > max_length
        was_trimmed = (was_over_max if auto_trim else False) or did_collapse
        return draft, max_length, eff_len, was_trimmed, warnings

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

    # --- Shared controller (UI-agnostic) ---------------------------------
    def _build_controller(bot, *, platform_var, auto_trim_var, enforce_rules_var,
                          counter_var, remaining_var, trimmed_var, status_var, warnings_var,
                          get_input, set_preview, set_rules_text):
        def set_status(msg: str):
            status_var.set(msg or "")

        def set_warnings(lines: list[str]):
            warnings_var.set("\n".join(lines) if lines else "")

        def set_rules_panel(platform: str):
            rules = bot.platforms.get(platform, {})
            lines = []
            if "max_length" in rules:
                lines.append(f"Max length: {rules['max_length']} (Twitter uses effective length w/ t.co)")
            if platform == "twitter":
                lines.append(f"t.co URL length: {rules.get('tco_url_length', 23)}")
                lines.append("Links count as fixed length (approx).")
            if "hashtag_limit" in rules:
                lines.append(f"Hashtag limit: {rules['hashtag_limit']}")
            if "see_more_cutoff" in rules:
                lines.append(f"“See more” cutoff hint: ~{rules['see_more_cutoff']} chars")
            if rules.get("normalize_line_breaks"):
                lines.append("Line breaks normalized for preview.")
            set_rules_text("\n".join(lines) if lines else "No extra rules.")

        def update_preview(*_):
            try:
                content = get_input()
                platform = platform_var.get()
                draft, max_len, eff_len, was_trimmed, warnings = bot.get_preview(
                    content, platform, auto_trim=auto_trim_var.get()
                )
                set_preview(draft)
                counter_var.set(f"{eff_len}/{max_len}")
                remaining = max_len - eff_len
                remaining_var.set(f"Remaining: {remaining}" if remaining >= 0 else f"Over by: {-remaining}")
                trimmed_var.set("trimmed" if was_trimmed else "")
                set_warnings(warnings)
                set_status("")
                set_rules_panel(platform)
            except Exception as e:
                set_status(str(e))

        def copy_to_clipboard(clipboard_clear, clipboard_append, clipboard_flush):
            draft = bot.generate_post(get_input(), platform_var.get(), enforce_rules=enforce_rules_var.get())
            clipboard_clear()
            clipboard_append(draft)
            clipboard_flush()
            set_status("Copied draft to clipboard.")

        def simulate_post():
            bot.post_to_social_media(
                bot.generate_post(get_input(), platform_var.get(), enforce_rules=enforce_rules_var.get()),
                platform_var.get(),
            )
            set_status("Simulated posting in console.")

        return {
            "update_preview": update_preview,
            "copy_to_clipboard": copy_to_clipboard,
            "simulate_post": simulate_post,
        }

    # ---------------------------------------------------------------------

    if not _USE_CTK:
        import tkinter as tk
        from tkinter import ttk

        bot = DraftingBot()
        root = tk.Tk()
        root.title("Draftyy - Live Preview")

        # ---- Layout (two panes)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        main = ttk.Frame(root, padding=10)
        main.grid(row=0, column=0, sticky="nsew")
        main.columnconfigure(0, weight=1)  # left
        main.columnconfigure(1, weight=1)  # right
        main.rowconfigure(1, weight=1)

        # ---- State
        platform_var = tk.StringVar(value="twitter")
        auto_trim_var = tk.BooleanVar(value=True)
        enforce_rules_var = tk.BooleanVar(value=True)

        counter_var = tk.StringVar(value="0/0")
        remaining_var = tk.StringVar(value="")
        trimmed_var = tk.StringVar(value="")
        status_var = tk.StringVar(value="")
        warnings_var = tk.StringVar(value="")

        # ---- Left pane (controls + input)
        left = ttk.Frame(main)
        left.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 10))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(4, weight=1)

        ttk.Label(left, text="Platform").grid(row=0, column=0, sticky="w")
        platform_combo = ttk.Combobox(
            left,
            textvariable=platform_var,
            values=list(bot.platforms.keys()),
            state="readonly",
            width=24,
        )
        platform_combo.grid(row=1, column=0, sticky="w", pady=(4, 8))

        toggles = ttk.Frame(left)
        toggles.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        ttk.Checkbutton(toggles, text="Auto-trim preview", variable=auto_trim_var).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(toggles, text="Enforce rules on copy/post", variable=enforce_rules_var).grid(row=1, column=0, sticky="w")

        ttk.Label(left, text="Input").grid(row=3, column=0, sticky="w")
        input_txt = tk.Text(left, height=10, wrap="word")
        input_txt.grid(row=4, column=0, sticky="nsew", pady=(4, 10))

        btns = ttk.Frame(left)
        btns.grid(row=5, column=0, sticky="ew")
        btns.columnconfigure(0, weight=1)

        def _get_input() -> str:
            return input_txt.get("1.0", "end-1c")

        def _set_preview(text: str):
            preview_txt.configure(state="normal")
            preview_txt.delete("1.0", "end")
            preview_txt.insert("1.0", text)
            preview_txt.configure(state="disabled")

        def _set_rules_text(text: str):
            rules_text.configure(state="normal")
            rules_text.delete("1.0", "end")
            rules_text.insert("1.0", text)
            rules_text.configure(state="disabled")

        controller = _build_controller(
            bot,
            platform_var=platform_var,
            auto_trim_var=auto_trim_var,
            enforce_rules_var=enforce_rules_var,
            counter_var=counter_var,
            remaining_var=remaining_var,
            trimmed_var=trimmed_var,
            status_var=status_var,
            warnings_var=warnings_var,
            get_input=_get_input,
            set_preview=_set_preview,
            set_rules_text=_set_rules_text,
        )

        def clear_input():
            input_txt.delete("1.0", "end")
            controller["update_preview"]()

        def copy_to_clipboard():
            controller["copy_to_clipboard"](root.clipboard_clear, root.clipboard_append, root.update)

        def simulate_post():
            controller["simulate_post"]()

        ttk.Button(btns, text="Clear", command=clear_input).grid(row=0, column=0, sticky="w")
        ttk.Button(btns, text="Copy", command=copy_to_clipboard).grid(row=0, column=1, padx=(8, 0))
        ttk.Button(btns, text="Simulate post", command=simulate_post).grid(row=0, column=2, padx=(8, 0))

        # ---- Right pane (preview + info)
        right = ttk.Frame(main)
        right.grid(row=0, column=1, rowspan=2, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(3, weight=1)

        header = ttk.Frame(right)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Live Preview").grid(row=0, column=0, sticky="w")
        ttk.Label(header, textvariable=counter_var).grid(row=0, column=1, sticky="e")

        subheader = ttk.Frame(right)
        subheader.grid(row=1, column=0, sticky="ew", pady=(2, 8))
        subheader.columnconfigure(0, weight=1)
        ttk.Label(subheader, textvariable=remaining_var).grid(row=0, column=0, sticky="w")
        ttk.Label(subheader, textvariable=trimmed_var).grid(row=0, column=1, sticky="e")

        preview_txt = tk.Text(right, height=14, wrap="word", state="disabled")
        preview_txt.grid(row=3, column=0, sticky="nsew", pady=(0, 10))

        # Rules panel
        rules_box = ttk.LabelFrame(right, text="Platform rules (approx)")
        rules_box.grid(row=4, column=0, sticky="ew")
        rules_box.columnconfigure(0, weight=1)
        rules_text = tk.Text(rules_box, height=6, wrap="word", state="disabled")
        rules_text.grid(row=0, column=0, sticky="ew")

        ttk.Label(right, text="Warnings").grid(row=5, column=0, sticky="w", pady=(8, 2))
        warnings_lbl = ttk.Label(right, textvariable=warnings_var, foreground="#b26a00", wraplength=420, justify="left")
        warnings_lbl.grid(row=6, column=0, sticky="ew")

        ttk.Label(right, text="Status").grid(row=7, column=0, sticky="w", pady=(8, 2))
        status_lbl = ttk.Label(right, textvariable=status_var, wraplength=420, justify="left")
        status_lbl.grid(row=8, column=0, sticky="ew")

        input_txt.bind("<KeyRelease>", controller["update_preview"])
        platform_combo.bind("<<ComboboxSelected>>", controller["update_preview"])
        for var in (auto_trim_var, enforce_rules_var):
            var.trace_add("write", lambda *_: controller["update_preview"]())

        controller["update_preview"]()
        root.minsize(860, 560)
        root.mainloop()
        return

    # --- CustomTkinter UI
    import tkinter as tk  # StringVar/BooleanVar

    bot = DraftingBot()

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Draftyy - Live Preview")

    # ---- State
    platform_var = tk.StringVar(value="twitter")
    auto_trim_var = tk.BooleanVar(value=True)
    enforce_rules_var = tk.BooleanVar(value=True)

    counter_var = tk.StringVar(value="0/0")
    remaining_var = tk.StringVar(value="")
    trimmed_var = tk.StringVar(value="")
    status_var = tk.StringVar(value="")
    warnings_var = tk.StringVar(value="")

    # ---- Layout (two panes)
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    main = ctk.CTkFrame(root)
    main.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
    main.grid_columnconfigure(0, weight=1)
    main.grid_columnconfigure(1, weight=1)
    main.grid_rowconfigure(0, weight=1)

    left = ctk.CTkFrame(main)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    left.grid_columnconfigure(0, weight=1)
    left.grid_rowconfigure(5, weight=1)

    right = ctk.CTkFrame(main)
    right.grid(row=0, column=1, sticky="nsew")
    right.grid_columnconfigure(0, weight=1)
    right.grid_rowconfigure(3, weight=1)

    # ---- Left pane
    ctk.CTkLabel(left, text="Platform").grid(row=0, column=0, sticky="w")
    platform_combo = ctk.CTkComboBox(
        left, values=list(bot.platforms.keys()), variable=platform_var, state="readonly", width=220
    )
    platform_combo.grid(row=1, column=0, sticky="w", pady=(6, 10))

    ctk.CTkCheckBox(left, text="Auto-trim preview", variable=auto_trim_var).grid(row=2, column=0, sticky="w")
    ctk.CTkCheckBox(left, text="Enforce rules on copy/post", variable=enforce_rules_var).grid(row=3, column=0, sticky="w", pady=(0, 10))

    ctk.CTkLabel(left, text="Input").grid(row=4, column=0, sticky="w")
    input_txt = ctk.CTkTextbox(left, wrap="word", height=220)
    input_txt.grid(row=5, column=0, sticky="nsew", pady=(6, 12))

    btns = ctk.CTkFrame(left, fg_color="transparent")
    btns.grid(row=6, column=0, sticky="e")

    def _get_input() -> str:
        return input_txt.get("1.0", "end-1c")

    def _set_preview(text: str):
        preview_txt.configure(state="normal")
        preview_txt.delete("1.0", "end")
        preview_txt.insert("1.0", text)
        preview_txt.configure(state="disabled")

    def _set_rules_text(text: str):
        rules_txt.configure(state="normal")
        rules_txt.delete("1.0", "end")
        rules_txt.insert("1.0", text)
        rules_txt.configure(state="disabled")

    controller = _build_controller(
        bot,
        platform_var=platform_var,
        auto_trim_var=auto_trim_var,
        enforce_rules_var=enforce_rules_var,
        counter_var=counter_var,
        remaining_var=remaining_var,
        trimmed_var=trimmed_var,
        status_var=status_var,
        warnings_var=warnings_var,
        get_input=_get_input,
        set_preview=_set_preview,
        set_rules_text=_set_rules_text,
    )

    def clear_input():
        input_txt.delete("1.0", "end")
        controller["update_preview"]()

    def copy_to_clipboard():
        # CTk root still exposes standard Tk clipboard APIs
        controller["copy_to_clipboard"](root.clipboard_clear, root.clipboard_append, root.update)

    def simulate_post():
        controller["simulate_post"]()

    ctk.CTkButton(btns, text="Clear", command=clear_input, width=90).grid(row=0, column=0, padx=(0, 8))
    ctk.CTkButton(btns, text="Copy", command=copy_to_clipboard, width=90).grid(row=0, column=1, padx=(0, 8))
    ctk.CTkButton(btns, text="Simulate post", command=simulate_post, width=130).grid(row=0, column=2)

    # ---- Right pane
    hdr = ctk.CTkFrame(right, fg_color="transparent")
    hdr.grid(row=0, column=0, sticky="ew")
    hdr.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(hdr, text="Live Preview").grid(row=0, column=0, sticky="w")
    ctk.CTkLabel(hdr, textvariable=counter_var).grid(row=0, column=1, sticky="e")

    subhdr = ctk.CTkFrame(right, fg_color="transparent")
    subhdr.grid(row=1, column=0, sticky="ew", pady=(2, 8))
    subhdr.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(subhdr, textvariable=remaining_var).grid(row=0, column=0, sticky="w")
    ctk.CTkLabel(subhdr, textvariable=trimmed_var).grid(row=0, column=1, sticky="e")

    preview_txt = ctk.CTkTextbox(right, wrap="word", height=240)
    preview_txt.grid(row=3, column=0, sticky="nsew", pady=(0, 12))
    preview_txt.configure(state="disabled")

    rules_box = ctk.CTkFrame(right)
    rules_box.grid(row=4, column=0, sticky="ew")
    rules_box.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(rules_box, text="Platform rules (approx)").grid(row=0, column=0, sticky="w", padx=10, pady=(8, 0))
    rules_txt = ctk.CTkTextbox(rules_box, wrap="word", height=90)
    rules_txt.grid(row=1, column=0, sticky="ew", padx=10, pady=(6, 10))
    rules_txt.configure(state="disabled")

    ctk.CTkLabel(right, text="Warnings").grid(row=5, column=0, sticky="w")
    warnings_lbl = ctk.CTkLabel(right, textvariable=warnings_var, text_color="#b26a00", justify="left", wraplength=420)
    warnings_lbl.grid(row=6, column=0, sticky="ew", pady=(2, 8))

    ctk.CTkLabel(right, text="Status").grid(row=7, column=0, sticky="w")
    status_lbl = ctk.CTkLabel(right, textvariable=status_var, justify="left", wraplength=420)
    status_lbl.grid(row=8, column=0, sticky="ew", pady=(2, 0))

    input_txt.bind("<KeyRelease>", controller["update_preview"])
    platform_combo.bind("<<ComboboxSelected>>", controller["update_preview"])
    for var in (auto_trim_var, enforce_rules_var):
        var.trace_add("write", lambda *_: controller["update_preview"]())

    controller["update_preview"]()
    root.minsize(980, 620)
    root.mainloop()

# Example usage
if __name__ == "__main__":
    run_tk_app()