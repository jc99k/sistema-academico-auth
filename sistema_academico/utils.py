def user_display(user):
    """
    Return a display string for the user.
    Since we don't have username, use email or full name.
    """
    if hasattr(user, 'get_full_name'):
        full_name = user.get_full_name()
        if full_name:
            return full_name

    if hasattr(user, 'email'):
        return user.email

    return str(user)
