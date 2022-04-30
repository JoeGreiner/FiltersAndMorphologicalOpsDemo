import numpy as np
from imageio import imread
from ipywidgets import widgets
import matplotlib.pyplot as plt
from skimage import data
from skimage.color import rgb2gray


class LUT_2D_Widget():
    def __init__(self, indicator_scale_length = 15):
        # close all old figures
        plt.close("all")
        self.indicator_scale_length = indicator_scale_length


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
        self.colorbar = plt.colorbar(extend='max')
        self.ax_bottom_right.xaxis.set_visible(False)
        self.ax_bottom_right.yaxis.set_visible(False)
        plt.title('Image With Applied LUT')

        plt.sca(self.ax_bottom_left)
        plt.hist(self.image.flatten(), bins=range(0, 255 + 1, 1), color='gray')
        self.minimum_line = plt.axvline(0, color='r')
        self.maximum_line = plt.axvline(255, color='r')
        plt.title('Data Histogram')
        plt.xlabel('Data Values')
        plt.ylabel('Count')

        self.indicator_text = self.create_text_annotation(self.indicator_scale, axes=self.ax_top)

        self.min_slider = widgets.IntSlider(description='Minimum:', min=0, max=254, value=0)
        self.max_slider = widgets.IntSlider(description='Maximum:', min=1, max=255, value=255)
        self.min_slider.observe(handler=self.change_image_clim_prio_min)
        self.max_slider.observe(handler=self.change_image_clim_prio_max)

        data_selection_options = ['cat', 'WGA', 'DAPI']
        default_value_img = 'cat'

        self.image_selection_dropdown = widgets.Dropdown(options=data_selection_options,
                                                         description='Image Data:',
                                                         value=default_value_img)

        self.image_selection_dropdown.observe(self.create_image_data, names='value')


        LUT_selection_options = sorted(['viridis', 'plasma', 'inferno', 'binary', 'gray',
                      'hot', 'Spectral', 'hsv', 'rainbow'])
        default_LUT_value = 'gray'
        self.lut_dropdown = widgets.Dropdown(options=LUT_selection_options,
                                             description='LUT:',
                                             value=default_LUT_value)
        self.lut_dropdown.observe(handler=self.change_cmap, names='value')
        self.change_cmap({'new':default_LUT_value})

        self.vbox = widgets.VBox((self.image_selection_dropdown, self.lut_dropdown, self.min_slider, self.max_slider))

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
                                                     cmap=self.lut_dropdown.value,
                                                     vmin=self.min_slider.value,
                                                     vmax=self.max_slider.value)
        self.colorbar.remove()
        plt.sca(self.ax_bottom_right)
        self.colorbar = plt.colorbar(extend='max')
        plt.title('Image With Applied LUT')

        self.ax_bottom_left.clear()
        plt.sca(self.ax_bottom_left)
        plt.hist(self.image.flatten(), bins=range(0, 255 + 1, 1), color='gray')
        self.minimum_line = plt.axvline(self.min_slider.value, color='r')
        self.maximum_line = plt.axvline(self.max_slider.value, color='r')
        plt.title('Data Histogram')
        plt.xlabel('Data Values')
        plt.ylabel('Count')

    def change_cmap(self, change):
        self.image_obj.set_cmap(change['new'])
        self.indicator_image_obj.set_cmap(change['new'])

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

