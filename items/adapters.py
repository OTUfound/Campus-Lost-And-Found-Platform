from allauth.account.adapter import DefaultAccountAdapter


class EmailDomainAdapter(DefaultAccountAdapter):
    def clean_email(self, email):
        email = super().clean_email(email)
        if not email.endswith('@ostimteknik.edu.tr'):
            raise ValueError('Email must be from @ostimteknik.edu.tr domain')
        return email

