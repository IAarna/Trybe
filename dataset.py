# dataset.py - Contains predefined body shapes and sizes

BODY_SHAPES = ["Slim", "Athletic", "Curvy", "Plus Size"]
SIZES = ["S", "M", "L", "XL", "XXL"]

def validate_selection(body_shape, size):
    """
    Validate if the given body shape and size are valid.
    
    :param body_shape: str - The selected body shape
    :param size: str - The selected size
    :return: tuple (bool, str) - (Validation result, Message)
    """
    body_shape = body_shape.title()  # Ensure case consistency
    size = size.upper()  # Ensure case consistency

    if body_shape not in BODY_SHAPES:
        return False, f"Invalid body shape: {body_shape}. Choose from {BODY_SHAPES}."
    
    if size not in SIZES:
        return False, f"Invalid size: {size}. Choose from {SIZES}."
    
    return True, "Valid selection"

# Example usage
if __name__ == "__main__":
    result, message = validate_selection("curvy", "m")
    print(message)  # Outputs: "Valid selection"