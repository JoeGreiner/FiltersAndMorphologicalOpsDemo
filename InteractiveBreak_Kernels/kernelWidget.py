import numpy as np
from ipywidgets import widgets
import matplotlib.pyplot as plt
from scipy import ndimage
from skimage import data
from ipywidgets import Checkbox

class KernelWidget():
    def __init__(self, kernel_min=-8, kernel_max=8, small_example=True, small_example_size=7):
        # close all old figures
        plt.close("all")


        self.box_absolute = Checkbox(False, description='absolute value')
        self.box_absolute.observe(handler=self.convolve)

        self.box_norm = Checkbox(False, description='normalize')
        self.box_norm.observe(handler=self.convolve)

        self.w00 = widgets.IntSlider(min=kernel_min, max=kernel_max, value=0)
        self.w01 = widgets.IntSlider(min=kernel_min, max=kernel_max, value=0)
        self.w02 = widgets.IntSlider(min=kernel_min, max=kernel_max, value=0)
        self.w10 = widgets.IntSlider(min=kernel_min, max=kernel_max, value=0)
        self.w11 = widgets.IntSlider(min=kernel_min, max=kernel_max, value=1)
        self.w12 = widgets.IntSlider(min=kernel_min, max=kernel_max, value=0)
        self.w20 = widgets.IntSlider(min=kernel_min, max=kernel_max, value=0)
        self.w21 = widgets.IntSlider(min=kernel_min, max=kernel_max, value=0)
        self.w22 = widgets.IntSlider(min=kernel_min, max=kernel_max, value=0)

        self.kernel =  np.zeros((3,3), dtype=np.int8)
        self.kernel[1, 1] = 1

        self.set_kernel_observe_on()

        self.small_example = small_example
        self.small_example_size = small_example_size
        self.small_example_mid_point = small_example_size // 2
        if self.small_example:
            self.image = np.ones((small_example_size, small_example_size))
            self.image[self.small_example_mid_point, :] = 3
        else:
            self.image = data.brick()
            self.image = self.image.astype(np.float32)

        self.convolved_image = np.empty_like(self.image)

        self.axes = plt.figure(figsize=(9, 4), constrained_layout=True).subplot_mosaic(
            """
            AAAAA..BBBBB
            AAAAACCBBBBB
            AAAAACCBBBBB
            AAAAA..BBBBB
            """
        )

        self.ax_left = self.axes['A']
        self.ax_middle = self.axes['C']
        self.ax_right = self.axes['B']

        plt.sca(self.ax_left)
        self.original_img = self.ax_left.imshow(self.image, cmap='gray')
        self.ax_left.xaxis.set_visible(False)
        self.ax_left.yaxis.set_visible(False)
        plt.title('Original Image')

        plt.sca(self.ax_middle)
        self.kernel_obj = self.ax_middle.imshow(self.kernel, interpolation='none', cmap='seismic')
        self.kernel_obj.set_clim(kernel_min, kernel_max)
        self.ax_middle.xaxis.set_visible(False)
        self.ax_middle.yaxis.set_visible(False)
        plt.title('Kernel')

        plt.sca(self.ax_right)
        self.ax_right.sharex(self.ax_left)
        self.ax_right.sharey(self.ax_left)
        self.img_obj = self.ax_right.imshow(self.image, cmap='gray')
        self.ax_right.xaxis.set_visible(False)
        self.ax_right.yaxis.set_visible(False)
        plt.title('Filtered Image')
        if self.small_example:
            self.img_obj.set_clim(0, 1+np.max([np.max(self.image), np.max(self.convolved_image)]))
            self.original_img.set_clim(0, 1+np.max([np.max(self.image), np.max(self.convolved_image)]))


        self.kernel_text = self.create_text_annotation(self.kernel, axes=self.ax_middle)

        if self.small_example:
            self.original_text = self.create_text_annotation(self.image, axes=self.ax_left)
            self.conv_text = self.create_text_annotation(self.convolved_image, axes=self.ax_right)

        # plt.title('Used 3x3 kernel')

        if small_example:
            data_selection_options = ['random noise', 'vertical line', 'horizontal line', 'vertical block', 'horizontal block', 'point']
            default_value_img = 'vertical line'
        else:
            data_selection_options = ['cat', 'brick']
            default_value_img = 'brick'


        self.image_data_selection = widgets.Dropdown(options=data_selection_options,
                                                     description='Image Data:',
                                                     value=default_value_img)



        self.image_data_selection.observe(self.create_image_data, names='value')

        kernel_selection_options = ['Identity', 'Box', 'Gaussian', 'Laplacian',  'Sharpen', 'Prewitt_X', 'Prewitt_Y', 'Sobel_X', 'Sobel_Y']
        default_value_kernel = 'Identity'

        self.kernel_selection = widgets.Dropdown(options=kernel_selection_options,
                                            description='Kernel:',
                                            value=default_value_kernel)

        self.kernel_selection.observe(self.set_kernel, names='value')


        #update right image
        self.convolve()

        self.hbox_1 = widgets.HBox((self.w00, self.w01, self.w02))
        self.hbox_2 = widgets.HBox((self.w10, self.w11, self.w12))
        self.hbox_3 = widgets.HBox((self.w20, self.w21, self.w22))
        self.hbox_dropdowns = widgets.HBox((self.image_data_selection, self.kernel_selection))
        self.hbox_modifiers = widgets.HBox((self.box_absolute, self.box_norm))

        self.vbox = widgets.VBox((self.hbox_dropdowns, self.hbox_modifiers, self.hbox_1, self.hbox_2, self.hbox_3))

        display(self.vbox)

    def set_kernel_observe_on(self):
        self.w00.observe(handler=self.convolve)
        self.w01.observe(handler=self.convolve)
        self.w02.observe(handler=self.convolve)
        self.w10.observe(handler=self.convolve)
        self.w11.observe(handler=self.convolve)
        self.w12.observe(handler=self.convolve)
        self.w20.observe(handler=self.convolve)
        self.w21.observe(handler=self.convolve)
        self.w22.observe(handler=self.convolve)

    def set_kernel_observe_off(self):
        self.w00.unobserve(handler=self.convolve)
        self.w01.unobserve(handler=self.convolve)
        self.w02.unobserve(handler=self.convolve)
        self.w10.unobserve(handler=self.convolve)
        self.w11.unobserve(handler=self.convolve)
        self.w12.unobserve(handler=self.convolve)
        self.w20.unobserve(handler=self.convolve)
        self.w21.unobserve(handler=self.convolve)
        self.w22.unobserve(handler=self.convolve)

    def create_image_data(self, change):
        if self.small_example:
            if change['new'] == 'random noise':
                self.image = (1+np.random.rand(self.small_example_size,self.small_example_size)*4).astype(np.int32)
                self.original_img = self.ax_left.imshow(self.image, cmap='gray')
            elif change['new'] == 'vertical line':
                self.image = np.ones((self.small_example_size,self.small_example_size))
                self.image[self.small_example_mid_point,:] = 3
            elif change['new'] == 'horizontal line':
                self.image = np.ones((self.small_example_size, self.small_example_size))
                self.image[:, self.small_example_mid_point] = 3
            elif change['new'] == 'horizontal block':
                self.image = np.ones((self.small_example_size, self.small_example_size))
                self.image[:, self.small_example_mid_point:] = 3
            elif change['new'] == 'vertical block':
                self.image = np.ones((self.small_example_size, self.small_example_size))
                self.image[self.small_example_mid_point:, :] = 3
            elif change['new'] == 'point':
                self.image = np.ones((self.small_example_size, self.small_example_size))
                self.image[self.small_example_mid_point, self.small_example_mid_point] = 3

        else:
            if change['new'] == 'cat':
                self.image = data.cat()[:, :, 0]
            elif change['new'] == 'brick':
                self.image = data.brick()

        self.image = self.image.astype(np.float32)


        self.convolve()

        self.ax_left.clear()
        self.ax_right.clear()


        self.original_img = self.ax_left.imshow(self.image, cmap='gray')
        self.ax_left.set_title('Original Image')
        self.img_obj = self.ax_right.imshow(self.convolved_image, cmap='gray')
        self.ax_right.set_title('Filtered Image')

        if self.small_example:
            self.original_text = self.create_text_annotation(self.image, axes=self.ax_left)
            self.conv_text = self.create_text_annotation(self.convolved_image, axes=self.ax_right)


    def set_kernel(self, change=None):
        self.set_kernel_observe_off()
        if change['new'] == 'Identity':
            self.kernel[:, :] = 0
            self.kernel[1, 1] = 1
        elif change['new'] == 'Box':
            self.kernel[:, :] = 1
        elif change['new'] == 'Gaussian':
            self.kernel[0, 0] = 1
            self.kernel[0, 1] = 2
            self.kernel[0, 2] = 1
            self.kernel[1, 0] = 2
            self.kernel[1, 1] = 4
            self.kernel[1, 2] = 2
            self.kernel[2, 0] = 1
            self.kernel[2, 1] = 2
            self.kernel[2, 2] = 1
        elif change['new'] == 'Prewitt_X':
            self.kernel[:, :] = 0
            self.kernel[:, 0] = 1
            self.kernel[:, -1] = -1
        elif change['new'] == 'Prewitt_Y':
            self.kernel[:, :] = 0
            self.kernel[0, :] = 1
            self.kernel[-1, :] = -1
        elif change['new'] == 'Sobel_X':
            self.kernel[:, :] = 0
            self.kernel[:, 0] = 1
            self.kernel[1, 0] = 2
            self.kernel[:, -1] = -1
            self.kernel[1, -1] = -2
        elif change['new'] == 'Sobel_Y':
            self.kernel[:, :] = 0
            self.kernel[0, :] = 1
            self.kernel[0, 1] = 2
            self.kernel[-1, :] = -1
            self.kernel[-1, 1] = -2
        elif change['new'] == 'Laplacian':
            self.kernel[:, :] = 0
            self.kernel[0, 1] = 1
            self.kernel[1, 0] = 1
            self.kernel[1, 1] = -4
            self.kernel[1, 2] = 1
            self.kernel[2, 1] = 1
        elif change['new'] == 'Sharpen':
            self.kernel[:, :] = 0
            self.kernel[0, 1] = -1
            self.kernel[1, 0] = -1
            self.kernel[1, 1] = 5
            self.kernel[1, 2] = -1
            self.kernel[2, 1] = -1

        self.transfer_kernel_to_widgets()
        self.set_kernel_observe_on()
        self.convolve()

    def transfer_kernel_to_widgets(self):
        self.w00.value = self.kernel[0, 0]
        self.w01.value = self.kernel[0, 1]
        self.w02.value = self.kernel[0, 2]
        self.w10.value = self.kernel[1, 0]
        self.w11.value = self.kernel[1, 1]
        self.w12.value = self.kernel[1, 2]
        self.w20.value = self.kernel[2, 0]
        self.w21.value = self.kernel[2, 1]
        self.w22.value = self.kernel[2, 2]

    def update_kernel(self):
        self.kernel_obj.set_data(self.kernel)
        self.update_text_annotation(text_annotation=self.kernel_text, image=self.kernel)

    def update_image(self):
        self.original_img.set_data(self.image)
        if self.small_example:
            self.update_text_annotation(text_annotation=self.original_text, image=self.image)

    def update_conv(self):
        self.img_obj.set_data(self.convolved_image)
        if not self.small_example:
            self.img_obj.autoscale()
        else:
            self.img_obj.set_clim(self.min_imgs(self.image, self.convolved_image),
                                  1 + self.max_imgs(self.image, self.convolved_image))
            self.original_img.set_clim(self.min_imgs(self.image, self.convolved_image),
                                  1 + self.max_imgs(self.image, self.convolved_image))
            self.update_text_annotation(text_annotation=self.conv_text, image=self.convolved_image)

    def max_imgs(self, img1, img2):
        return np.nanmax([np.nanmax(img1), np.nanmax(img2)])

    def min_imgs(self, img1, img2):
        return np.nanmin([np.nanmin(img1), np.nanmin(img2)])


    def convolve(self, change=None):
        self.kernel = np.array([[self.w00.value, self.w01.value, self.w02.value], [self.w10.value, self.w11.value, self.w12.value], [self.w20.value, self.w21.value, self.w22.value]])
        if self.box_norm.value == True:
            sum_of_kernel = np.sum(self.kernel)
            if sum_of_kernel != 0:
                self.kernel = self.kernel / sum_of_kernel
        self.update_kernel()
        self.kernel = np.flipud(np.fliplr(self.kernel))

        self.convolved_image = ndimage.convolve(self.image, self.kernel, mode='nearest')
        if self.box_absolute.value == True:
            self.convolved_image = np.abs(self.convolved_image)


        if self.small_example:
            self.convolved_image[0,:] = np.nan
            self.convolved_image[-1,:] = np.nan
            self.convolved_image[:,0] = np.nan
            self.convolved_image[:,-1] = np.nan
        self.update_conv()

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
