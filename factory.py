from models import User, Administrator, VeterinaryExpert, FirstAidGuide, VideoContent, Quiz

class AccountFactory:
    @staticmethod
    def create_account(role, username, email, password, first_name, last_name, phone_number=None):
        """
        Factory method to create subclasses of Account.
        """
        role_lower = role.strip().lower()
        
        if role_lower == 'user':
            account = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                role='user'
            )
        elif role_lower == 'admin':
            account = Administrator(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                role='admin'
            )
        elif role_lower == 'vet':
            account = VeterinaryExpert(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                role='vet'
            )
        else:
            raise ValueError(f"Unknown account role: {role}")
        
        account.set_password(password)
        return account


class ContentFactory:
    @staticmethod
    def create_content(content_type, title, description, author_id, **kwargs):
        """
        Factory method to create subclasses of Content.
        """
        type_lower = content_type.strip().lower()
        
        if type_lower == 'guide':
            severity = kwargs.get('severity', 'Minor')
            species = kwargs.get('species', 'Other')
            return FirstAidGuide(
                title=title,
                description=description,
                author_id=author_id,
                severity=severity,
                species=species,
                content_type='guide'
            )
        elif type_lower == 'video':
            video_url = kwargs.get('video_url', '')
            duration = kwargs.get('duration', '0:00')
            transcript = kwargs.get('transcript', '')
            species = kwargs.get('species', 'Other')
            severity = kwargs.get('severity', 'Minor')
            return VideoContent(
                title=title,
                description=description,
                author_id=author_id,
                video_url=video_url,
                duration=duration,
                transcript=transcript,
                species=species,
                severity=severity,
                content_type='video'
            )
        elif type_lower == 'quiz':
            species = kwargs.get('species', 'Other')
            return Quiz(
                title=title,
                description=description,
                author_id=author_id,
                species=species,
                content_type='quiz'
            )
        else:
            raise ValueError(f"Unknown content type: {content_type}")
