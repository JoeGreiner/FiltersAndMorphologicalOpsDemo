import numpy as np
from ipywidgets import widgets
import matplotlib.pyplot as plt
from itk import binary_dilate_image_filter,\
    binary_morphological_closing_image_filter,\
    binary_morphological_opening_image_filter,\
    binary_erode_image_filter,\
    GetArrayFromImage,\
    GetImageFromArray


class OpenCloseWidget():
    def __init__(self):
        self.image = np.zeros((50,50), dtype=np.uint8)
        self.image[13, 13] = 255
        self.image[20:30, 20:23] = 255
        self.image[30, 21] = 255
        self.image[31:40, 20:23] = 255
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
        plt.clim((0,255))

    def opening(self, event):
        itk_image = GetImageFromArray(self.image)
        self.image = GetArrayFromImage(binary_morphological_opening_image_filter(itk_image))
        self.img_obj.set_data(self.image)

    
    def closing(self, event):
        itk_image = GetImageFromArray(self.image)
        self.image = GetArrayFromImage(binary_morphological_closing_image_filter(itk_image))
        self.img_obj.set_data(self.image)

    def reset(self, event):
        self.image = self.image_copy
        self.img_obj.set_data(self.image_copy)


class DilateErodeWidget():
    def __init__(self):
        self.image = np.zeros((50,50), dtype=np.uint8)
        self.image[13, 13] = 255
        self.image[20:30, 20:23] = 255
        self.image[30, 21] = 255
        self.image[31:40, 20:23] = 255
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
        plt.clim((0,255))

    def dilate(self, event):
        itk_image = GetImageFromArray(self.image)
        self.image = GetArrayFromImage(binary_dilate_image_filter(itk_image))
        self.img_obj.set_data(self.image)
        
    def erode(self, event):
        itk_image = GetImageFromArray(self.image)
        self.image = GetArrayFromImage(binary_erode_image_filter(itk_image))
        self.img_obj.set_data(self.image)
        
    def reset(self, event):
        self.image = self.image_copy
        self.img_obj.set_data(self.image_copy)

class Drawer():
    def __init__(self, paint_width=1, paint_value = 255, erase_value=0):
        self.drawing = False
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
        plt.clim((0,255))           
        plt.show()
         
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.fig.canvas.mpl_connect('button_release_event', self.onrelease)
        self.fig.canvas.mpl_connect('motion_notify_event', self.onmove)
    
    def create_image(self):
        return np.zeros((100,100), dtype=np.uint8)

    def dilate(self, event):
        itk_image = GetImageFromArray(self.image)
        self.image = GetArrayFromImage(binary_dilate_image_filter(itk_image))
        self.img_obj.set_data(self.image)
        
    def erode(self, event):
        itk_image = GetImageFromArray(self.image)
        self.image = GetArrayFromImage(binary_erode_image_filter(itk_image))
        self.img_obj.set_data(self.image)
    
    def reset(self, event):
        self.image = self.create_image()
        self.img_obj.set_data(self.image)

    def opening(self, event):
        itk_image = GetImageFromArray(self.image)
        self.image = GetArrayFromImage(binary_morphological_opening_image_filter(itk_image))
        self.img_obj.set_data(self.image)

    
    def closing(self, event):
        itk_image = GetImageFromArray(self.image)
        self.image = GetArrayFromImage(binary_morphological_closing_image_filter(itk_image))
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

