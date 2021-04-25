from IPython.core.display import display
from skimage.data import shepp_logan_phantom
from skimage.util import random_noise
import numpy as np
import ipywidgets as widgets
from itkwidgets.widget_viewer import Viewer
import itk
from ipywidgets import interact, widgets

def get_shepp_logan_phantom():
    image = (shepp_logan_phantom()*255).astype(np.uint8)
    return image




def compare_3_images(image1, image2, image3,
                     link_cmap=False,
                     **viewer_kwargs):
    viewer1 = Viewer(image=image1, interpolation=False, annotations=False, ui_collapsed=True,
                     cmap='Grayscale', **viewer_kwargs)
    viewer2 = Viewer(image=image2, interpolation=False, annotations=False, ui_collapsed=True,
                     cmap='Grayscale', **viewer_kwargs)
    viewer3 = Viewer(image=image3, interpolation=False, annotations=False, ui_collapsed=True,
                     cmap='Grayscale', **viewer_kwargs)

    widgets.jslink((viewer1, 'mode'), (viewer2, 'mode'))
    widgets.jslink((viewer1, 'camera'), (viewer2, 'camera'))
    widgets.jslink((viewer1, 'roi'), (viewer2, 'roi'))
    widgets.jslink((viewer1, 'rotate'), (viewer2, 'rotate'))
    widgets.jslink((viewer1, 'annotations'), (viewer2, 'annotations'))

    widgets.jslink((viewer1, 'mode'), (viewer3, 'mode'))
    widgets.jslink((viewer1, 'camera'), (viewer3, 'camera'))
    widgets.jslink((viewer1, 'roi'), (viewer3, 'roi'))
    widgets.jslink((viewer1, 'rotate'), (viewer3, 'rotate'))
    widgets.jslink((viewer1, 'annotations'), (viewer3, 'annotations'))

    link_widgets = []
    link_widgets.append(widgets.Label('Link:'))

    class UpdateLink(object):
        def __init__(self, enable, name):
            self.link = None
            self.link2 = None
            self.name = name
            if enable:
                self.link = widgets.jslink((viewer1, name), (viewer2, name))
                self.link2 = widgets.jslink((viewer1, name), (viewer3, name))

        def __call__(self, change):
            if change.new:
                self.link = widgets.jslink((viewer1, self.name), (viewer2, self.name))
                self.link2 = widgets.jslink((viewer1, self.name), (viewer3, self.name))
            else:
                self.link.unlink()
                self.link2.unlink()

    update_cmap_link = UpdateLink(link_cmap, 'cmap')

    viewer1_textbox = widgets.Label('Raw Data')
    leftWidget = widgets.VBox([viewer1_textbox, viewer1])

    viewer2_textbox = widgets.Label('Filtered Data')
    centerWidget = widgets.VBox([viewer2_textbox, viewer2])

    viewer3_textbox = widgets.Label('Thresholded Data')
    rightWidget = widgets.VBox([viewer3_textbox, viewer3])


    widget = widgets.AppLayout(header=None,
                               left_sidebar=leftWidget,
                               center=centerWidget,
                               right_sidebar=rightWidget,
                               footer=None,
                               pane_widths=[1, 1, 1],
                               pane_heights=[1, 1, 1])
    return (widget, viewer1, viewer2, viewer3)





def corrup_salt_and_pepper(image):
	image = (255*random_noise(image, mode='s&p', amount=0.35)).astype(np.uint8)
	return image



phantom = get_shepp_logan_phantom()
noisy_phantom_salt_pepper = corrup_salt_and_pepper(phantom)
noisy_phantom_salt_pepper_itk = itk.GetImageFromArray(noisy_phantom_salt_pepper)


# initialize viewer
widget, viewer1, viewer2, viewer3 = compare_3_images(noisy_phantom_salt_pepper_itk,
                                                     noisy_phantom_salt_pepper_itk,
                                                     noisy_phantom_salt_pepper_itk)
display(widget)

# function that does the filtering
def filter_and_threshold(upper_threshold=255,
                         lower_threshold=128,
                         filter_selection='mean',
                         kernel_size=3):
    # upper threshold cant be higher than the lower threshold
    if upper_threshold < lower_threshold:
        upper_threshold = lower_threshold

    if filter_selection == 'Median Filter':
        viewer2.image = itk.median_image_filter(noisy_phantom_salt_pepper_itk, radius=kernel_size)
    elif filter_selection == 'Mean Filter':
        viewer2.image = itk.mean_image_filter(noisy_phantom_salt_pepper_itk, radius=kernel_size)
    elif filter_selection == 'None':
        viewer2.image = noisy_phantom_salt_pepper_itk
    else:
        raise ValueError('filter not implemented!')

    # thresholding using an itk filter
    viewer3.image = itk.binary_threshold_image_filter(viewer2.image,
                                                      lower_threshold=lower_threshold,
                                                      upper_threshold=upper_threshold)


# create UI
threshold_label = widgets.Label('Threshold Settings')
lower_threshold = widgets.IntSlider(description='Lower Threshold:', min=0, max=255, value=128)
upper_threshold = widgets.IntSlider(description='Upper Threshold:', min=0, max=255, value=255)

filter_selection = widgets.Dropdown(options=['Mean Filter', 'Median Filter', 'None'],
                                    description='Active Filter:',
                                    value='None')
kernel_size = widgets.IntSlider(description='Box Size:', min=3, max=10)

threshold_box = widgets.VBox([threshold_label, lower_threshold, upper_threshold])
filter_box = widgets.VBox([filter_selection, kernel_size])

ui = widgets.HBox([filter_box, threshold_box])

widgets.interactive_output(filter_and_threshold,
                           {'lower_threshold': lower_threshold,
                            'upper_threshold': upper_threshold,
                            'filter_selection': filter_selection,
                            'kernel_size': kernel_size})

display(ui)