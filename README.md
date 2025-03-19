# Hemliga Meddelanden

A steganography tool for hiding secret messages within images.

<img src="https://github.com/ntijoh-edvin-te/hemliga-meddelanden/blob/main/data/input/example_image.jpg?raw=true" style="height: 500px;" />

## Requirements

- Python 3.6+
- Pillow
- colorama

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/ntijoh-edvin-te/hemliga-meddelanden
   cd hemliga-meddelanden
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Interactive Mode

Run the application without any arguments to use interactive mode:

```
python main.py
```

### Command Line Mode

Encode a message:

```
python main.py encode <input_image_path> <message> [-o <output_image_path>]
```

Decode a message:

```
python main.py decode <encoded_image_path>
```

### Examples

Encode:

```
python main.py encode ./data/input/image.jpg "Hemliga meddelanden" => 12345_encoded.png
```

Decode:

```
python main.py decode data/output/12345_encoded.png => "Hemliga meddelanden"
```

## How it works

This application uses the Least Significant Bit (LSB) steganography technique to hide messages in images. Each bit of the message is stored in the least significant bit of a color channel (R, G, B) of pixels in the image.
