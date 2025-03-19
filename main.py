import argparse
import os
import pathlib
from lib.Steganography import Steganography
from lib.ColorFormatter import ColorFormatter
from utils.generate_suffix import generate_suffix
from utils.setup_logger import setup_logger
from utils.ensure_directories import ensure_directories

def main():
    """
    Main entry point.
    """
    ensure_directories()
    
    logger = setup_logger(ColorFormatter)
    stego = Steganography(logger)

    default_output_path = pathlib.Path(f"./data/output/{generate_suffix()}_encoded.png").absolute()

    parser = argparse.ArgumentParser(
        description="Steganography Tool - Hide messages in images",
        epilog="Example: python main.py encode input.jpg 'secret message' -o output.png"
    )
    subparsers = parser.add_subparsers(dest='command', required=False)

    encode_parser = subparsers.add_parser('encode', help="Encode a message into an image")
    encode_parser.add_argument('input', nargs='?', help="Input image path")
    encode_parser.add_argument('message', nargs='?', help="Message to encode")
    encode_parser.add_argument('-o', '--output', default=default_output_path, 
                             help="Output image path (default: ./data/output/<random>_encoded.png)")

    decode_parser = subparsers.add_parser('decode', help="Decode a message from an image")
    decode_parser.add_argument('input', nargs='?', help="Encoded image path")

    args = parser.parse_args()

    if not args.command:
        print("Steganography Tool - Hide messages in images")
        print("-------------------------------------------")
        args.command = input("Command (encode/decode): ").strip()
        if args.command.lower() == 'encode':
            args.input = None
            args.message = None
            args.output = str(default_output_path)
        elif args.command.lower() == 'decode':
            args.input = None

    try:
        if args.command.lower() == 'encode':
            input_path = getattr(args, 'input', None) or input("Enter input image path: ").strip() 
            
            try:
                max_chars = stego.calculate_capacity(input_path)
                logger.info(f"Maximum message size: {max_chars} characters with basic LSB encoding")
            except Exception as e:
                logger.warning(f"Failed to calculate capacity: {str(e)}")
            
            message = getattr(args, 'message', None) or input("Enter message to encode: ").strip()
            output_prompt = f"Enter output image path (default: {default_output_path}): "
            output_path = args.output or input(output_prompt).strip() or default_output_path
            
            os.makedirs(os.path.dirname(str(output_path)), exist_ok=True)
            
            stego.encode(input_path, message, output_path)
            logger.info(f"Message encoded successfully in {output_path}")
        
        elif args.command.lower() == 'decode':
            input_path = getattr(args, 'input', None) or input("Enter encoded image path: ").strip()
            
            message = stego.decode(input_path)
            logger.info("Decoded message:")
            print(f"\n{message}\n")
        
        else:
            print("Invalid command. Use 'encode' or 'decode'.")
            exit(1)
            
    except Exception as e:
        logger.error(f"Operation failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()