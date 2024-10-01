import tkinter as tk 
from PIL import Image, ImageTk
import os
import random
import threading

from tarot_deck import tarot_deck

# Try to import OpenAI and set the API key if available
try:
    import openai
    # Set your OpenAI API key
    openai.api_key = 'INPUT YOUR OPEN API KEY HERE' ### ######### #####     Here is where you paste your own OpenAI API Key within the apostrophes
    openai_available = True
except ImportError:
    openai_available = False

def generate_tarot_reading(cards):
    # Check if OpenAI is available and the API key is set
    if not openai_available or not openai.api_key or openai.api_key.strip() == '' or openai.api_key == 'INPUT YOUR OPEN API KEY HERE':
        return None  # No reading generated

    card_names = [card['name'] for card in cards]
    prompt = f"Without acknowledging this prompt (like without saying Certainly or Yes), Provide a tarot reading of the following cards with an overall of what all the cards mean together as a reading. If there is only one card, do not do a reading as a whole and only do a reading of the single card. If there are 10 cards, then it is a Celtic Cross reading which is set up like this: Card 1 is the Present Situation. Card 2 is Influences or Challenges. Card 3 is the Distant Past. Card 4 is the Recent Past. Card 5 is the Best possible outcome. Card 6 is the Immediate Future. Card 7 is Advice. Card 8 is The Current Environment. Card 9 is Hopes or Fears. Card 10 is the Potential Outcome. : {', '.join(card_names)}."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",  ####   Here you can adjust the OpenAI model
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=1000,  # Adjust as needed
            temperature=0.7  # Adjust for creativity
        )
        reading = response.choices[0].message.content.strip()
        return reading
    except Exception as e:
        # Do not return error messages
        return None

def draw_cards(num_cards):
    deck = tarot_deck.copy()
    random.SystemRandom().shuffle(deck)
    return deck[:num_cards]

def draw_celtic_cross(canvas_frame, text_box):
    for widget in canvas_frame.winfo_children():
        widget.destroy()
    cards = draw_cards(10)
    images = []
    for i, card in enumerate(cards):
        image_path = os.path.join(os.path.dirname(__file__), card['image'])
        pil_image = Image.open(image_path)
        if i == 1:
            pil_image = pil_image.rotate(90, expand=True)
        images.append(pil_image)
    canvas = tk.Canvas(canvas_frame)
    canvas.pack(fill="both", expand=True)
    canvas.images = images
    canvas.bind("<Configure>", lambda event: redraw_celtic_cross(canvas, images))
    redraw_celtic_cross(canvas, images)
    positional_names = [
        "Present Situation (1)",
        "Influences or Challenges (2)",
        "Distant Past (3)",
        "Recent Past (4)",
        "Best Outcome (5)",
        "Immediate Future (6)",
        "Advice (7)",
        "Environment (8)",
        "Hopes or Fears (9)",
        "Potential Outcome (10)"
    ]
    card_meanings = "\n".join([f"{positional_names[i]}:\n{cards[i]['name']} - {cards[i]['meaning']}\n" for i in range(10)])
    text_box.config(state="normal")
    text_box.delete("1.0", tk.END)
    text_box.insert("1.0", card_meanings)
    text_box.config(state="disabled")

    # Generate and display the tarot reading in a separate thread
    def update_reading():
        reading = generate_tarot_reading(cards)
        if reading:
            text_box.config(state="normal")
            text_box.insert(tk.END, f"\nTarot Reading:\n{reading}")
            text_box.config(state="disabled")

    threading.Thread(target=update_reading).start()

def redraw_celtic_cross(canvas, images):
    canvas.delete("all")
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    if canvas_width <= 0 or canvas_height <= 0:
        return
    card_original_width = images[0].width
    card_original_height = images[0].height
    spacing = 20
    horizontal_spacing = 125
    vertical_spacing_7_10 = -24
    extra_horizontal_spacing_4_6 = 60
    extra_horizontal_offset_7_10 = 30
    padding_left = 55
    padding_right = 35

    total_width = (
        4 * card_original_width
        + 3 * horizontal_spacing
        + 3 * extra_horizontal_spacing_4_6
        + extra_horizontal_offset_7_10
        + padding_left
        + padding_right
    )
    total_height = card_original_height * 4 + (-24 * 3)
    scaling_x = canvas_width / total_width
    scaling_y = canvas_height / total_height
    scaling = min(scaling_x, scaling_y, 1)
    spacing *= scaling
    horizontal_spacing *= scaling
    vertical_spacing_7_10 *= scaling
    extra_horizontal_spacing_4_6 *= scaling
    extra_horizontal_offset_7_10 *= scaling
    padding_left *= scaling
    padding_right *= scaling
    resized_images = []
    for i, pil_image in enumerate(images):
        img = pil_image.copy()
        new_width = max(int(img.width * scaling), 1)
        new_height = max(int(img.height * scaling), 1)
        img = img.resize((new_width, new_height), Image.LANCZOS)
        resized_image = ImageTk.PhotoImage(img)
        resized_images.append(resized_image)
    card_width = resized_images[0].width()
    card_height = resized_images[0].height()
    total_width = (
        4 * card_width
        + 3 * horizontal_spacing
        + 3 * extra_horizontal_spacing_4_6
        + extra_horizontal_offset_7_10
        + padding_left
        + padding_right
    )
    leftmost_x = (canvas_width - total_width) / 2 + padding_left
    center_x = leftmost_x + card_width + horizontal_spacing + extra_horizontal_spacing_4_6
    center_y = canvas_height / 2 - card_height / 2
    positions = [
        (center_x, center_y),
        (
            center_x + (card_width - resized_images[1].width()) / 2,
            center_y + (card_height - resized_images[1].height()) / 2,
        ),
        (center_x, center_y + card_height + spacing),
        (
            center_x - card_width - horizontal_spacing - extra_horizontal_spacing_4_6,
            center_y,
        ),
        (center_x, center_y - card_height - spacing),
        (
            center_x + card_width + horizontal_spacing + extra_horizontal_spacing_4_6,
            center_y,
        ),
    ]
    x_offset = (
        center_x
        + 2 * (card_width + horizontal_spacing)
        + extra_horizontal_offset_7_10
        + 2 * extra_horizontal_spacing_4_6
    )
    y_offset = center_y + 1.5 * (card_height + vertical_spacing_7_10)
    for i in range(6, 10):
        positions.append(
            (x_offset, y_offset - (card_height + vertical_spacing_7_10) * (i - 6))
        )
    for i, (x, y) in enumerate(positions):
        canvas.create_image(x, y, image=resized_images[i], anchor='nw')
    canvas.images = resized_images

def draw_one_card(canvas_frame, text_box):
    for widget in canvas_frame.winfo_children():
        widget.destroy()
    cards = draw_cards(1)
    images = []
    card = cards[0]
    image_path = os.path.join(os.path.dirname(__file__), card['image'])
    pil_image = Image.open(image_path)
    images.append(pil_image)
    canvas = tk.Canvas(canvas_frame)
    canvas.pack(fill="both", expand=True)
    canvas.images = images
    canvas.bind("<Configure>", lambda event: redraw_one_card(canvas, images))
    redraw_one_card(canvas, images)
    positional_names = ["Card: "]
    card_meanings = f"{positional_names[0]}{cards[0]['name']}\n{cards[0]['meaning']}\n"
    text_box.config(state="normal")
    text_box.delete("1.0", tk.END)
    text_box.insert("1.0", card_meanings)
    text_box.config(state="disabled")

    # Generate and display the tarot reading in a separate thread
    def update_reading():
        reading = generate_tarot_reading(cards)
        if reading:
            text_box.config(state="normal")
            text_box.insert(tk.END, f"\nTarot Reading:\n{reading}")
            text_box.config(state="disabled")

    threading.Thread(target=update_reading).start()

def redraw_one_card(canvas, images):
    canvas.delete("all")
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    if canvas_width <= 0 or canvas_height <= 0:
        return
    padding_left = 32
    padding_right = 22
    available_width = canvas_width - padding_left - padding_right
    img = images[0]
    scaling = min(
        available_width / img.width,
        canvas_height / img.height,
        1
    )
    if scaling <= 0:
        scaling = 1
    new_width = max(int(img.width * scaling), 1)
    new_height = max(int(img.height * scaling), 1)
    img_resized = img.resize((new_width, new_height), Image.LANCZOS)
    resized_image = ImageTk.PhotoImage(img_resized)
    image_x = padding_left + (available_width - resized_image.width()) // 2
    image_y = (canvas_height - resized_image.height()) // 2
    canvas.create_image(image_x, image_y, image=resized_image, anchor='nw')
    canvas.images = [resized_image]

def draw_three_cards(canvas_frame, text_box):
    for widget in canvas_frame.winfo_children():
        widget.destroy()
    cards = draw_cards(3)
    images = []
    for card in cards:
        image_path = os.path.join(os.path.dirname(__file__), card['image'])
        pil_image = Image.open(image_path)
        images.append(pil_image)
    canvas = tk.Canvas(canvas_frame)
    canvas.pack(fill="both", expand=True)
    canvas.images = images
    canvas.bind("<Configure>", lambda event: redraw_three_cards(canvas, images))
    redraw_three_cards(canvas, images)
    positional_names = [
        "Card 1: ",
        "Card 2: ",
        "Card 3: "
    ]
    card_meanings = "\n".join([f"{positional_names[i]}{cards[i]['name']}\n{cards[i]['meaning']}\n" for i in range(3)])
    text_box.config(state="normal")
    text_box.delete("1.0", tk.END)
    text_box.insert("1.0", card_meanings)
    text_box.config(state="disabled")

    # Generate and display the tarot reading in a separate thread
    def update_reading():
        reading = generate_tarot_reading(cards)
        if reading:
            text_box.config(state="normal")
            text_box.insert(tk.END, f"\nTarot Reading:\n{reading}")
            text_box.config(state="disabled")

    threading.Thread(target=update_reading).start()

def redraw_three_cards(canvas, images):
    canvas.delete("all")
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    if canvas_width <= 0 or canvas_height <= 0:
        return
    img_width = images[0].width
    img_height = images[0].height
    spacing = 25
    padding_left = 32
    padding_right = 22
    total_width = padding_left + img_width * 3 + spacing * 2 + padding_right
    scaling = min(
        canvas_width / total_width,
        canvas_height / img_height
    )
    scaling = min(scaling, 1)
    if scaling <= 0:
        scaling = 1
    horizontal_spacing = spacing * scaling
    padding_left_scaled = padding_left * scaling
    padding_right_scaled = padding_right * scaling
    resized_images = []
    for img in images:
        new_width = max(int(img.width * scaling), 1)
        new_height = max(int(img.height * scaling), 1)
        img_resized = img.resize((new_width, new_height), Image.LANCZOS)
        resized_image = ImageTk.PhotoImage(img_resized)
        resized_images.append(resized_image)
    card_width = resized_images[0].width()
    card_height = resized_images[0].height()
    total_width = padding_left_scaled + card_width * 3 + horizontal_spacing * 2 + padding_right_scaled
    start_x = (canvas_width - total_width) // 2 + padding_left_scaled
    center_y = canvas_height // 2 - card_height // 2
    positions = [
        (start_x, center_y),
        (start_x + card_width + horizontal_spacing, center_y),
        (start_x + 2 * (card_width + horizontal_spacing), center_y)
    ]
    for i, (x, y) in enumerate(positions):
        canvas.create_image(x, y, image=resized_images[i], anchor='nw')
    canvas.images = resized_images

def setup_main_gui(root, spread_type=None):
    sample_card_path = os.path.join(os.path.dirname(__file__), tarot_deck[0]['image'])
    sample_card_image = Image.open(sample_card_path)
    card_width, card_height = sample_card_image.size
    spacing = 25
    padding_left = 30
    padding_right = 30
    total_width = padding_left + card_width * 3 + spacing * 2 + padding_right
    window_width = total_width + 280
    window_height = card_height + 175
    root.geometry(f"{int(window_width)}x{int(window_height)}")
    root.resizable(True, True)
    content_frame = tk.Frame(root)
    content_frame.pack(fill="both", expand=True)
    content_frame.grid_rowconfigure(0, weight=1)
    content_frame.grid_columnconfigure(0, weight=3)
    content_frame.grid_columnconfigure(1, weight=1)
    canvas_frame = tk.Frame(content_frame)
    canvas_frame.grid(row=0, column=0, sticky="nsew")
    right_frame = tk.Frame(content_frame, width=245)
    right_frame.grid(row=0, column=1, sticky="nsew")
    right_frame.grid_propagate(False)
    right_frame.grid_rowconfigure(0, weight=1)
    right_frame.grid_columnconfigure(0, weight=1)
    text_frame = tk.Frame(right_frame)
    text_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    text_frame.grid_rowconfigure(0, weight=1)
    text_frame.grid_columnconfigure(0, weight=1)
    text_box = tk.Text(text_frame, wrap="word", font=("Courier New", 10), width=37)
    text_box.grid(row=0, column=0, sticky="nsew")
    scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_box.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    text_box.config(yscrollcommand=scrollbar.set)
    text_box.config(state="normal")
    buttons_frame = tk.Frame(right_frame)
    buttons_frame.grid(row=1, column=0, padx=5, pady=(5, 10), sticky="n")
    draw_one_card_button = tk.Button(
        buttons_frame,
        text="Draw One Card",
        width=20,
        command=lambda: draw_one_card(canvas_frame, text_box)
    )
    draw_one_card_button.pack(pady=5)
    draw_three_cards_button = tk.Button(
        buttons_frame,
        text="Draw Three Cards",
        width=20,
        command=lambda: draw_three_cards(canvas_frame, text_box)
    )
    draw_three_cards_button.pack(pady=5)
    draw_celtic_button = tk.Button(
        buttons_frame,
        text="Draw Celtic Cross",
        width=20,
        command=lambda: draw_celtic_cross(canvas_frame, text_box)
    )
    draw_celtic_button.pack(pady=5)
    if spread_type is None:
        add_placeholder(canvas_frame)
    else:
        if spread_type == "celtic":
            draw_celtic_cross(canvas_frame, text_box)
        elif spread_type == "one":
            draw_one_card(canvas_frame, text_box)
        elif spread_type == "three":
            draw_three_cards(canvas_frame, text_box)

def add_placeholder(canvas_frame):
    try:
        for widget in canvas_frame.winfo_children():
            widget.destroy()
        image_path = os.path.join(os.path.dirname(__file__), "back.gif")
        pil_image = Image.open(image_path)
        canvas = tk.Canvas(canvas_frame)
        canvas.pack(fill="both", expand=True)
        canvas.placeholder_image = pil_image
        canvas.bind("<Configure>", lambda event: redraw_placeholder(canvas, pil_image))
        redraw_placeholder(canvas, pil_image)
    except Exception as e:
        print(f"Error loading placeholder image: {e}")

def redraw_placeholder(canvas, pil_image):
    canvas.delete("all")
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    if canvas_width <= 0 or canvas_height <= 0:
        return
    padding_left = 32
    padding_right = 22
    available_width = canvas_width - padding_left - padding_right
    scaling = min(
        available_width / pil_image.width,
        canvas_height / pil_image.height,
        1
    )
    if scaling <= 0:
        scaling = 1
    new_width = max(int(pil_image.width * scaling), 1)
    new_height = max(int(pil_image.height * scaling), 1)
    img = pil_image.resize((new_width, new_height), Image.LANCZOS)
    resized_image = ImageTk.PhotoImage(img)
    image_x = padding_left + (available_width - resized_image.width()) // 2
    image_y = (canvas_height - resized_image.height()) // 2
    canvas.create_image(image_x, image_y, image=resized_image, anchor='nw')
    canvas.placeholder_image = resized_image

def main():
    root = tk.Tk()
    root.title("Tarot Cards")
    root.resizable(True, True)
    setup_main_gui(root, spread_type=None)
    root.mainloop()

if __name__ == "__main__":
    main()