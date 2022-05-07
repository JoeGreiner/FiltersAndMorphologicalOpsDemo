from IPython.core.display import display
from matplotlib import pyplot as plt
from skimage.data import shepp_logan_phantom
from skimage.util import random_noise
import numpy as np
import ipywidgets as widgets
from ipywidgets import  widgets

from skimage.morphology import square, disk, star, diamond
from skimage.filters.rank import mean, median

# ideas:   change image,
#           change noise
#           more filters
#           show math as with convolutions

class RankFilterWidget():
    def __init__(self):

        plt.close("all")

        self.phantom = (shepp_logan_phantom()*255).astype(np.uint8)
        self.noisy_phantom = self.corrupt(self.phantom)

        self.filtered_image = self.noisy_phantom.copy()
        self.thresholded_image = np.zeros_like(self.noisy_phantom, dtype=bool)

        self.footprint = np.zeros(shape=(3,3))

        self.figure = plt.figure(figsize=(9, 5), constrained_layout=True)
        self.axes = self.figure.subplot_mosaic(
            """
            ....d....
            AAABBBCCC
            AAABBBCCC
            AAABBBCCC
            """
        )

        self.ax_left = self.axes['A']
        self.ax_middle = self.axes['B']
        self.ax_right = self.axes['C']
        self.ax_footprint = self.axes['d']

        plt.sca(self.ax_footprint)
        self.footprint_img_obj = plt.imshow(self.footprint, cmap='gray', vmin=0, vmax=1, interpolation='none')
        plt.title('Neighborhood')

        plt.sca(self.ax_left)
        self.input_img_obj = plt.imshow(self.noisy_phantom, cmap='gray', interpolation='None')
        self.ax_left.xaxis.set_visible(False)
        self.ax_left.yaxis.set_visible(False)
        plt.title('Noisy Image')

        plt.sca(self.ax_middle)
        self.filtered_img_obj =plt.imshow(self.filtered_image, cmap='gray', interpolation='None')
        self.ax_middle.xaxis.set_visible(False)
        self.ax_middle.yaxis.set_visible(False)
        self.ax_middle.sharex(self.ax_left)
        self.ax_middle.sharey(self.ax_left)
        plt.title('Filtered Image')


        plt.sca(self.ax_right)
        self.threshold_img_obj = plt.imshow(self.thresholded_image, cmap='gray', vmin=0, vmax=1, interpolation='None')
        self.ax_right.xaxis.set_visible(False)
        self.ax_right.yaxis.set_visible(False)
        self.ax_right.sharex(self.ax_left)
        self.ax_right.sharey(self.ax_left)
        plt.title('Thresholded Image')



        plt.show()


        # create UI
        threshold_label = widgets.Label('Threshold Settings')
        lower_threshold = widgets.IntSlider(description='Lower Threshold:', min=0, max=255, value=128,
                                            width='auto',
                                            style= {'description_width': 'initial'})
        upper_threshold = widgets.IntSlider(description='Upper Threshold:', min=0, max=255, value=255,
                                            width='auto',
                                            style= {'description_width': 'initial'})

        filter_selection = widgets.Dropdown(options=['Mean', 'Median', 'None'],
                                            description='Filter:',
                                            value='None')

        self.neighborhood_selection = widgets.Dropdown(options=['square', 'disk', 'star', 'diamond'],
                                            description='Neighborhood Shape:',
                                            value='disk')

        self.neighborhood_size = widgets.IntSlider(description='Neighborhood Size:', min=3, max=25, step=2,
                                                   style= {'description_width': 'initial'})

        threshold_box = widgets.VBox([threshold_label, lower_threshold, upper_threshold])
        filter_box = widgets.VBox([filter_selection, self.neighborhood_selection, self.neighborhood_size])

        ui = widgets.HBox([filter_box, threshold_box])

        widgets.interactive_output(self.filter_and_threshold,
                                   {'lower_threshold': lower_threshold,
                                    'upper_threshold': upper_threshold,
                                    'neighborhood_selection': self.neighborhood_selection,
                                    'filter_selection': filter_selection,
                                    'neighborhood_size': self.neighborhood_size})

        display(ui)




    def corrupt(self, image, mode='s&p', noise_amount=0.35):
        image = (255*random_noise(image, mode=mode, amount=noise_amount)).astype(np.uint8)
        return image


    def filter_and_threshold(self,
                             upper_threshold=255,
                             lower_threshold=128,
                             neighborhood_selection='disk',
                             filter_selection='Mean Filter',
                             neighborhood_size=3):

        # upper threshold cant be higher than the lower threshold
        if upper_threshold < lower_threshold:
            upper_threshold = lower_threshold

        if neighborhood_selection == 'disk':
            self.footprint = disk((neighborhood_size-1)//2)
        elif neighborhood_selection == 'square':
            self.footprint = square(neighborhood_size)
        elif neighborhood_selection == 'star':
            self.footprint = star(neighborhood_size)
        elif neighborhood_selection == 'diamond':
            self.footprint = diamond((neighborhood_size-1)//2)

        if filter_selection == 'Median':
            self.filtered_image = median(self.noisy_phantom, footprint=self.footprint)
        elif filter_selection == 'Mean':
            self.filtered_image = mean(self.noisy_phantom, footprint=self.footprint)
        elif filter_selection == 'None':
            self.filtered_image = self.noisy_phantom.copy()
        else:
            raise ValueError('filter not implemented!')

        # thresholding using an itk filter
        self.thresholded_image = (self.filtered_image >= lower_threshold) & (self.filtered_image <= upper_threshold)

        self.update()

    def update(self):
        self.input_img_obj.set_data(self.noisy_phantom)
        self.filtered_img_obj.set_data(self.filtered_image)
        self.threshold_img_obj.set_data(self.thresholded_image)
        self.footprint_img_obj.set_data(self.footprint)

        xlim = self.ax_footprint.get_xlim()
        ylim = self.ax_footprint.get_ylim()
        self.ax_footprint.set_xticks(xlim)
        self.ax_footprint.set_yticks(ylim)

        self.ax_footprint.set_xticklabels([0, self.neighborhood_size.value])
        self.ax_footprint.set_yticklabels([0, self.neighborhood_size.value])

        self.figure.canvas.draw_idle()

