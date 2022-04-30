import copy

import numpy as np
from imageio import imread
from ipywidgets import widgets, Checkbox
import matplotlib.pyplot as plt
from skimage import data
from skimage.color import rgb2gray


class LUT_2D_Widget():
    def __init__(self, indicator_scale_length = 15):
        # close all old figures
        plt.close("all")
        self.indicator_scale_length = indicator_scale_length

        self.over_color = [255/255, 20/255, 147/255]
        self.under_color = [255/255,255/255,0/255]

        self.axes = plt.figure(figsize=(9, 6), constrained_layout=True).subplot_mosaic(
            """
            AAAAAAA
            CCCBBBB
            CCCBBBB
            CCCBBBB
            """
        )

        self.ax_top = self.axes['A']
        self.ax_bottom_right = self.axes['B']
        self.ax_bottom_left = self.axes['C']

        plt.sca(self.ax_top)
        self.indicator_scale = np.zeros(shape=(1, self.indicator_scale_length), dtype=np.uint8)
        self.indicator_scale[0, :] = np.linspace(0, 255, self.indicator_scale_length)
        self.indicator_image_obj = plt.imshow(self.indicator_scale, interpolation='none')
        self.ax_top.xaxis.set_visible(False)
        self.ax_top.yaxis.set_visible(False)
        plt.title('LUT Indicator')

        plt.sca(self.ax_bottom_right)
        self.image = data.cat()[:, :, 0]
        self.image_obj = plt.imshow(self.image, vmin=0, vmax=255)
        self.colorbar = plt.colorbar(extend='both')
        self.ax_bottom_right.xaxis.set_visible(False)
        self.ax_bottom_right.yaxis.set_visible(False)
        plt.title('Image With Applied LUT')

        plt.sca(self.ax_bottom_left)
        plt.hist(self.image.flatten(), bins=range(0, 255 + 1, 1), color='gray')
        self.minimum_line = plt.axvline(0, color='r')
        self.maximum_line = plt.axvline(255, color='r')
        self.under_span = plt.axvspan(0, 0, facecolor=self.under_color)
        self.over_span = plt.axvspan(255, 255, facecolor=self.over_color)
        self.over_span.set_visible(False)
        self.under_span.set_visible(False)
        plt.title('Data Histogram')
        plt.xlabel('Data Values')
        plt.ylabel('Count')

        self.indicator_text = self.create_text_annotation(self.indicator_scale, axes=self.ax_top)

        self.min_slider = widgets.IntSlider(description='Minimum:', min=0, max=254, value=0)
        self.max_slider = widgets.IntSlider(description='Maximum:', min=1, max=255, value=255)
        self.min_slider.observe(handler=self.change_image_clim_prio_min)
        self.max_slider.observe(handler=self.change_image_clim_prio_max)

        self.show_over_under = Checkbox(False, description='Show clipped/saturated pixels:')
        self.show_over_under.observe(handler=self.change_over_under, names='value')

        data_selection_options = ['cat', 'WGA', 'DAPI']
        default_value_img = 'cat'

        self.image_selection_dropdown = widgets.Dropdown(options=data_selection_options,
                                                         description='Image Data:',
                                                         value=default_value_img)

        self.image_selection_dropdown.observe(self.create_image_data, names='value')


        LUT_selection_options = sorted(['viridis', 'inferno', 'binary', 'gray', 'hot'])
        default_LUT_value = 'gray'
        self.lut_dropdown = widgets.Dropdown(options=LUT_selection_options,
                                             description='LUT:',
                                             value=default_LUT_value)
        self.lut_dropdown.observe(handler=self.change_cmap, names='value')
        self.change_cmap({'new':default_LUT_value})



        self.vbox = widgets.VBox((self.image_selection_dropdown, self.lut_dropdown,
                                  self.min_slider, self.max_slider,
                                  self.show_over_under))

        display(self.vbox)

    def create_image_data(self, change):
        if change['new'] == 'cat':
            self.image = (255*rgb2gray(data.cat())).astype(np.uint8)
        elif change['new'] == 'WGA':
            self.image = imread(uri='images/wga_cm.tif')
        elif change['new'] == 'DAPI':
            self.image = imread(uri='images/dapi.tif')

        self.ax_bottom_right.clear()
        self.image_obj = self.ax_bottom_right.imshow(self.image,
                                                     cmap=self.colormap,
                                                     vmin=self.min_slider.value,
                                                     vmax=self.max_slider.value)
        self.colorbar.remove()
        plt.sca(self.ax_bottom_right)
        self.colorbar = plt.colorbar(extend='both')
        plt.title('Image With Applied LUT')

        self.ax_bottom_left.clear()
        plt.sca(self.ax_bottom_left)
        plt.hist(self.image.flatten(), bins=range(0, 255 + 1, 1), color='gray')
        self.minimum_line = plt.axvline(self.min_slider.value, color='r')
        self.maximum_line = plt.axvline(self.max_slider.value, color='r')
        plt.title('Data Histogram')
        plt.xlabel('Data Values')
        plt.ylabel('Count')
        self.change_over_under()

    def change_over_under(self, change=None):
        self.colormap = copy.copy(plt.get_cmap(self.colormap_string))
        if self.show_over_under.value:
            self.colormap.set_under(self.under_color)
            self.colormap.set_over(self.over_color)
            self.over_span.set_visible(True)
            self.under_span.set_visible(True)
            self.update_span_max()
            self.update_span_min()
        else:
            self.over_span.set_visible(False)
            self.under_span.set_visible(False)
        self.update_cmap()


    def change_cmap(self, change=None):
        self.colormap_string = change['new']
        self.colormap = copy.copy(plt.get_cmap(self.colormap_string))
        self.change_over_under()
        self.update_cmap()

    def update_cmap(self):
        self.image_obj.set_cmap(self.colormap)
        self.indicator_image_obj.set_cmap(self.colormap)

    def update_span_min(self):
        new_min_value = self.min_slider.value
        self.under_span.remove()
        self.under_span = plt.axvspan(0, new_min_value, facecolor=self.under_color, alpha=0.2)

    def update_span_max(self):
        new_max_value = self.max_slider.value
        self.over_span.remove()
        self.over_span = plt.axvspan(new_max_value, 255, facecolor=self.over_color, alpha=0.2)

    def change_image_clim_prio_max(self, change=None):
        new_min_value = self.min_slider.value
        new_max_value = self.max_slider.value
        if new_max_value < new_min_value:
            self.min_slider.value = new_max_value - 1
        else:
            self.image_obj.set_clim((new_min_value,new_max_value))
            self.indicator_image_obj.set_clim((new_min_value, new_max_value))
            self.minimum_line.set_data([new_min_value, new_min_value], [0, 1])
            self.maximum_line.set_data([new_max_value, new_max_value], [0, 1])
            if self.show_over_under.value:
                self.update_span_max()

    def change_image_clim_prio_min(self, change=None):
        new_min_value = self.min_slider.value
        new_max_value = self.max_slider.value
        if new_min_value > new_max_value:
            self.max_slider.value = new_min_value + 1
        else:
            self.image_obj.set_clim((new_min_value,new_max_value))
            self.indicator_image_obj.set_clim((new_min_value, new_max_value))
            self.minimum_line.set_data([new_min_value, new_min_value], [0, 1])
            self.maximum_line.set_data([new_max_value, new_max_value], [0, 1])
            if self.show_over_under.value:
                self.update_span_min()




    def create_text_annotation(self, image, axes):
        text_annotation = {}
        for i in range(image.shape[0]):
            text_annotation[i] = dict()
            for j in range(image.shape[1]):
                if np.isnan(image[i, j]):
                    image_text = ''
                else:
                    image_text = str(np.round(image[i, j], 2))
                text_annotation[i][j] = axes.text(j, i, image_text,
                                                  ha="center", va="center", color="w", backgroundcolor=[0, 0, 0, 0.1])

        return text_annotation

    def update_text_annotation(self, text_annotation, image):
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                if np.isnan(image[i, j]):
                    image_text = ''
                else:
                    image_text = str(np.round(image[i, j], 2))
                text_annotation[i][j].set_text(image_text)

# LUT_2D_Widget()