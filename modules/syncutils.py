from pathlib import Path
from typing import Union


def write_symlinks(
        target_folder_path: Union[str, Path],
        link_folder_path: Union[str, Path],
        link_names: Union[None, tuple[str]] = None,
        resolve_path: bool = True,
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
        for target_item, link_name in zip(target_items, link_names):
            try:
                symlink_count += write_symlink(
                    target_item, link_dir,
                    link_name, resolve_path=resolve_path,
                    v=v
                )
            except Exception as e:
                if v:
                    print(
                        f"Problem linking {target_item} -> {link_dir/link_name}", e
                    )
    else:
        for target_item in target_items:
            try:
                symlink_count += write_symlink(
                    target_item, link_dir,
                    target_item.name, resolve_path=resolve_path,
                    v=v
                )
            except Exception as e:
                if v:
                    print(
                        f"Problem linking {target_item} -> {link_dir/target_item.name}", e
                    )
    print(
        f"******\n{symlink_count} symlinks written."
        f" Link folder: {link_dir} -> Target folder: {target_dir}\n******"
    )
    return symlink_count


def write_symlink(
        target_path: Path,
        link_dir: Path,
        link_name: Union[str, None] = None,
        resolve_path: bool = True,
        v: bool = False
) -> int:
    """
    Writes a single symlink from link_dir/link_name -> target_path.
    resolve_path flag set to True will ensure paths are absolute
    and if a target is a symlink, the new symlink will point to the
    original target. Set this flag to False to suppress modification
    of target path.
    """
    for obj, t in zip(
        (target_path, link_dir, link_name),
        (Path, Path, (str, type(None)))
    ):
        if not isinstance(obj, t):
            raise TypeError(
                f"{obj} must be type {t}. Got {type(obj)}."
            )
    if target_path.exists():
        if resolve_path and not target_path.is_absolute():
            target_path = target_path.resolve()
    else:
        raise FileNotFoundError(
            f"Error!\n> Target {target_path} not found."
        )
    link_dir.mkdir(parents=True, exist_ok=True)
    if link_name is None:
        link_path: Path = link_dir/target_path.name
    else:
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
            if v:
                print(
                    f"Existing symlink found: {link_path} -> {target_path}. Skipping."
                )
            return 0
        else:
            print(
                f"Error!\n> File {link_path} exists but does not point to {target_path}."
                " Check and try again."
            )
            raise
    except OSError as e:
        print(
            f"Error!\n> Error accessing {target_path} or {link_path}."
            f" Check e.g. permissions or tha file exists.",
            e
        )
