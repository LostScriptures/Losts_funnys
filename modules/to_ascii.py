"""ASCII converter module for Losts_funnys CLI.

Provides a `do_ascii` command that can:
- print ASCII codes for a string (--codes)
- render ASCII art using `pyfiglet` if available or a small built-in fallback (--art)

Usage (from CLI):
  ascii --art --scale 3 --fill "#" Hello world
  ascii --codes "Hi"

The CLI loader in `cli.py` will attach `do_ascii` and `help_ascii` to the main CLI.
"""

import shlex
import argparse

def _try_pyfiglet():
	try:
		import pyfiglet
		return pyfiglet
	except Exception:
		return None

def _simple_block_art(text: str, scale: int = 3, fill: str = '#') -> str:
	"""Create a very simple block-style ASCII art by scaling characters into filled blocks.

	This is intentionally simple and dependency-free: each non-space character becomes
	a block of `fill` of size scale x scale. Words are separated by a single column of spaces.
	"""
	if scale < 1:
		scale = 1

	rows = []
	for _ in range(scale):
		parts = []
		for ch in text:
			if ch == ' ':
				parts.append(' ' * scale)
			else:
				parts.append(fill * scale)
		rows.append(' '.join(parts))

	return '\n'.join(rows)

def do_ascii(self, args: str):
	"""Convert text to ASCII art or show ASCII codes.

	Examples:
	  ascii --art Hello
	  ascii --art --scale 4 --fill "*" "Big!"
	  ascii --codes "Hi"
	"""

	argv = shlex.split(args)
	parser = argparse.ArgumentParser(prog='ascii', add_help=False)
	parser.add_argument('--art', '-a', action='store_true', help='Render ASCII art')
	parser.add_argument('--codes', '-c', action='store_true', help='Print ASCII codes (decimal)')
	parser.add_argument('--style', '-s', default='auto', help='pyfiglet font name or "block" for fallback')
	parser.add_argument('--scale', type=int, default=3, help='Scale for builtin block art (integer)')
	parser.add_argument('--fill', default='#', help='Fill character for builtin block art')
	parser.add_argument('text', nargs='*', help='Text to convert')

	try:
		ns = parser.parse_args(argv)
	except SystemExit:
		# argparse prints its own help on error; keep CLI running
		print('Usage: ascii [--art] [--codes] [--scale N] [--fill C] text...')
		return

	text = ' '.join(ns.text) if ns.text else input('Text: ')

	if ns.codes:
		# Print decimal ASCII codes separated by spaces
		codes = ' '.join(str(ord(ch)) for ch in text)
		print(codes)
		return

	if ns.art:
		pyfiglet = _try_pyfiglet()
		# Use pyfiglet unless user explicitly requested block style or pyfiglet missing
		if pyfiglet and ns.style != 'block':
			try:
				font = None if ns.style == 'auto' else ns.style
				# If font is None, pyfiglet chooses default font
				print(pyfiglet.figlet_format(text, font=font) )
				return
			except Exception:
				# Fall through to builtin fallback
				pass

		# Fallback simple block art
		art = _simple_block_art(text, scale=ns.scale, fill=ns.fill[0] if ns.fill else '#')
		print(art)
		return

	# If no flag given, show plain text and hint
	print(text)
	print('\nHint: use --art to render ASCII art or --codes to show ASCII values.')

def help_ascii(self):
	print(do_ascii.__doc__)
