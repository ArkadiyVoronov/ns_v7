from app.forms.forms import RegistrationForm, LoginForm, EditProfileForm


class TestFormFactory:
    @staticmethod
    def create_registration_form(valid=True):
        if valid:
            return RegistrationForm(
                username='test_user',
                email='test@example.com',
                password='test_password',
                confirm_password='test_password'
            )
        return RegistrationForm(
            username='',
            email='invalid_email',
            password='short',
            confirm_password='different'
        )

    @staticmethod
    def create_login_form(valid=True):
        if valid:
            return LoginForm(
                email='test@example.com',
                password='test_password'
            )
        return LoginForm(
            email='',
            password=''
        )

    @staticmethod
    def create_edit_profile_form(valid=True, original_username='test_user'):
        form = EditProfileForm(original_username=original_username)
        if valid:
            form.username.data = 'new_username'
        else:
            form.username.data = ''
        return form
