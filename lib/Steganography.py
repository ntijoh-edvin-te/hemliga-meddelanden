import logging
from PIL import Image
from .SteganographyError import SteganographyError

class Steganography:
    """
    Provides steganography functionality to hide and retrieve messages in images.
    """
    
    TERMINATOR = "%%%"
    
    def __init__(self, logger=None):
        """Initialize with logger"""
        self.logger = logger or logging.getLogger(__name__)
        
    def encode(self, image_path, message, output_path):
        """
        Encode a message into an image.
        
        Args:
            image_path (str): Path to the input image
            message (str): Message to encode
            output_path (str): Path where to save the encoded image
        """
        self.logger.info(f"Starting encoding to {output_path}")
        
        try:
            with Image.open(image_path) as img:
                img = img.convert("RGB")
                pixels = img.load()
                width, height = img.size
                
                binary_msg = self._message_to_binary(message + self.TERMINATOR)
                required_bits = len(binary_msg)
                
                bits_per_pixel = 3
                max_bits_per_channel = 4
                
                bits_per_channel = 1
                while (width * height * bits_per_pixel * bits_per_channel < required_bits and 
                       bits_per_channel < max_bits_per_channel):
                    bits_per_channel += 1
                
                available_bits = width * height * bits_per_pixel * bits_per_channel
                
                if required_bits > available_bits:
                    raise SteganographyError(
                        f"Message too large ({required_bits} bits needed, {available_bits} available) "
                        f"even with {bits_per_channel} bits per channel"
                    )

                self.logger.info(f"Using {bits_per_channel} bit(s) per color channel for encoding")
                
                r, g, b = pixels[0, 0]
                pixels[0, 0] = (
                    (r & 0xF8) | bits_per_channel,
                    g,
                    b
                )
                
                self._embed_bits_multi_depth(pixels, binary_msg, width, height, bits_per_channel, start_pixel=1)
                img.save(output_path)
                self.logger.info("Encoding completed successfully")
                
        except Exception as e:
            self.logger.error(f"Encoding failed: {str(e)}")
            raise SteganographyError("Encoding failed") from e

    def decode(self, image_path):
        """
        Decode a message from an image.
        
        Args:
            image_path (str): Path to the encoded image
            
        Returns:
            str: Decoded message
        """
        self.logger.info(f"Starting decoding from {image_path}")
        
        try:
            with Image.open(image_path) as img:
                img = img.convert("RGB")
                
                pixels = img.load()
                r, g, b = pixels[0, 0]
                bits_per_channel = r & 0x07
                
                if bits_per_channel < 1 or bits_per_channel > 4:
                    self.logger.warning("Invalid bit depth detected, using 1 bit per channel")
                    bits_per_channel = 1
                else:
                    self.logger.info(f"Detected {bits_per_channel} bit(s) per color channel")
                
                binary_str = self._extract_bits_multi_depth(img, bits_per_channel, start_pixel=1)
                message = self._binary_to_message(binary_str)
                
                if self.TERMINATOR not in message:
                    self.logger.warning("No termination sequence found in decoded message")
                    
                return message.split(self.TERMINATOR)[0]
                
        except Exception as e:
            self.logger.error(f"Decoding failed: {str(e)}")
            raise SteganographyError("Decoding failed") from e
    
    def calculate_capacity(self, image_path):
        """
        Calculate the maximum number of characters that can be encoded using 1 bit per channel.
        
        Args:
            image_path (str): Path to the input image
            
        Returns:
            int: Maximum number of characters that can be encoded

        """
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                
                bits_per_pixel = 3
                bits_per_channel = 1
                
                total_pixels = width * height - 1
                
                available_bits = total_pixels * bits_per_pixel * bits_per_channel
                
                max_chars = (available_bits // 8) - len(self.TERMINATOR)
                
                return max(0, max_chars)
                
        except Exception as e:
            self.logger.error(f"Capacity calculation failed: {str(e)}")
            raise SteganographyError("Failed to calculate image capacity") from e

    # Private methods
    def _message_to_binary(self, message):
        """Convert message to binary string"""
        return ''.join(format(ord(c), '08b') for c in message)

    def _binary_to_message(self, binary_str):
        """Convert binary string to message"""
        message = ""
        for i in range(0, len(binary_str), 8):
            byte = binary_str[i:i+8]
            if len(byte) < 8:
                break
            message += chr(int(byte, 2))
        return message

    def _embed_bits_multi_depth(self, pixels, binary_msg, width, height, bits_per_channel, start_pixel=0):
        """Embed bits into image pixels"""
        index = 0
        bit_masks = [(0xFF << b) & 0xFF for b in range(bits_per_channel)]
        
        for y in range(height):
            for x in range(width):
                if start_pixel > 0 and x == 0 and y == 0:
                    continue
                    
                if index >= len(binary_msg):
                    return
                
                r, g, b = pixels[x, y]
                
                for channel_value, channel_name in [(r, 'r'), (g, 'g'), (b, 'b')]:
                    new_value = channel_value & (0xFF << bits_per_channel)
                    
                    for bit_pos in range(bits_per_channel):
                        if index < len(binary_msg):
                            if binary_msg[index] == '1':
                                new_value |= (1 << bit_pos)
                            index += 1
                    
                    if channel_name == 'r':
                        r = new_value
                    elif channel_name == 'g':
                        g = new_value
                    else:
                        b = new_value
                
                pixels[x, y] = (r, g, b)

    def _extract_bits_multi_depth(self, img, bits_per_channel, start_pixel=0):
        """Extract bits from image pixels"""
        binary_str = ""
        width, height = img.size
        pixels = img.load()
        
        self.logger.info(f"Scanning image using {bits_per_channel} bit(s) per channel...")
        
        for y in range(height):
            for x in range(width):
                if start_pixel > 0 and x == 0 and y == 0:
                    continue
                    
                r, g, b = pixels[x, y]
                
                for channel_value in [r, g, b]:
                    for bit_pos in range(bits_per_channel):
                        binary_str += '1' if (channel_value & (1 << bit_pos)) else '0'
                
                if len(binary_str) % (24 * bits_per_channel) == 0:
                    current_text = self._binary_to_message(binary_str)
                    if self.TERMINATOR in current_text:
                        self.logger.info(f"Terminator found at position {x},{y}")
                        terminator_pos = current_text.find(self.TERMINATOR) + len(self.TERMINATOR)
                        binary_length = terminator_pos * 8
                        return binary_str[:binary_length]
                        
                if (y % 50) == 0 and x == 0 and y > 0:
                    progress = (y * 100) // height
                    self.logger.info(f"Progress: {progress}% - Processed {y} of {height} rows...")
        
        self.logger.warning("No terminator found when analysing image")
        return binary_str