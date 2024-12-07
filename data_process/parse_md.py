# -*- coding: utf-8 -*-

import re
import os
import shutil
import logging


class MarkdownSplitter:
    def __init__(self, input_file, output_dir, logger):
        self.input_file = os.path.abspath(input_file)
        self.output_dir = os.path.abspath(output_dir)
        self.logger = logger
        self.logger.info(f'Processing input file: {self.input_file}')
        self.logger.info(f'Output directory: {self.output_dir}')

    def read_markdown(self):
        with open(self.input_file, 'r', encoding='utf-8') as file:
            return file.read()

    def extract_metadata(self, content):
        metadata_pattern = r'(?s)^(---[\s\S]+?---)'
        match = re.match(metadata_pattern, content)
        if match:
            metadata = match.group(1)
            content = content[len(metadata):].lstrip()
            return metadata, content
        return None, content

    def split_by_headers(self, content):
        lines = content.splitlines()
        segments = []
        current_segment_lines = []
        header_stack = []

        for i, line in enumerate(lines):
            header_match = re.match(r'^(#{2,4})\s+(.*)', line)
            if header_match:
                header_level = len(header_match.group(1))
                if header_level == 2:
                    if self.has_content(current_segment_lines):
                        segments.append('\n'.join(current_segment_lines).strip())
                    header_stack = [line.strip()]
                    current_segment_lines = header_stack.copy()
                elif header_level == 3:
                    if self.has_content(current_segment_lines):
                        segments.append('\n'.join(current_segment_lines).strip())
                    if len(header_stack) < 1:
                        header_stack = ['']
                    header_stack = [header_stack[0], line.strip()]
                    current_segment_lines = header_stack.copy()
                elif header_level == 4:
                    if self.has_content(current_segment_lines):
                        segments.append('\n'.join(current_segment_lines).strip())
                    if len(header_stack) < 2:
                        if len(header_stack) == 0:
                            header_stack = ['']
                        header_stack = header_stack + ['']
                    header_stack = header_stack[:2] + [line.strip()]
                    current_segment_lines = header_stack.copy()
                else:
                    current_segment_lines.append(line)
            else:
                current_segment_lines.append(line)

        if self.has_content(current_segment_lines):
            segments.append('\n'.join(current_segment_lines).strip())

        return [seg for seg in segments if seg.strip()]

    def has_content(self, lines):
        for line in lines:
            if not re.match(r'^#{2,4}\s', line) and line.strip() != '':
                return True
        return False

    def extract_toc_from_content(self):
        markdown_content = self.read_markdown()
        toc = []
        for line in markdown_content.splitlines():
            if re.match(r'^\#{2,4}\s+\d+(\.\d+)*\.?\s', line):
                toc.append(line.strip())
        return '\n'.join(toc)

    def save_segments(self, segments, metadata=None):
        base_dir = os.path.join(self.output_dir, os.path.splitext(os.path.basename(self.input_file))[0])
        base_dir = os.path.abspath(base_dir)
        os.makedirs(base_dir, exist_ok=True)
        base_filename = os.path.splitext(os.path.basename(self.input_file))[0]

        metadata_file_path = None
        if metadata:
            metadata_file_path = os.path.join(base_dir, f'{base_filename}_metadata.md')
            metadata_file_path = os.path.abspath(metadata_file_path)
            with open(metadata_file_path, 'w', encoding='utf-8') as meta_file:
                meta_file.write(metadata)

        chunk_file_paths = []
        for i, segment in enumerate(segments, start=1):
            segment_file_path = os.path.join(base_dir, f'{base_filename}_chunk_{i}.md')
            segment_file_path = os.path.abspath(segment_file_path)
            with open(segment_file_path, 'w', encoding='utf-8') as seg_file:
                seg_file.write(segment + '\n')
            chunk_file_paths.append(segment_file_path)

        toc = self.extract_toc_from_content()
        toc_file_path = os.path.join(base_dir, f'{base_filename}_toc.md')
        toc_file_path = os.path.abspath(toc_file_path)
        with open(toc_file_path, 'w', encoding='utf-8') as toc_file:
            toc_file.write(toc + '\n')

        return metadata_file_path, chunk_file_paths, toc_file_path

    def process(self):
        markdown_content = self.read_markdown()
        metadata, markdown_content = self.extract_metadata(markdown_content)
        chunks = self.split_by_headers(markdown_content)
        return self.save_segments(chunks, metadata)


def process_directory(input_dir, output_dir, logger):

    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(output_dir)

    logger.info("=" * 50)
    delete_output_dir(output_dir)
    logger.info(f'Deleting existing output directory: {output_dir}')
    logger.info(f'Input directory: {input_dir}')
    logger.info(f'Output directory: {output_dir}')
    logger.info("=" * 50 + "\n")

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.md'):
                input_file = os.path.join(root, file)
                input_file = os.path.abspath(input_file)
                logger.info("=" * 50)
                logger.info(f'Start processing: {input_file}')
                logger.info("-" * 50)

                splitter = MarkdownSplitter(input_file, output_dir, logger)
                metadata_path, chunk_files, toc_file = splitter.process()

                if metadata_path:
                    logger.info(f'Metadata saved to {metadata_path}')
                logger.info(f'TOC saved to {toc_file}')

                logger.info('Chunks saved to:')
                for chunk_file in chunk_files:
                    logger.info(chunk_file)

                logger.info("-" * 50)
                logger.info(f'Finished processing: {input_file}')
                logger.info("=" * 50 + "\n")


def delete_output_dir(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)


def setup_logging(log_path):

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)

    handler = logging.FileHandler(log_path)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.abspath(os.path.join(current_dir, '../data/blog_input'))
    output_dir = os.path.abspath(os.path.join(current_dir, '../data/blog_output'))
    log_path = os.path.abspath(os.path.join(current_dir, './parse_md.log'))
    logger = setup_logging(log_path)
    process_directory(input_dir, output_dir, logger)
