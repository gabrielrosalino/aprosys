from django import forms
from django.template.loader import render_to_string


class CustomRelatedFieldWidgetWrapper(forms.Widget):
    """
    Widget que permite abrir um formulário relacionado em popup
    e atualizar automaticamente o select na página pai.
    """

    def __init__(self, widget, rel, add_url=None, *args, **kwargs):
        self.widget = widget
        self.rel = rel
        self.add_url = add_url
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        """
        Renderiza o select com botão de adicionar em popup.
        """
        context = {
            'widget': self.widget.render(name, value, attrs, renderer),
            'name': name,
            'add_url': self.add_url,
        }
        return render_to_string('widgets/related_field_wrapper.html', context)

    def value_from_datadict(self, data, files, name):
        return self.widget.value_from_datadict(data, files, name)

    def id_for_label(self, id_):
        return self.widget.id_for_label(id_)
