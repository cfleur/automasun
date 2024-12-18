from pathlib import Path
from typing import Union


def write_symlinks(
        target_folder_path: Union[str, Path],
        link_folder_path: Union[str, Path],
        link_names: Union[None, tuple[str]] = None,
        v: bool = False
) -> int:
    """
    Writes symlinks in link directory that point to files in a
    target directory. Creates a link directory if it doesn't exist.
    Works for directories and files.
    """
    link_dir = Path(link_folder_path)
    link_dir.mkdir(parents=True, exist_ok=True)
    target_dir = Path(target_folder_path)
    target_items = sorted(
        target_dir.glob('*'),
        key=lambda p: p.name
    )
    symlink_count = 0
    if link_names is not None:
        if not isinstance(link_names, tuple) or len(link_names) != len(target_items):
            raise TypeError(
                "Link names should be a tuple with the same length as files in target directory."
                f"Found {len(target_items)} in target directory."
                f" Got type {type(link_names)} of length {len(link_names)}."
            )
        for source_item, link_name in zip(target_items, link_names):
            symlink_count += write_symlink(
                source_item, link_dir,
                link_name, v=v
            )
    else:
        for source_item in target_items:
            symlink_count += write_symlink(
                source_item, link_dir,
                source_item.name, v=v
            )
    print(f"***\n{symlink_count} symlinks written.")
    return symlink_count


def write_symlink(
        target_path: Path,
        link_dir: Path,
        link_name: str,
        v: bool = False
) -> int:
    """
    Writes a single symlink from link_dir/link_name -> target_path.
    """
    for obj, t in zip(
        (target_path, link_dir, link_name),
        (Path, Path, str)
    ):
        if not isinstance(obj, t):
            raise TypeError(
                f"{obj} must be type {t}. Got {type(obj)}."
            )
    link_dir.mkdir(parents=True, exist_ok=True)
    link_path: Path = link_dir/link_name
    try:
        link_path.symlink_to(target_path)
        if v:
            print(
                f"Symlink created: {link_path} -> {target_path}"
            )
        return 1
    except FileExistsError:
        if link_path.is_symlink() and link_path.readlink() == target_path:
            print(
                f"Existing symlink found: {link_path} -> {target_path}. Skipping."
            )
        else:
            print(
                f"File {link_path} exists but does not point to {target_path}."
                " Check and try again."
            )
            raise
    except OSError as e:
        print(
            f"Error accessing {target_path} or {link_path}. Check e.g. permissions.",
            e
        )
