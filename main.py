#-*- coding: utf-8 -*-
import os
import csv
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.config import Config
from kivymd.app import MDApp
import shutil
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.textinput import TextInput
from kivy.utils import platform  # Import the platform module





class ImageButton(ButtonBehavior, Image):
    pass


class ClickableImageGridApp(MDApp):
    def __init__(self, **kwargs):
        super(ClickableImageGridApp, self).__init__(**kwargs)
        self.data_file = "csvdata.csv"  # CSV database file path
        # self.image_data = {}  # Dictionary to store image data (name and path)
        self.ids = []
        self.paths = []
        self.labels = []
        self.clicks_counts = []
        self.clicked_images = []



    def build(self):
        Window.maximize()
        folder_path = "img/"  # Replace with the path to your image folder
        self.title = 'Comunicator App'
        Config.set('kivy', 'window_icon', 'icon.png')

        if platform == 'android':
            from android.permissions import request_permissions, Permission

            # List the permissions you need
            permissions = [Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE]

            # Request permissions
            request_permissions(permissions)

        # Get a list of all image files in the folder
        image_files = [file for file in os.listdir(folder_path) if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

        # Load data from CSV database file (if it exists)
        self.load_data()

        # Create a RelativeLayout as the main layout
        main_layout = RelativeLayout()

        # Create a Widget for the red rectangle
        red_rectangle = Widget(size_hint=(1, None), height=200, pos = (0, Window.height - 210))  

        # Position the red rectangle at the top of the window
        red_rectangle.pos_hint = {'top': 1}

        with main_layout.canvas:
            #Color(1, 0, 1, 1)
            Color(243/255, 245/255, 220/255, 1)
            Rectangle(pos = (0, 0), size = (Window.width, Window.height))

        with red_rectangle.canvas:
            

            #Color(1, 0, 1, 1)
            Color(243/255, 245/255, 220/255, 1)  # Set color to red (R, G, B, A) ||  0.188235, 0.49019608, 0.6196078, 1
            self.rect = Rectangle(pos=red_rectangle.pos, size=red_rectangle.size)

            Color(243/255, 245/255, 220/255, 1)
            self.sep_line = Line(rectangle = (-20, Window.height - 210, Window.width+50, 210), width = 10)  

            #Color(1, 0, 1, 1)
            Color(115/255.0, 203/255.0, 182/255.0, 1)
            #self.line = Line(rectangle=(0, Window.height - 192, Window.width - 252, 185), width=3)
            line_canvas_width = Window.width - 210
            self.dis_rect = RoundedRectangle(pos = (0, Window.height - 260), size = (line_canvas_width, 240), radius = [(50.0, 50.0), (50.0, 50.0), (50.0, 50.0), (50.0, 50.0)])

            Clock.schedule_interval(self.update_rect_size, 0)
            Clock.schedule_interval(self.update_rect_pos, 0)


        # Create a GridLayout to hold the images
        self.grid_layout = GridLayout(cols=1, spacing=40, size_hint_y=None, size_hint_x = 0.96)
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))  # Make the GridLayout height dynamically adjust based on content


        for i in range(len(self.paths)):
            image = ImageButton(source="", size_hint=(None, None), size=(200, 200))
            image.source = self.paths[i]

            image_layout = GridLayout(cols=1, size_hint_y=None, height=230)
            image_layout.add_widget(image)

            label_background = RelativeLayout(size_hint=(None, None), size=(200, 50), pos=(image.x, image.y))
            with label_background.canvas:
                Color(115/255.0, 203/255.0, 182/255.0, 1)  # Set color to blue (R, G, B, A)
                Rectangle(pos=label_background.pos, size=label_background.size)

            label = Label(text=self.labels[i], font_hinting=None, font_size='22sp', color=(243/255, 245/255, 220/255, 1), size_hint_y=None, height=30, pos=(label_background.x, label_background.y + 10))

            label_background.add_widget(label)
            image_layout.add_widget(label_background)

            image.bind(on_release=self.on_image_click)
            self.grid_layout.add_widget(image_layout)




        
        
        self.grid_layout.bind(width=self.on_resize)
        self.schedule_sorting_and_updating()

        scroll_view_size_y = Window.height - 290
        # Create a ScrollView and add the GridLayout to it
        scroll_view = ScrollView(size_hint=(None, None),pos = (20, 0), size= (Window.width, scroll_view_size_y))  #  ||||| Subtract 200 for the height of the red rectangle
        scroll_view.add_widget(self.grid_layout)
        scroll_view.do_scroll_x = False


        # Add the red rectangle and the ScrollView to the main_layout
        main_layout.add_widget(red_rectangle)
        main_layout.add_widget(scroll_view)


        # Schedule the real-time updates of the columns
        self.grid_layout.bind(width=self.on_resize)
        print('build')


        self.clicked_image_layout = BoxLayout(size_hint = (None, None), size = (180, 180), pos = (35, Window.height - 255), spacing = 5)
        main_layout.add_widget(self.clicked_image_layout)

        delete_button = Button(text = 'Delete',font_size = 30,  size_hint = (None, None), size = (186, 180), pos = (Window.width - 200, Window.height - 200))
        delete_button.bind(on_release = self.delete_all_images)
        delete_button.background_normal = 'delete_icon.png'
        main_layout.add_widget(delete_button)


        settings_button = Button(size_hint = (None, None), size = (180, 50), pos = (Window.width - 200, Window.height - 260))
        settings_button.bind(on_release = self.show_settings_popup)
        settings_button.background_normal = 'settings_icon.png'
        main_layout.add_widget(settings_button)


        self.clicked_image_count = 0
        self.max_clicked_images = int(line_canvas_width/230)

        return main_layout
    
    def select_and_add_image(self, instance):
        file_chooser = FileChooserIconView()

        def on_selection(instance, selection):
            if selection:
                selected_image_path = selection[0]
            
                # Create a popup to display the selected image preview
                preview_popup = Popup(title="Selected Image Preview", size_hint=(None, None), size=(600, 600))
                preview_image = Image(source=selected_image_path)
                confirm_button = Button(text="Confirm", size_hint = (0.5, 1), size_hint_y = (0.2), pos_hint = {'center_x' : 0.5})

                def confirm_preview(instance):
                    # Close the preview popup and open the label input popup
                    preview_popup.dismiss()
                    label_popup.open()

                confirm_button.bind(on_release=confirm_preview)
                preview_layout = BoxLayout(orientation='vertical')
                preview_layout.add_widget(preview_image)
                preview_layout.add_widget(confirm_button)
                preview_popup.content = preview_layout

                # Create a popup to get the new label from the user
                label_popup = Popup(title="New Label", size_hint=(None, None), size=(300, 150))
                label_input = TextInput(hint_text="Enter new label", multiline=False)
                confirm_button = Button(text="Confirm")

                def confirm_label(instance):
                    new_label = label_input.text.strip()
                    if new_label:
                        new_image_path = os.path.join("img", os.path.basename(selected_image_path))
                        shutil.copy(selected_image_path, new_image_path)
                        self.add_image_to_csv(new_image_path, new_label)
                        label_popup.dismiss()

                confirm_button.bind(on_release=confirm_label)
                content_layout = BoxLayout(orientation='vertical')
                content_layout.add_widget(label_input)
                content_layout.add_widget(confirm_button)
                label_popup.content = content_layout

                # Open the preview popup
                preview_popup.open()

        file_chooser.bind(selection=on_selection)
        content = BoxLayout(orientation='vertical')
        content.add_widget(file_chooser)

        popup = Popup(title="Select Image", content=content, size_hint=(None, None), size=(600, 600))
        popup.open()

    def add_image_to_csv(self, image_path, label):
        new_id = max(self.ids) + 1 if self.ids else 1
        self.ids.insert(0, new_id)  # Insert at the beginning
        self.paths.insert(0, image_path)  # Insert at the beginning
        self.labels.insert(0, label)  # Insert at the beginning

        if self.clicks_counts:
            new_clicks_count = max(self.clicks_counts) + 1
        else:
            new_clicks_count = 1
        self.clicks_counts.insert(0, new_clicks_count)  # Insert at the beginning

        self.save_data()
        self.update_grid()


    def show_settings_popup(self, instance):
        content_layout = BoxLayout(orientation='vertical')
        add_image_button = Button(text='Add Image', size_hint=(None, None), size=(200, 50), pos_hint = {'center_x' : 0.5})
        add_image_button.bind(on_release=self.select_and_add_image)  # Bind to the new method
        content_layout.add_widget(add_image_button)

        popup = Popup(title='Settings', content=content_layout, size_hint=(None, None), size=(300, 150))
        popup.open()

    
    def schedule_sorting_and_updating(self, dt=60):  # Default to updating every 60 seconds (1 minute)
        Clock.schedule_interval(self.sort_and_update, dt)
        print("10s")

    def sort_and_update(self, dt):
        self.load_data()  # Load sorted data
        self.update_grid()  # Update the grid with the sorted data
        print("sorted and updated")

    def update_grid(self):
        self.grid_layout.clear_widgets()  # Clear the existing widgets
        for i in range(len(self.paths)):
            image = ImageButton(source="", size_hint=(None, None), size=(200, 200))
            image.source = self.paths[i]
            image_layout = GridLayout(cols=1, size_hint_y=None, height=230)
            image_layout.add_widget(image)
            label_background = RelativeLayout(size_hint=(None, None), size=(200, 50), pos=(image.x, image.y))
            with label_background.canvas:
                Color(115/255.0, 203/255.0, 182/255.0, 1)  # Set color to blue (R, G, B, A)
                Rectangle(pos=label_background.pos, size=label_background.size)
            label = Label(text=self.labels[i], font_hinting=None, font_size='22sp', color=(243/255, 245/255, 220/255, 1), size_hint_y=None, height=30, pos=(label_background.x, label_background.y + 10))            
            label_background.add_widget(label)
            image_layout.add_widget(label_background)
            image.bind(on_release=self.on_image_click)
            self.grid_layout.add_widget(image_layout)

       

    def on_resize(self, instance, width):
        cols = max(1, int(width / 200))  # 200 is the fixed image width
        self.grid_layout.cols = cols


    def update_rect_size(self, dt):
        """Update the size of the red rectangle as the window is resized."""
        self.rect.size = (Window.width, 200)


    def update_rect_pos(self, dt):
        """Update the size of the red rectangle as the window is resized."""
        self.rect.pos = (0, Window.height - 200)


    def on_window_size(self, instance, width, height):
        """Update the scroll view size when the window size changes."""
        self.scroll_view.size = (width, height - 200)  # Subtract 200 for the height of the red rectangle
        self.grid_layout.height = height - 200

    


    def delete_all_images(self, instance):
        self.clicked_image_layout.clear_widgets()
        self.clicked_image_count = 0
        for image in self.clicked_image_layout.children:
            image.bind(on_release = self.on_image_click)



    def img_display(self):
        print('Img displayed')


    def load_data(self):
        # Load data from the CSV database file, sort it by clicks_count, and populate the arrays
        self.ids = []
        self.paths = []
        self.labels = []
        self.clicks_counts = [] 
        if os.path.exists('csvdata.csv'):
            with open(self.data_file, 'r', newline='', encoding='utf8') as csvfile:
                reader = csv.DictReader(csvfile)
                sorted_data = sorted(reader, key=lambda row: int(row['clicks_count']), reverse=True)
                for row in sorted_data:
                    self.ids.append(int(row['id']))
                    self.paths.append(str(row['path']))
                    self.labels.append(str(row['label']))
                    self.clicks_counts.append(int(row['clicks_count']))
        print("loaded")

                


    def on_image_click(self, instance):
        if self.clicked_image_count < self.max_clicked_images:
            print("Image Clicked:", instance.source)
            clicked_index = self.paths.index(instance.source)  # Find the index of the clicked image in the paths list
            self.update_clicks_count(clicked_index)  # Update the clicks_count value for the clicked image
            clicked_image_widget = Image(source=instance.source, size_hint=(None, None), size=(230, 230))
            self.clicked_image_layout.add_widget(clicked_image_widget)
            self.clicked_image_count += 1
            if self.clicked_image_count == self.max_clicked_images:
                for image in self.clicked_image_layout.children:
                    image.unbind(on_release=self.on_image_click)



    def update_clicks_count(self, image_index):
        if 0 <= image_index < len(self.clicks_counts):
            self.clicks_counts[image_index] += 1
            self.save_data()  # Save data when updating clicks_count


    def save_data(self):
        with open(self.data_file, 'w', newline='', encoding='utf8') as csv_file:
            fieldnames = ['id', 'path', 'label', 'clicks_count']
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()
            for i in range(len(self.ids)):
                csv_writer.writerow({
                    'id': self.ids[i],
                    'path': self.paths[i],
                    'label': self.labels[i],
                    'clicks_count': self.clicks_counts[i]
                })

        

    def on_stop(self):
        # Save data to CSV database when the app is closed
        self.save_data()


    def on_request_permissions(self, permissions, results):
        if all(results):
            print("Permissions granted.")
            # Your app logic when permissions are granted
        else:
            print("Permissions denied.")
            # Your app logic when permissions are denied


if __name__ == "__main__":
    ClickableImageGridApp().run()