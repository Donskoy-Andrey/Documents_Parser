from PIL import Image

image_path = 'back.png'
ico_path = 'train.png'
output_path = 'output.png'

def place_ico_on_image(image_path, ico_path, step, i):
    # Open the image and ICO files
    image = Image.open(image_path)
    ico = Image.open(ico_path).resize((200,200))
    print(ico.size)
    print(image.size)

    # Resize the ICO to a desired size (optional)
    # ico = ico.resize((50, 50))

    # Calculate the position to place the ICO on the image
    position = (0 + step, -30)
    print(step)
    # Paste the ICO onto the image at the calculated position
    image.paste(ico, position, mask=ico)

    # Save the modified image with the ICO placed on it
    if 10 > i > 0:
        image.save(f"gif/output-00{i}.png")
    elif i<100:
        image.save(f"gif/output-0{i}.png")
    else:
        image.save(f"gif/output-{i}.png")

def spam():
    step = 0
    i = 0
    ds = 10
    while step < 1472:
        place_ico_on_image(image_path, ico_path, step=step, i=i)
        step += ds
        i += 1
# Example usage:


spam()