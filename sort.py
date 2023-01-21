#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
from typing import List, io


def chunk_file(chunk_number: int) -> str:
    return "chunk_%s.txt" % chunk_number


def save_chunk(chunk: list[str], chunk_number: int) -> None:
    chunk.sort()
    with open(chunk_file(chunk_number), "w") as out:
        out.writelines(chunk)


def merge_chunks(chunk_count: int, output: str) -> None:
    files: List[io | None] = [None] * chunk_count
    strings: List[str | None] = [None] * chunk_count

    for chunk_number in range(chunk_count):
        if os.path.exists(chunk_file(chunk_number)):
            files[chunk_number] = open(chunk_file(chunk_number), "r")
            strings[chunk_number] = files[chunk_number].readline()
        else:
            chunk_count = chunk_number
            strings[chunk_number] = ""
            break

    with open(output, "w") as out:
        while True:
            min: str | None = None
            min_index = -1
            for chunk_number in range(chunk_count):
                if strings[chunk_number] and (min is None or min > strings[chunk_number]):
                    min = strings[chunk_number]
                    min_index = chunk_number
            if min is None:
                break
            out.write(min)
            strings[min_index] = files[min_index].readline()

    for chunk_number in range(chunk_count):
        if files[chunk_number]:
            os.unlink(chunk_file(chunk_number))
            files[chunk_number].close()


def sort(chunk_count: int, chunk_size: int, input: str, output: str) -> None:
    chunk: list[str]
    chunk_number = 0

    with open(input, "r") as original:
        chunk = []
        for row in original:
            chunk.append(row)
            if len(chunk) >= chunk_size:
                save_chunk(chunk, chunk_number)
                chunk_number += 1
                chunk = []
            if chunk_number >= chunk_count:
                merge_chunks(chunk_count, output)
                os.rename(output, chunk_file(0))
                chunk_number = 1

    save_chunk(chunk, chunk_number)
    merge_chunks(chunk_count, output)
    for chunk_number in range(chunk_count):
        if os.path.exists(chunk_file(chunk_number)):
            os.unlink(chunk_file(chunk_number))


parser = argparse.ArgumentParser()
parser.add_argument("-c", "--count", help="Chunks count", type=int, default=10)
parser.add_argument("-s", "--chunk-size", help="Chunk size (lines count)", type=int, default=100000)
parser.add_argument("-i", "--input", help="Input filename", default="in.txt")
parser.add_argument("-o", "--output", help="Output filename", default="out.txt")
args = parser.parse_args()
sort(args.count, args.chunk_size, args.input, args.output)
