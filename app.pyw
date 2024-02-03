import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class VirtualKeyboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notation Image Generator")

        # Set window icon
        icon_path = os.path.join(os.getcwd(), "icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        self.root.geometry("1056x505")  # Adjust the width as needed
        
        self.assets_types = [
            ("Default", "assets"),
            ("PlayStation", "assets_ps"),
            ("Xbox", "assets_xbox"),
        ]
        
        self.selected_images = []
        self.include_dark = tk.BooleanVar(value=False)

        # Initialize preview_frame
        self.preview_frame = tk.Frame(self.root)
        self.preview_frame.grid(row=6, column=0, columnspan=5, pady=5)

        self.images_folder_var = tk.StringVar(value="Default")
        self.images_folder_var.trace_add("write", self.load_and_reload_assets)

        # Get the selected assets folder
        # self.selected_assets = self.assets_mapping.get(self.images_folder_var.get(), "assets")
        self.selected_assets = self.assets_types[0][1]

        self.create_widgets()

    def create_widgets(self):
        # Selected Images Display
        self.image_frame = tk.Frame(self.root)
        self.image_frame.grid(row=0, column=0, columnspan=5, pady=10)

        # Load Images from the selected folder, group them by prefix, and sort within each group
        image_files = self.load_and_group_images()

        self.image_buttons = [[] for _ in range(5)]

        for group in image_files:
            for filename in group:
                if "_Dark" in filename:
                    continue  # Skip buttons with "_Dark" suffix

                # Fix the image_path for the default option
                image_path = os.path.join(self.selected_assets, filename)
                img = Image.open(image_path).resize((50, 50), Image.LANCZOS)  # Resize for display
                img_tk = ImageTk.PhotoImage(img)
                button = tk.Button(self.image_frame, image=img_tk, command=lambda i=image_path: self.toggle_image(i))
                button.image = img_tk

                # Determine the row based on the prefix
                row = min(int(filename.split('_')[0][1]), 5)  # Ensure row doesn't exceed 5
                self.image_buttons[row - 1].append(button)


        # Arrange buttons in separate rows
        for i, row_buttons in enumerate(self.image_buttons):
            for j, button in enumerate(row_buttons):
                button.grid(row=i, column=j, padx=5, pady=5)

        # Drop-down menu for selecting assets
        assets_menu_label = tk.Label(self.root, text="Select Assets:")
        assets_menu_label.grid(row=i + 1, column=3, pady=10, columnspan=1)
        assets_menu = tk.OptionMenu(self.root, self.images_folder_var, *[option[0] for option in self.assets_types])
        assets_menu.grid(row=i + 1, column=3, pady=10, columnspan=2)

        # Include Dark Checkbox
        include_dark_checkbox = tk.Checkbutton(self.root, text="Include dark notation", variable=self.include_dark)
        include_dark_checkbox.grid(row=i + 1, column=0, pady=10, columnspan=5)

        # Backspace Button
        backspace_button = tk.Button(self.root, text="Backspace", command=self.remove_last_image)
        backspace_button.grid(row=i + 1, column=0, pady=5, columnspan=1)

        # Clear Button
        clear_button = tk.Button(self.root, text="Clear", command=self.clear_selected_images)
        clear_button.grid(row=i + 1, column=0, pady=5, columnspan=2)

        # Export Button
        export_button = tk.Button(self.root, text="Save as PNG", command=self.export_images)
        export_button.grid(row=i + 2, column=0, pady=10, columnspan=5)

        # Preview Field
        self.preview_frame = tk.Frame(self.root)
        self.preview_frame.grid(row=i + 3, column=0, columnspan=5, pady=5)

    def load_and_reload_assets(self, *args):
        # Reload assets when the drop-down menu changes
        value_to_find = self.images_folder_var.get()  # Extract the string value
        index = next(i for i, option in enumerate(self.assets_types) if option[0] == value_to_find)  # Find the index
        new_asset_folder = self.assets_types[index][1]
        self.selected_assets = new_asset_folder
        
        self.create_widgets()
        self.load_and_group_images()
        self.update_selected_images_display()
        self.update_preview_field()

    def load_and_group_images(self, *args):
        # Get the selected assets folder
        # selected_assets = self.assets_mapping.get(self.images_folder_var.get(), "assets")

        # Load Images from the selected folder, group them by prefix, and sort within each group
        image_files = sorted(os.listdir(self.selected_assets))
        image_files = sorted(image_files, key=lambda x: (x.split('_')[0], x))

        grouped_images = [[] for _ in range(5)]

        for filename in image_files:
            if "_Dark" in filename:
                continue  # Skip buttons with "_Dark" suffix

            image_path = os.path.join(self.selected_assets, filename)
            # Determine the row based on the prefix
            row = min(int(filename.split('_')[0][1]), 5)  # Ensure row doesn't exceed 5
            grouped_images[row - 1].append(filename)

        self.update_preview_field(grouped_images)

        return grouped_images

    def toggle_image(self, image_path):
        # Allow the same image to be added to the list more than once
        self.selected_images.append(image_path)
        self.update_selected_images_display()

    def remove_last_image(self):
        # Remove the last image from the list
        if self.selected_images:
            self.selected_images.pop()
            self.update_selected_images_display()

    def clear_selected_images(self):
        # Clear the entire list of selected images
        self.selected_images = []
        self.update_selected_images_display()

    def update_selected_images_display(self):
        # Display the selected images
        for row_buttons in self.image_buttons:
            for button in row_buttons:
                button.config(state=tk.NORMAL)

        for i, image_path in enumerate(self.selected_images):
            img = Image.open(image_path).resize((50, 50), Image.LANCZOS)  # Resize for display
            img_tk = ImageTk.PhotoImage(img)

        # Update the preview field
        self.update_preview_field()

    def update_preview_field(self, grouped_images=None):
        # Destroy previous preview images
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        if grouped_images is None:
            # Load Images from the selected folder, group them by prefix, and sort within each group
            grouped_images = self.load_and_group_images()

        # Display the selected images in the preview field
        total_width = len(self.selected_images) * 50  # Original width without scaling
        max_width = 19 * 50  # Maximum width without scaling

        if total_width > max_width:
            # Scale down images dynamically
            scale_factor = max_width / total_width
            scaled_size = 50 * scale_factor

            for i, image_path in enumerate(self.selected_images):
                img = Image.open(image_path).resize((int(scaled_size), int(scaled_size)), Image.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                label = tk.Label(self.preview_frame, image=img_tk)
                label.image = img_tk
                label.grid(row=0, column=i, padx=0)
        else:
            # Display images without scaling
            for i, image_path in enumerate(self.selected_images):
                img = Image.open(image_path).resize((50, 50), Image.LANCZOS)  # Resize for display
                img_tk = ImageTk.PhotoImage(img)
                label = tk.Label(self.preview_frame, image=img_tk)
                label.image = img_tk
                label.grid(row=0, column=i, padx=0)

    def export_images(self):
        if not self.selected_images:
            messagebox.showinfo("Error", "Cannot save an empty notation.")
            return

        # Combine selected images into a single image (in a row) with a transparent background
        total_width = len(self.selected_images) * 80  # Use original width for exported image
        total_height = 80  # Use original height for exported image
        combined_image = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))  # Transparent background

        current_width = 0
        for image_path in self.selected_images:
            img = Image.open(image_path).resize((80, 80), Image.LANCZOS)  # Original size
            combined_image.paste(img, (current_width, 0), mask=img.convert('RGBA').split()[3])
            current_width += 80

        # Export normal image
        combined_image.save("exported_image.png")
        messagebox.showinfo("Save Successful", "Image file(s) created successfully.")

        # Export dark image if checkbox is checked
        if self.include_dark.get():
            dark_image = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))  # Transparent background
            current_width = 0

            for image_path in self.selected_images:
                dark_path = image_path.replace(".png", "_Dark.png")
                dark_img = Image.open(dark_path).resize((80, 80), Image.LANCZOS)  # Original size
                dark_image.paste(dark_img, (current_width, 0), mask=dark_img.convert('RGBA').split()[3])
                current_width += 80

            dark_image.save("exported_image_dark.png")
            # messagebox.showinfo("Exported", "Dark Images exported as PNG: exported_image_Dark.png")

if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualKeyboardApp(root)
    root.mainloop()
