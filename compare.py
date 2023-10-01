import shutil
from difflib import SequenceMatcher, get_close_matches
from pathlib import Path
from typing import Iterator

DL_FOLDER = Path("/quirinalis/Bagarre/Torrent/")
TRASH_FOLDER = DL_FOLDER / "corbeille"
TRASH_FOLDER.mkdir(exist_ok=True)
CUTOFF = 0.9

ENABLE_SHORTCUTS =True 


def diff_strings(a: str, b: str) -> tuple[str, bool, bool]:
    output = []
    matcher = SequenceMatcher(None, a, b)

    green = "\x1b[38;5;16;48;5;2m"
    red = "\x1b[38;5;16;48;5;1m"
    endgreen = "\x1b[0m"
    endred = "\x1b[0m"

    is_new_extension = False
    is_same_file = False

    for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
        if opcode == "equal":
            output.append(a[a0:a1])
        elif opcode == "insert":
            insert = b[b0:b1]
            if insert == " (1)":
                is_same_file = True
            output.append(f"{green}{b[b0:b1]}{endgreen}")
        # elif opcode == "delete":
        #     output.append(f"{red}{a[a0:a1]}{endred}")
        elif opcode == "replace":
            replacement = b[b0:b1]
            if replacement.lower() in {"pdf", "epu"}:
                is_new_extension = True
            output.append(f"{green}{b[b0:b1]}{endgreen}")
            # output.append(f"{red}{a[a0:a1]}{endred}")

    return "".join(output), is_new_extension, is_same_file

def find_files_without_extension() -> None:
    for file_ in get_torrent_files():
        if file_.is_file() and not file_.suffix:
            print(f"File without extension: {file_}")
            file_.rename(file_.with_suffix(".torrent"))


def remove_zeros(file_path: Path) -> str:
    filename = file_path.stem

    if not filename.startswith("0"):
        return filename

    parts = filename.split(" ", 1)
    if len(parts) == 2 and all(x == "0" for x in parts[0]):
        new_filename = parts[1].lstrip()
        shutil.move(str(file_path), str(file_path.with_stem(new_filename)))
        filename = new_filename

    return filename


def get_torrent_files() -> Iterator[Path]:
    files = sorted(list(DL_FOLDER.glob("*.torrent")), key=lambda x: x.stem)
    for file_ in files:
        if file_.exists():
            yield file_

# find_files_without_extension()

for file_ in get_torrent_files():
    # filename = remove_zeros(file_.stem)
    # if not file_.with_stem(filename).exists():
    #     shutil.move(file_, file_.with_stem(filename))
    filename = file_.stem
    matches = get_close_matches(
        remove_zeros(file_),
        [remove_zeros(x) for x in DL_FOLDER.glob("*.torrent") if x.name != file_.name],
        n=2,
        cutoff=0.8,
    )
    if matches:
        print(f">>> {filename}:")
        for match in matches:
            diff, is_file_extension, is_same_file = diff_strings(filename, match)
            if ENABLE_SHORTCUTS and (is_file_extension or is_same_file):
                print(f"\t>> {diff}")
                match_name = match + ".torrent"
                to_move = input(f"\t\tmove {match_name} ?")
                if to_move == "y":
                    shutil.move(DL_FOLDER / match_name, TRASH_FOLDER / match_name)
                elif to_move == "f":
                    shutil.move(str(file_), TRASH_FOLDER / file_.name)
            elif not ENABLE_SHORTCUTS:
                print(f"\t>> {diff}")
                match_name = match + ".torrent"
                to_move = input(f"\t\tmove {match_name} ?")
                if to_move == "y":
                    shutil.move(DL_FOLDER / match_name, TRASH_FOLDER / match_name)
                elif to_move == "f":
                    shutil.move(str(file_), TRASH_FOLDER / file_.name)
