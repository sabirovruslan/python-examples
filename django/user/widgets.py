from django.forms import ClearableFileInput


class ClearableImageInput(ClearableFileInput):
    template_name = 'widgets/clearable_image_input.html'
