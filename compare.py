import shutil
from difflib import SequenceMatcher, get_close_matches
from pathlib import Path
from typing import Iterator

DL_FOLDER = Path("/quirinalis/Bagarre/Torrent/")
TRASH_FOLDER = DL_FOLDER / "corbeille"
TRASH_FOLDER.mkdir(exist_ok=True)
CUTOFF = 0.8


def diff_strings(a: str, b: str) -> str:
    output = []
    matcher = SequenceMatcher(None, a, b)

    green = "\x1b[38;5;16;48;5;2m"
    red = "\x1b[38;5;16;48;5;1m"
    endgreen = "\x1b[0m"
    endred = "\x1b[0m"

    for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
        if opcode == "equal":
            output.append(a[a0:a1])
        elif opcode == "insert":
            output.append(f"{green}{b[b0:b1]}{endgreen}")
        # elif opcode == "delete":
        #     output.append(f"{red}{a[a0:a1]}{endred}")
        elif opcode == "replace":
            output.append(f"{green}{b[b0:b1]}{endgreen}")
            # output.append(f"{red}{a[a0:a1]}{endred}")

    return "".join(output)


def remove_zeros(filename: str) -> str:
    if not filename.startswith("0"):
        return filename
    parts = filename.split(" ", 1)
    if len(parts) == 2 and all(x == "0" for x in parts[0]):
        return parts[1]
    else:
        return filename


def get_torrent_files() -> Iterator[Path]:
    files = sorted(list(DL_FOLDER.glob("*.torrent")), key=lambda x: x.stem)
    for file_ in files:
        if file_.exists():
            yield file_


for file_ in get_torrent_files():
    # filename = remove_zeros(file_.stem)
    # if not file_.with_stem(filename).exists():
    #     shutil.move(file_, file_.with_stem(filename))
    filename = file_.stem
    matches = get_close_matches(
        filename,
        [
            remove_zeros(x.stem)
            for x in DL_FOLDER.glob("*.torrent")
            if x.name != file_.name
        ],
        n=2,
        cutoff=0.8,
    )
    if matches:
        print(f">>> {filename}:")
        for match in matches:
            print(f"\t>> {diff_strings(filename, match)}")
            match_name = match + ".torrent"
            to_move = input(f"\t\tmove {match_name} ?")
            if to_move == "y":
                shutil.move(DL_FOLDER / match_name, TRASH_FOLDER / match_name)
            elif to_move == "f":
                shutil.move(str(file_), TRASH_FOLDER / file_.name)
