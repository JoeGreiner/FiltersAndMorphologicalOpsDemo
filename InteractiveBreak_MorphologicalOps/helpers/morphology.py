import numpy as np
from ipywidgets import widgets
import matplotlib.pyplot as plt

from skimage.morphology import binary_closing, binary_erosion, binary_opening, binary_dilation, square

# Future: Grayscale Dilation on real images
# different footprints?

class OpenCloseWidget():
    def __init__(self, binary_value=1, footprint=square(3)):
        self.image = np.zeros((50,50), dtype=np.uint8)
        self.binary_value = binary_value
        self.footprint = footprint
        self.image[13, 13] = binary_value
        self.image[20:30, 20:23] = binary_value
        self.image[30, 21] = binary_value
        self.image[31:40, 20:23] = binary_value
        self.image_copy = self.image


        reset_button = widgets.Button(description='Reset Image')
        open_button = widgets.Button(description='Open')
        close_button = widgets.Button(description='Close')

        reset_button.on_click(self.reset)
        open_button.on_click(self.opening)
        close_button.on_click(self.closing)
        
        display(widgets.HBox([open_button, close_button, reset_button]))

        self.fig = plt.figure(figsize=(5,5))
        self.img_obj = plt.imshow(self.image, origin='lower')
        plt.clim((0,self.binary_value))

    def opening(self, event):
        self.image = binary_opening(self.image, footprint=self.footprint)
        self.img_obj.set_data(self.image)

    
    def closing(self, event):
        self.image = binary_closing(self.image, footprint=self.footprint)
        self.img_obj.set_data(self.image)

    def reset(self, event):
        self.image = self.image_copy
        self.img_obj.set_data(self.image_copy)


class DilateErodeWidget():
    def __init__(self, binary_value=1, footprint=square(3)):
        self.image = np.zeros((50,50), dtype=np.uint8)
        self.binary_value = binary_value
        self.footprint = footprint
        self.image[13, 13] = binary_value
        self.image[20:30, 20:23] = binary_value
        self.image[30, 21] = binary_value
        self.image[31:40, 20:23] = binary_value
        self.image_copy = self.image


        reset_button = widgets.Button(description='Reset Image')
        dilate_button = widgets.Button(description='Dilate')
        erode_button = widgets.Button(description='Erode')

        dilate_button.on_click(self.dilate)
        erode_button.on_click(self.erode)
        reset_button.on_click(self.reset)
        
        display(widgets.HBox([dilate_button, erode_button, reset_button]))

        self.fig = plt.figure(figsize=(5,5))
        self.img_obj = plt.imshow(self.image, origin='lower')
        plt.clim((0,self.binary_value))

    def dilate(self, event):
        self.image = binary_dilation(self.image, footprint=self.footprint)
        self.img_obj.set_data(self.image)
        
    def erode(self, event):
        self.image = binary_erosion(self.image, footprint=self.footprint)
        self.img_obj.set_data(self.image)
        
    def reset(self, event):
        self.image = self.image_copy
        self.img_obj.set_data(self.image_copy)

class Drawer():
    def __init__(self, paint_width=1, paint_value = 1, erase_value=0, footprint=square(3)):
        self.drawing = False
        self.footprint = footprint
        self.paint_width = paint_width
        self.paint_value = paint_value
        self.erase_value = erase_value
        self.image = self.create_image()
        
        dilate_button = widgets.Button(description='Dilate')
        erode_button = widgets.Button(description='Erode')
        open_button = widgets.Button(description='Open')
        close_button = widgets.Button(description='Close')
        reset_button = widgets.Button(description='Reset Image')

        dilate_button.on_click(self.dilate)
        erode_button.on_click(self.erode)
        open_button.on_click(self.opening)
        close_button.on_click(self.closing)
        reset_button.on_click(self.reset)

        display(widgets.HBox([dilate_button,erode_button, open_button, close_button, reset_button]))

        self.fig = plt.figure(figsize=(5,5))
        self.img_obj = plt.imshow(self.image, origin='lower')
        plt.clim((0,self.paint_value))
        plt.show()
         
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.fig.canvas.mpl_connect('button_release_event', self.onrelease)
        self.fig.canvas.mpl_connect('motion_notify_event', self.onmove)
    
    def create_image(self):
        return np.zeros((100,100), dtype=np.uint8)

    def dilate(self, event):
        self.image = binary_dilation(self.image, footprint=self.footprint)
        self.img_obj.set_data(self.image)

    def erode(self, event):
        self.image = binary_erosion(self.image, footprint=self.footprint)
        self.img_obj.set_data(self.image)

    def reset(self, event):
        self.image = self.create_image()
        self.img_obj.set_data(self.image)

    def opening(self, event):
        self.image = binary_opening(self.image, footprint=self.footprint)
        self.img_obj.set_data(self.image)

    def closing(self, event):
        self.image = binary_closing(self.image, footprint=self.footprint)
        self.img_obj.set_data(self.image)

    def onclick(self, event):
        self.drawing = True
        if event.button == 1:
                self.draw_point(int(event.xdata), int(event.ydata), self.paint_value)
        elif event.button == 3:
                self.draw_point(int(event.xdata), int(event.ydata), self.erase_value)

    def onmove(self, event):
        if event.button == 1:
                self.draw_point(int(event.xdata), int(event.ydata), self.paint_value)
        elif event.button == 3:
                self.draw_point(int(event.xdata), int(event.ydata), self.erase_value)

    def draw_point(self, ix, iy, value):
        if self.drawing == True:
            if self.paint_width == 0:
                self.image[iy, ix] = value 
                self.img_obj._A.data[iy, ix] = value
            else:
                self.image[iy-self.paint_width : iy+self.paint_width,
                           ix-self.paint_width : ix+self.paint_width] = value
                self.img_obj._A.data[iy-self.paint_width : iy+self.paint_width,
                                     ix-self.paint_width : ix+self.paint_width] = value
            plt.draw()
        
    def onrelease(self, event):
        self.drawing=False

