from IPython.display import display
from ipywidgets import widgets

button = widgets.Button(description="Click for answer")
output = widgets.Output()

display(button, output)

already_clicked = False

def on_button_clicked(b):
    global already_clicked, button
    if not already_clicked:
        already_clicked = True
        button.description = 'Answer:'
        with output:
            print('We added Salt & Pepper noise (minimum value – pepper – black pixels;'
                  ' maximum value – salt – white pixels.\n\n'
                  'The median filter will sort the elements within the mask'
                  ' and then return the center value of the sorted elements.\n\n'
                  'Therefore, by construction, it is unlikely that the median filter chooses a noisy pixel,\nas noisy pixels'
                  ' are likely at the very begin/end of the sorted elements; and not a center pixel.')

button.on_click(on_button_clicked)