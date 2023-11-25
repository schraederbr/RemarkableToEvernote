from pdf2image import convert_from_path

def pdf_to_png(pdf_path, output_path):
    # Convert the PDF to images
    images = convert_from_path(pdf_path)

    for i, image in enumerate(images):
        # Save each image as a PNG file
        image.save(f'{output_path}/output_{i}.png', 'PNG')

# Usage
pdf_to_png('../PDFs/rmrl2.pdf', '../PNGs')