from django import template

register = template.Library()

@register.filter(name='price_format')
def price_format(value):
    """Formats a number string to have a comma after the first two digits."""
    if not value:
        return "0.00"
    
    # Convert to string and handle floats/decimals safely
    val_str = f"{value:.2f}" if isinstance(value, (int, float)) else str(value)
    
    # Split into integer and decimal parts
    parts = val_str.split('.')
    int_part = parts[0]
    dec_part = f".{parts[1]}" if len(parts) > 1 else ""
    
    # Add comma after first two digits
    if len(int_part) > 2:
        formatted_int = f"{int_part[:2]},{int_part[2:]}"
    else:
        formatted_int = int_part
        
    return f"{formatted_int}{dec_part}"
