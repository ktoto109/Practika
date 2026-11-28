from django import forms

from .models import Asteroid


class AsteroidForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_image = self.instance.image if self.instance and self.instance.pk else None
        self.fields['spectral_class'].empty_label = 'Выберите класс'
        self.fields['image'].required = not bool(self._original_image)
        self.fields['image'].error_messages['required'] = 'Фото обязательно.'

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image and not self._original_image:
            raise forms.ValidationError('Фото обязательно.')
        return image

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self._original_image and not self.cleaned_data.get('image'):
            instance.image = self._original_image
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    class Meta:
        model = Asteroid
        fields = (
            'title',
            'description',
            'price',
            'distance',
            'image',
            'spectral_class',
            'compositions',
            'status',
        )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'admin-form__input'}),
            'description': forms.Textarea(attrs={'class': 'admin-form__textarea', 'rows': 5}),
            'price': forms.NumberInput(attrs={'class': 'admin-form__input', 'min': 0}),
            'distance': forms.NumberInput(attrs={'class': 'admin-form__input', 'min': 0}),
            'image': forms.FileInput(attrs={'class': 'admin-form__file'}),
            'spectral_class': forms.Select(attrs={'class': 'admin-form__select'}),
            'compositions': forms.CheckboxSelectMultiple(),
            'status': forms.Select(attrs={'class': 'admin-form__select'}),
        }
