import badge

class App(badge.BaseApp):
    def on_open(self) -> None:
        me = badge.contacts.my_contact()
        if not me:
            badge.display.fill(1)
            badge.display.nice_text("No contact\ninfo. Please add\nyourself to\ncontacts.", 0, 0, font=32)
            badge.display.show()
            return
        self.logger.info(f"Rendering contact info for {me}")
        self.render_display(me)
    
    def render_display(self, contact) -> None:
        badge.display.fill(1)  # Clear the display
        
        # text rendering: decide on a font size and line breaks for the name
        # if the name has no spaces, go as low as font size 32 before inserting hyphens where needed
        # if the name has spaces, break at the middlemost space first, then the rest of the spaces, then insert hyphens as needed
        font, name = self.decide_name_size(contact.name)
        name_height = font.height * (name.count('\n') + 1)
        badge.display.nice_text(name, 0, 0, font=font, color=0, rot=0, x_spacing=0, y_spacing=0)
        badge.display.nice_text(f"{contact.pronouns}\n@{contact.handle}", 0, name_height, font=24, color=0, rot=0, x_spacing=0, y_spacing=0)
        badge.display.nice_text(f"0x{contact.badge_id:0>4x}", 200-badge.display.nice_fonts[24].max_width*6, name_height, font=24, color=0, rot=0, x_spacing=0, y_spacing=0)
        badge.display.show()
    
    def decide_name_size(self, name: str):
        """
        Decide the best size and line breaks for the name.
        Tries to use as large of a font as possible while not breaking the name in weird places (if possible).
        """
        font = None
        max_chars_for_sizes = {size: badge.display.width // font.max_width for size, font in badge.display.nice_fonts.items()}
        for size, max_chars in sorted(max_chars_for_sizes.items(), key=lambda x: x[0], reverse=True):
            if size < 24:
                # we don't want to use sizes smaller than 24 for names
                continue
            if len(name) <= max_chars:
                font = badge.display.nice_fonts[size]
                break
            elif ' ' in name:
                # If the name has spaces, break at the middlemost space first
                parts = name.split(' ')
                mid = len(parts) // 2
                test_name = ' '.join(parts[:mid]) + '\n' + ' '.join(parts[mid:])
                if max(len(part) for part in test_name.split('\n')) <= max_chars:
                    name = test_name
                    font = badge.display.nice_fonts[size]
                    break
                else:
                    # try breaking on all spaces
                    lines_available = 130 // size
                    if len(parts) > lines_available:
                        # this many lines will run the rest of the text off the screen
                        continue
                    if max(len(part) for part in parts) <= max_chars:
                        name = '\n'.join(parts)
                        font = badge.display.nice_fonts[size]
                        break
        if not font:
            # we have to hyphenate
            # we have 130 pixels, figure out how big the font can be while fitting the name
            for size, max_chars in sorted(max_chars_for_sizes.items(), key=lambda x: x[0], reverse=True):
                lines_available = 130 // size
                if len(name) // lines_available <= (max_chars - 1):
                    font = badge.display.nice_fonts[size]
                    name = '-\n'.join(name[i:i + max_chars - 1] for i in range(0, len(name), max_chars - 1))
                    break
        if not font:
            # just use the smallest font and cut off the rest
            font = badge.display.nice_fonts[18]
            name = '-\n'.join([name[i:i + 10] for i in range(0, len(name), 10)][:7])
        return font, name


    def loop(self) -> None:
        pass
