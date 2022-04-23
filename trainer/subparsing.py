import os
import re
from typing import Iterator, Union

from text.processing import default_line_processors, default_extractors, processed_string, SrtConversionSettings, extracted_sub


def srt_from_vtt(lines: Union[Iterator[str], Iterator[bytes]], settings: SrtConversionSettings = None) -> str:
    settings = (
        settings if settings is not None else SrtConversionSettings(default_extractors(), default_line_processors(), True)
    )
    processors = settings.processors if settings is not None else default_line_processors()
    extractors = settings.extractors if settings is not None else default_extractors()
    one_line = settings.one_line if settings is not None else True
    sep = os.linesep
    ending = f"{sep}{sep}" if one_line else f"{sep}"
    stage = 0
    current_text = ""
    sub_count = 1
    buffer = ""
    result = ""

    for line in lines:
        line = str(line, encoding='utf8') if isinstance(line, bytes) else line
        if stage == 2 and line == '\n':
            stage = 0
            current_text = processed_string(current_text, processors)
            if current_text:
                result += f"{buffer}{current_text}{ending}"
                sub_count += 1
            buffer = ""
            current_text = ""
            continue
        if re.search(r'^\d+$', line):
            buffer += f'{sub_count}\n'
            stage = 1
            continue
        if stage == 1:
            time = re.search(r'^([^ ]* --> [^ ]*)', line).group(1)
            buffer += f'{time}\n'
            stage = 2
            continue
        if stage == 2:
            text = extracted_sub(line, extractors)
            current_text = (
                    current_text
                    + (" " if current_text != "" and one_line else "")
                    + text
                    + (sep if not one_line else "")
            )
    return result


if __name__ == '__main__':

    name = "기생충"
    src_path = f"D:\\langapp\\langapp\\media\\auto_convert\\vtt.vtt"
    dest_path = f"D:\\langapp\\langapp\\media\\auto_convert\\{name}.srt"
    settings = SrtConversionSettings(default_extractors(), [], False)

    with open(src_path, "r", encoding="utf-8") as src:
        with open(dest_path, "w+", encoding="utf-8") as dest:
            dest.write(srt_from_vtt(src, settings))

    print(f"Conversion from {src_path} to {dest_path} finished.")
    exit()
