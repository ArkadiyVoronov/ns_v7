import pytest


@pytest.mark.usefixtures("client")
class TestForms:
    """Тестирование форм с использованием pytest"""

    def test_registration_form_valid(self, registration_form_valid):
        """Тест формы регистрации с корректными данными"""
        assert registration_form_valid.validate(), "Форма регистрации с валидными данными не прошла валидацию."

    def test_registration_form_invalid(self, registration_form_invalid):
        """Тест формы регистрации с некорректными данными"""
        assert not registration_form_invalid.validate(), "Форма регистрации с невалидными данными прошла валидацию."

    def test_login_form_valid(self, login_form_valid):
        """Тест формы входа с корректными данными"""
        assert login_form_valid.validate(), "Форма входа с валидными данными не прошла валидацию."

    def test_login_form_invalid(self, login_form_invalid):
        """Тест формы входа с некорректными данными"""
        assert not login_form_invalid.validate(), "Форма входа с невалидными данными прошла валидацию."

    def test_edit_profile_form_valid(self, edit_profile_form_valid):
        """Тест формы редактирования профиля с корректными данными"""
        assert edit_profile_form_valid.validate(), "Форма редактирования профиля с валидными данными не прошла " \
                                                   "валидацию."

    def test_edit_profile_form_invalid(self, edit_profile_form_invalid):
        """Тест формы редактирования профиля с некорректными данными"""
        assert not edit_profile_form_invalid.validate(), "Форма редактирования профиля с невалидными данными прошла " \
                                                         "валидацию."

    def test_result_form_valid(self, result_form_valid):
        """Тест формы подтверждения выполнения тренировки с корректными данными"""
        assert result_form_valid.validate(), "Форма подтверждения тренировки с валидными данными не прошла валидацию."

    def test_result_form_invalid(self, result_form_invalid):
        """Тест формы подтверждения выполнения тренировки с некорректными данными"""
        assert not result_form_invalid.validate(), "Форма подтверждения тренировки с невалидными данными прошла " \
                                                   "валидацию."
