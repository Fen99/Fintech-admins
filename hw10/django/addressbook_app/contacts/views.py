from django.urls import reverse
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from contacts import forms
from contacts.models import Contact


class ListContactView(ListView):

    model = Contact
    template_name = 'contact_list.html'


class CreateContactView(LoginRequiredMixin, CreateView):

    model = Contact
    template_name = 'edit_contact.html'

    form_class = forms.ContactForm

    def get_success_url(self):
        return reverse('contacts-list')

    def get_context_data(self, **kwargs):
        context = super(CreateContactView, self).get_context_data(**kwargs)
        context['action'] = reverse('contacts-new')

        return context


class UpdateContactView(LoginRequiredMixin, UpdateView):

    model = Contact
    template_name = 'edit_contact.html'
    fields = ('first_name', 'last_name', 'email')

    def get_context_data(self, **kwargs):
        print('update')
        context = super(UpdateContactView, self).get_context_data(**kwargs)
        context['action'] = reverse('contacts-edit',
                                    kwargs={'pk': self.get_object().id})

        return context

    def get_success_url(self):
        return reverse('contacts-list')


class DeleteContactView(DeleteView):

    model = Contact
    template_name = 'delete_contact.html'

    def get_success_url(self):
        return reverse('contacts-list')


class ContactView(DetailView):

    model = Contact
    template_name = 'contact.html'


class EditContactAddressView(UpdateView):

    model = Contact
    template_name = 'edit_addresses.html'
    form_class = forms.ContactAddressFormSet

    def get_success_url(self):

        # redirect to the Contact view.
        return self.get_object().get_absolute_url()
