import os
from django.conf import settings
import matplotlib.pyplot as plt

def save_plot(plot_img_path):
    """
    Save the plot image to the specified path.

    Args:
        plot_img_path (str): The path where the plot image will be saved.

    Returns:
        str: The URL of the saved plot image.
    """
    image_path = os.path.join(settings.MEDIA_ROOT, plot_img_path)
    plt.savefig(image_path)
    plt.close()
    image_url = settings.MEDIA_URL + plot_img_path
    return image_url
