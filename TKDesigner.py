from tkinter import *
from tkinter.messagebox import showinfo

pale_blue = '#c4d9ed'
mid_pale_blue = '#c0d6ea'
darker_pale_blue = '#aaceef'

class ResizingCanvas(Canvas):
    def __init__(self, container, **settings):
        settings.setdefault('bg', 'white')
        settings.setdefault('bd', 0)
        settings.setdefault('highlightthickness', 0)
        super().__init__(container, **settings)

        self.bind('<Configure>', self.on_resize)

        self.width = self.winfo_reqwidth()
        self.height = self.winfo_reqheight()

    def on_resize(self, event):
        #Determine the ration of old width/height to new width/height
        wscale = float(event.width) / self.width
        hscale = float(event.height) / self.height

        self.width = event.width
        self.height = event.height
        self.config(width=self.width, height=self.height)
        #Scale all the items in the canvas
        self.scale('all', 0, 0, wscale, hscale)


class TKDesigner(Tk):

    @staticmethod
    def add_to_grid(widget, row, column, **settings):
        settings = TKDesigner.get_custom_settings(Grid, **settings)
        settings.setdefault('sticky', 'ew')
        settings.setdefault('ipadx', 10)
        settings.setdefault('ipady', 5)
        widget.grid(row=row, column=column, **settings)

    @staticmethod
    def clear_widget(widget):
        for child in widget.winfo_children():
            child.destroy()

    @staticmethod
    def settings(**settings):
        return settings

    @staticmethod
    def find_centre_of(a, b):
        return (a + b) / 2

    @staticmethod
    def get_bold_font(font):
        bold_font = font[0:2] + ('bold',)
        return bold_font

    @staticmethod
    def set_font_size(font, size):
        new_font = (font[0],) + (size,)
        if len(font) > 2: new_font += font[2:]
        return new_font

    @staticmethod
    def create_popup(message, window_name='Notice'):
        showinfo(window_name, message)

    @staticmethod
    def centre_window(window, centre_on=None):

        window.update()

        offsetx = 0
        offsety = 0
        parent_width = window.winfo_screenwidth()
        parent_height = window.winfo_screenheight()
        if centre_on is not None:
            centre_on.update()
            offsetx = centre_on.winfo_x()
            offsety = centre_on.winfo_y()
            parent_width = centre_on.winfo_width()
            parent_height = centre_on.winfo_height()

        width = window.winfo_width()
        height = window.winfo_height()
        x = (parent_width // 2) - (width // 2) + offsetx
        y = (parent_height // 2) - (height // 2) + offsety
        window.geometry(f'+{x}+{y}')

    @staticmethod
    def get_custom_settings(widget_type, **settings):
        custom_settings = []

        def padding():
            padding = settings['padding']
            settings['padx'] = padding
            settings['pady'] = padding
            del settings['padding']

        def cooldown():
            def cooldown_function(widget):
                def cooldown_delay(event=None):
                    if event is not None:
                        command(event)
                    else:
                        command()
                    try:
                        widget.config(state='disabled')
                        widget.after(delay * 1000, lambda: widget.config(state='active'))
                    except TclError:
                        pass
                        # If the button's been destroyed then this will raise an error

                if iscommand:
                    widget.config(command=cooldown_delay)
                else:
                    widget.bind(button, cooldown_delay)

            delay = settings['cooldown']
            iscommand = True
            if 'command' in settings:
                command = settings['command']
                del settings['command']

            elif 'bind' in settings:
                iscommand = False
                command = settings['bind']
                button = settings['button']
                del settings['bind']
                del settings['button']
            del settings['cooldown']
            return cooldown_function

        def bind():
            def bind_function(widget):
                widget.bind(button, command)

            command = settings['bind']
            button = settings['mouse']
            del settings['bind']
            del settings['mouse']
            return bind_function

        custom_setting_methods = {
            Button: {
                'padding': padding,
                'cooldown': cooldown,
                'bind': bind
            },
            Label: {
                'padding': padding
            },
            Grid: {
                'padding': padding
            }
        }

        #Determine what custom settings are in the settings
        for custom_setting in custom_setting_methods[widget_type].keys():
            if custom_setting in settings:
                method = custom_setting_methods[widget_type][custom_setting]()
                if method is not None:
                    custom_settings.append(method)

        if widget_type is Grid:
            return settings
        return custom_settings, settings

    @staticmethod
    def set_custom_settings(widget, custom_settings):
        for setting in custom_settings:
            setting(widget)

    def __init__(self):
        super().__init__()

        self._header_font = ('Helvetica', 12, 'bold')
        self._label_font = ('Helvetica', 10)
        self._background = 'white'
        self.set_background(self._background)

    def set_background(self, colour):
        self._background = colour
        self.configure(background=colour)

    def get_background_colour(self):
        return self._background

    def get_container(self, container):
        if container is None:
            return self
        else: return container

    def clear_ui(self):
        for child in self.winfo_children():
            if child is Toplevel:
                print("Toplevel child found")
            child.destroy()

    def set_header_font(self, font):
        if not isinstance(font, tuple):
            return
        self._header_font = font

    def set_label_font(self, font):
        if not isinstance(font, tuple):
            return
        self._label_font = font

    def create_label(self, text, container=None, **settings):
        container = self.get_container(container)
        custom_settings, settings = self.get_custom_settings(Label, **settings)
        settings = self.set_default_widget_settings(**settings)
        label = Label(container, text=str(text), **settings)
        self.set_custom_settings(label, custom_settings)
        return label

    def create_header(self, text, container=None, **settings):
        header = self.create_label(text, container, **settings)
        header.config(font=self._header_font)
        return header

    def create_button(self, text, container=None, **settings):
        container = self.get_container(container)
        custom_settings, settings = self.get_custom_settings(Button, **settings)
        settings = self.set_default_widget_settings(**settings)
        button = Button(container, text=text, **settings)
        self.set_custom_settings(button, custom_settings)
        return button

    def create_entry(self, container=None, **settings):
        container = self.get_container(container)
        settings = self.set_default_widget_settings(**settings)

        return Entry(container, settings)

    def set_default_widget_settings(self, **settings):
        settings.setdefault('bg', self._background)
        settings.setdefault('font', self._label_font)
        return settings

    def set_current_size_as_min(self):
        self.update()
        self.minsize(self.winfo_width(), self.winfo_height())

    def create_row_from_dict(self, dictionary, container, row, bg, label_method=None,
                             column_formatting=None, row_formatting=None):
        """
        Creates a row from a dictionary
        :param dictionary: The dictionary from which to create the row
        :param container: The container of the row
        :param row: The current row in the grid
        :param bg: The background colour of the row
        :param label_method: The method used to create the label
        :param column_formatting: A dictionary containing methods which return a formatted value
        :param row_formatting: A list containing methods which will output label formatting
        """
        label_method = self.create_label if label_method is None else label_method
        if column_formatting is None: column_formatting = {}
        if row_formatting is None: row_formatting = []

        label_settings = {}
        label_settings.setdefault('bg', bg)
        for row_formator in row_formatting:
            label_settings.update(row_formator(dictionary))

        headers = list(dictionary.keys())
        for i in range(len(headers)):
            header = headers[i]
            value = dictionary[header]
            if header in column_formatting:
                value = column_formatting[header](value)
            elif 'default' in column_formatting:
                value = column_formatting['default'](value)

            TKDesigner.add_to_grid(label_method(value, container=container, **label_settings), row, i)

    def create_row_from_list(self, row_list, container, row, bg, label_method=None, **column_formatting):
        """
        Creates a row from a list
        :param row_list: The list from which to create the row
        :param container: The container of the row
        :param row: The current row of the grid
        :param bg: The background colour of the row
        :param label_method: The method used to create the label
        :param column_formatting: A dictionary containing methods which return formatted values
                                  which are matched by a key, which corresponds to the list index.
        """
        label_method = self.create_label if label_method is None else label_method

        for i in range(len(row_list)):
            value = row_list[i]
            if str(i) in column_formatting:
                value = column_formatting[str(i)](value)
            elif 'default' in column_formatting:
                value = column_formatting['default'](value)

            TKDesigner.add_to_grid(label_method(value, container=container, bg=bg), row, i)

    def grid_from_list_of_dict(self, dictionary_list, container=None, bg1=None, bg2=pale_blue,
                               column_formatting=None, row_formatting=None):
        """
        Makes a grid from a list of dictionaries
        :param dictionary_list: The list of dictionaries from which to create the grid
        :param container: The container of the frame for which the grid will be contained
        :param bg1: Alternate row colour 1
        :param bg2: Alternate row colour 2
        :param column_formatting: A dictionary containing methods which return formatted values
        :param row_formatting: A list containing methods which will output label formatting
        :return: Frame containing the grid
        """

        container = self.get_container(container)
        bg1 = self._background if bg1 is None else bg1

        frame = Frame(container)
        headers = list(dictionary_list[0].keys())
        row = 0

        self.create_row_from_list(headers, container=frame, row=row, bg=bg1,
                                  label_method=self.create_header, default=lambda x: x.capitalize())
        self.set_column_weights(len(headers), container=frame)

        for dictionary in dictionary_list:
            row += 1
            bg = bg1 if row % 2 == 0 else bg2
            self.create_row_from_dict(dictionary, container=frame, row=row, bg=bg,
                                      column_formatting=column_formatting, row_formatting=row_formatting)
        return frame

    def grid_from_list(self, grid_list, item_to_list_converter, headers=None, container=None,
                       bg1=None, bg2=pale_blue, **column_formatting):
        """
        Makes a grid from a list of items
        :param grid_list: The list of items from which to create the grid
        :param item_to_list_converter: A method which converts the items in the list to an array of columns
        :param headers: The grid headers
        :param container: The container of the frame for which the grid will be contained
        :param bg1: Alternate row colour 1
        :param bg2: Alternate row colour 2
        :param column_formatting: A dictionary containing methods which return formatted values
        :return: Frame containing the grid
        """
        container = self.get_container(container)
        bg1 = self._background if bg1 is None else bg1

        frame = Frame(container)
        row = -1

        if headers is not None:
            row += 1
            self.create_row_from_list(headers, container=frame, row=row, bg=bg1,
                                      label_method=self.create_header)

        for item in grid_list:
            row += 1
            bg = bg1 if row % 2 == 0 else bg2
            row_list = item_to_list_converter(item)
            self.create_row_from_list(row_list, container=frame, row=row, bg=bg, **column_formatting)

        if len(grid_list) != 0:
            #Set the column weights in this grid using the first item in the gridlist
            self.set_column_weights(len(item_to_list_converter(grid_list[0])), container=frame)
        return frame

    def set_column_weights(self, num_columns, container=None, weights=1, **settings):
        container = self.get_container(container)

        for i in range(num_columns):
            weight = weights[i] if isinstance(weights, tuple) else weights
            container.columnconfigure(i, weight=weight, **settings)

    def create_button_entry_pair(self, button_settings, entry_settings, container=None):

        #TODO: Make a more flexible cooldown/custom parameters system.
        container = self.get_container(container)
        button_settings.setdefault('button', '<Button-1>')
        button = self.create_button(container=container, **button_settings)

        content = StringVar()
        button.content = content
        if 'text' in entry_settings:
            content.set(entry_settings['text'])
            del entry_settings['text']
        entry = self.create_entry(container, textvariable=content, **entry_settings)

        return button, entry

    def create_text(self, canvas, x, y, text, **settings):
        settings.setdefault('font', self._label_font)
        canvas.create_text(x, y, text=text, **settings)

    def create_single_row(self, *widgets_info, container=None, weights=1, **settings):
        """
        Creates a single row of widgets
        :param container: The container for this row
        :param widgets_info: A tuple containing a widget creation function and a dictionary of its parameters
        :param weights: The weighting for the columns
        :param settings: The grid settings
        :return: Frame containing the row
        """
        container = self.get_container(container)
        frame = Frame(container)

        for i in range(len(widgets_info)):
            widget_info = widgets_info[i]
            widget_creator = widget_info[0]
            widget_settings = widget_info[1]
            widget = widget_creator(container=frame, **widget_settings)
            self.add_to_grid(widget, row=0, column=i, **settings)

        self.set_column_weights(len(widgets_info), container=frame, weights=weights)
        return frame

    def create_vertical_space(self, height, container=None, **settings):
        container = self.get_container(container)
        frame = Frame(container, height=height, bg=self._background)
        settings.setdefault('fill', X)
        frame.pack(settings)

    def create_temporary_popup(self, message, window_name='Notice', time_to_close=1):
        popup = Toplevel(bg=self._background)
        popup.title(window_name)

        self.create_label(text=message, container=popup).pack(fill=X, padx=30, pady=5)
        self.centre_window(popup, centre_on=self)
        self.after(time_to_close * 1000, popup.destroy)

    def create_centred_popup(self, message, window_name='Notice', centre_on=None):
        popup = Toplevel(bg=self._background)
        popup.title(window_name)

        self.create_label(text=message, container=popup).pack(fill=X, padx=30, pady=5)
        self.centre_window(popup, centre_on=self if centre_on is None else centre_on)

