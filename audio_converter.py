#!usr/bin/env python3
"""
simple little command line tool wrapper of pydub for converting audio files.
basically just wraps very, very basic functionality from ffmpeg,
but good for simple conversions without much thinking

requires pydub with ffmpeg:
https://github.com/jiaaro/pydub#installation
"""

import argparse
import glob
import os
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError


def convert_a_file(audio_file, out, out_enc, in_enc, frameRate):

    root, ext = os.path.splitext(os.path.basename(audio_file))

    in_enc = in_enc if in_enc else ext.strip('.')

    audio = AudioSegment.from_file(audio_file, format=in_enc)
    frameRate = frameRate if frameRate else audio.frame_rate

    out_base = '.'.join([root, out_enc])
    if os.path.isdir(out):
        audio.set_frame_rate(frameRate).export(os.path.join(out, out_base),
                                               format=out_enc)
    else:
        audio.set_frame_rate(frameRate).export(out,
                                               format=out_enc)


def convert_one_directory(args, in_dir, out_dir):
    extensions = [ex.strip('.') for ex in args.match_extensions]
    files_here = []
    for ext in extensions:
        files_here += glob.glob(os.path.join(in_dir, '*.'+ext))

    if files_here:
        for audio_file in files_here:
            try:
                convert_a_file(audio_file,
                               out_dir,
                               args.out_file_encoding,
                               args.in_file_encoding,
                               args.frame_rate)

            except CouldntDecodeError as e:
                if _V:
                    print("Couldn't decode {}".format(audio_file))
                if not _S:
                    raise e


def recursive_convert(args):
    abs_in_dir = os.path.abspath(args.path)
    abs_out_dir = os.path.abspath(args.out)

    all_dirs = []
    for root, dirs, files in os.walk(abs_in_dir):
        all_dirs.append(root)

    for in_dir in all_dirs:
        full_out_dir = in_dir.replace(abs_in_dir, abs_out_dir)

        os.makedirs(full_out_dir, exist_ok=True)
        convert_one_directory(args, in_dir, full_out_dir)




parser = argparse.ArgumentParser(description='Converts audio files. '
                                 'Tries to infer format by file extension. '
                                 'but can be provided explicitly')

# Base functionality - convert file
parser.add_argument('path', help='Either an audio file or a directory.')

parser.add_argument('-o', '--out', default='.',
                    help='Either the name of a file or a directory. '
                    'Default to working directory. If batch converting '
                    'must be an existing directory.')

parser.add_argument('-e', '--out-file-encoding', default='mp3',
                    help='File type to convert to. Can use any type '
                    'defined by ffmpeg. Defaults to mp3')

parser.add_argument('-i', '--in-file-encoding',
                    help='File format of input file. Can be any format '
                    'covered by ffmpeg. Caution, will be used on all '
                    'files if batch converting.')

parser.add_argument('-f', '--frame-rate', type=int,
                    help='Frame rate to encode new file. '
                    'Defaults to rate of source file')

parser.add_argument('-v', '--verbose', action='store_true',
                    help='more output messages.')

# Batch converting arguments
parser.add_argument('-m', '--match-extensions', nargs='+',
                    help='Extensions to search for and convert '
                    'If empty, just quit.')

parser.add_argument('-s', '--skip-encode-errors', action='store_true')

parser.add_argument('-r', '--recursive', action='store_true',
                    help='traverse sub directories recursively. '
                    'Will preserve the underlying file structure '
                    'with new parent directory OUT. As always, '
                    'be careful with recursion.')


args = parser.parse_args()

_V = args.verbose
_S = args.skip_encode_errors

if _V:
    print('Given path: {}'.format(args.path))
if os.path.isfile(args.path):
    if _V:
        print("Converting single file")
    convert_a_file(args.path,
                   args.out,
                   args.out_file_encoding,
                   args.in_file_encoding,
                   args.frame_rate)

if os.path.isdir(args.path):

    if not args.match_extensions:
        if _V:
            print('No extensions supplied to match.\n'
                  'No files will be converted\n'
                  'Specify files extensions  to match with -m')
        quit()

    if not args.recursive:
        if _V:
            print("Converting a directory")
        convert_one_directory(args, args.path, args.out)

    else:
        recursive_convert(args)
