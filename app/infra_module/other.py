from enum import Enum


class UserRole(Enum):
    ADMIN = 1
    READWRITE = 2
    READ = 3


ROLE_LABELS = {
    UserRole.ADMIN: 'Admin',
    UserRole.READWRITE: 'Read / Write',
    UserRole.READ: 'Read Only',
}

ROLE_CHOICES = [
    ('1', 'Admin'),
    ('2', 'Read / Write'),
    ('3', 'Read Only'),
]

SERVER_STATUS_CHOICES = [
    ('active', 'Active'),
    ('planned', 'Planned'),
    ('staged', 'Staged'),
    ('offline', 'Offline'),
    ('decommissioning', 'Decommissioning'),
    ('failed', 'Failed'),
]

STATUS_BADGE = {
    'active':          'success',
    'planned':         'info',
    'staged':          'warning',
    'offline':         'secondary',
    'decommissioning': 'warning',
    'failed':          'danger',
}


def status_badge(status: str) -> str:
    return STATUS_BADGE.get(status, 'secondary')


def role_label(role_int) -> str:
    try:
        return ROLE_LABELS[UserRole(int(role_int))]
    except (ValueError, KeyError):
        return str(role_int)


def _parse_hex_rgb(hex_color: str, default: tuple[int, int, int] = (13, 110, 253)) -> tuple[int, int, int]:
    h = (hex_color or '').lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    if len(h) != 6:
        return default
    try:
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except ValueError:
        return default


def hex_text_color(hex_color: str, *, dark: str = '#212529', light: str = '#fff') -> str:
    """Return a readable text color for the given hex background."""
    r, g, b = _parse_hex_rgb(hex_color)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return dark if brightness >= 128 else light


def color_badge_style(hex_color: str, default: str = '0d6efd') -> str:
    """Inline CSS for a colored badge with contrasting text."""
    color = (hex_color or default).lstrip('#')
    bg = f'#{color}'
    return f'background-color:{bg};color:{hex_text_color(color)}'


def split_ip_addresses(value: str) -> list[str]:
    """Split comma/newline-separated IP strings into individual addresses."""
    if not value:
        return []
    ips = []
    for part in value.replace(',', '\n').split('\n'):
        ip = part.strip()
        if ip:
            ips.append(ip)
    return ips
