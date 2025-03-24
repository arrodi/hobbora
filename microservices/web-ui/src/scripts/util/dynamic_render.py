from flask import render_template, session, g
import logging

logger = logging.getLogger(__name__)

def dynamic_render(page, **kwargs):
    logger.info(f"Rendering {page}")
    if session.get('user'):
        kwargs['encoded_image'] = g.current_user.get_profile_picture() if g.current_user else None
        kwargs['config'] = g.settings.config
        kwargs['user'] = g.current_user.get_json() if g.current_user else {}
    else:
        kwargs['encoded_image'] = b''
        kwargs['config'] = g.settings.config
        kwargs['user'] = {}
    return render_template(page, **kwargs)