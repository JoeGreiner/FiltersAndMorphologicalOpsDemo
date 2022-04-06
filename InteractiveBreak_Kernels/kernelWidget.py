import numpy as np
from ipywidgets import widgets
import matplotlib.pyplot as plt
from scipy import ndimage
from skimage import data

class KernelWidget():
    def __init__(self, kernel_min=-6, kernel_max=6, small_example=True):
        # if not annotate_images:
        #     self.image = data.cat()[:,:,0]
        #     self.image = self.image.astype(np.float32)
        # else:
        self.small_example = small_example
        if small_example:
            self.image = (1+np.random.rand(5,5)*4).astype(np.int32)
        else:
            self.image = data.cat()[:,:,0]
            self.image = self.image.astype(np.float32)

        self.convolved_image = self.image

        self.kernel =  np.zeros((3,3), dtype=np.int8)
        self.kernel[1, 1] = 1


        self.axes = plt.figure(figsize=(9, 4), constrained_layout=True).subplot_mosaic(
            """
            AAA.BBB
            AAACBBB
            AAA.BBB
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
        if small_example:
            self.img_obj.set_clim(0, 1+np.max([np.max(self.image), np.max(self.convolved_image)]))
            self.original_img.set_clim(0, 1+np.max([np.max(self.image), np.max(self.convolved_image)]))


        self.kernel_text = self.create_text_annotation(self.kernel, axes=self.ax_middle)

        if self.small_example:
            self.original_text = self.create_text_annotation(self.image, axes=self.ax_left)
            self.conv_text = self.create_text_annotation(self.convolved_image, axes=self.ax_right)

        # plt.title('Used 3x3 kernel')

        self.w00 = widgets.IntSlider(min=kernel_min, max=kernel_max, value=0)
        self.w01 = widgets.IntSlider(min=kernel_min, max=kernel_max, value=0)
        self.w02 = widgets.IntSlider(min=kernel_min, max=kernel_max, value=0)
        self.w10 = widgets.IntSlider(min=kernel_min, max=kernel_max, value=0)
        self.w11 = widgets.IntSlider(min=kernel_min, max=kernel_max, value=1)
        self.w12 = widgets.IntSlider(min=kernel_min, max=kernel_max, value=0)
        self.w20 = widgets.IntSlider(min=kernel_min, max=kernel_max, value=0)
        self.w21 = widgets.IntSlider(min=kernel_min, max=kernel_max, value=0)
        self.w22 = widgets.IntSlider(min=kernel_min, max=kernel_max, value=0)

        self.w00.observe(handler=self.convolve)
        self.w01.observe(handler=self.convolve)
        self.w02.observe(handler=self.convolve)
        self.w10.observe(handler=self.convolve)
        self.w11.observe(handler=self.convolve)
        self.w12.observe(handler=self.convolve)
        self.w20.observe(handler=self.convolve)
        self.w21.observe(handler=self.convolve)
        self.w22.observe(handler=self.convolve)

        if small_example:
            data_selection_options = ['random noise', 'vertical edges', 'horizontal edges']
            default_value = 'random noise'
        else:
            data_selection_options = ['cat', 'brick']
            default_value = 'cat'


        self.filter_selection = widgets.Dropdown(options=data_selection_options,
                                            description='Image Data:',
                                            value=default_value)

        self.filter_selection.observe(self.create_image_data, names='value')

        self.hbox_1 = widgets.HBox((self.w00, self.w01, self.w02))
        self.hbox_2 = widgets.HBox((self.w10, self.w11, self.w12))
        self.hbox_3 = widgets.HBox((self.w20, self.w21, self.w22))

        self.vbox = widgets.VBox((self.filter_selection, self.hbox_1, self.hbox_2, self.hbox_3))

        display(self.vbox)



    def create_image_data(self, change):
        if self.small_example:
            if change['new'] == 'random noise':
                self.image = (1+np.random.rand(5,5)*4).astype(np.int32)
                self.original_img = self.ax_left.imshow(self.image, cmap='gray')
            elif change['new'] == 'vertical edges':
                self.image = np.zeros((5,5))
                self.image[0,:] = 1
                self.image[2,:] = 1
                self.image[4,:] = 1
            elif change['new'] == 'horizontal edges':
                self.image = np.zeros((5, 5))
                self.image[:, 0] = 1
                self.image[:, 2] = 1
                self.image[:, 4] = 1
        else:
            if change['new'] == 'cat':
                self.image = data.cat()[:, :, 0]
            elif change['new'] == 'brick':
                self.image = data.brick()

            self.image = self.image.astype(np.float32)


        self.convolve()
        self.update_image()




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
                                  1 + np.max([np.max(self.image), np.max(self.convolved_image)]))
            self.original_img.set_clim(self.min_imgs(self.image, self.convolved_image),
                                  1 + np.max([np.max(self.image), np.max(self.convolved_image)]))
            self.update_text_annotation(text_annotation=self.conv_text, image=self.convolved_image)

    def max_imgs(self, img1, img2):
        return np.max([np.max(img1), np.max(img2)])

    def min_imgs(self, img1, img2):
        return np.min([np.min(img1), np.min(img2)])


    def convolve(self, change=None):
        self.kernel = np.array([[self.w00.value, self.w01.value, self.w02.value], [self.w10.value, self.w11.value, self.w12.value], [self.w20.value, self.w21.value, self.w22.value]])
        self.update_kernel()
        self.kernel = np.flipud(np.fliplr(self.kernel))

        self.convolved_image = ndimage.convolve(self.image, self.kernel, mode='constant', cval=0.)
        self.update_conv()

    def create_text_annotation(self, image, axes):
        text_annotation = {}
        for i in range(image.shape[0]):
            text_annotation[i] = dict()
            for j in range(image.shape[1]):
                text_annotation[i][j] = axes.text(j, i, image[i, j],
                               ha="center", va="center", color="w", backgroundcolor=[0, 0, 0, 0.1])

        return text_annotation

    def update_text_annotation(self, text_annotation, image):
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                text_annotation[i][j].set_text(str(image[i, j]))
