from pathlib import Path
from typing import Generator, Tuple

import pytest

from ..modules import syncutils


# @pytest.mark.only
def test_write_symlinks(
        tmp_path: Generator[Path, None, None],
) -> None:
    target_folder: Path = tmp_path/'source_folder'
    target_folder.mkdir(parents=True)
    link_folder: Path = tmp_path/'link_folder'
    target_paths: list[Path] = [
        target_folder/'test0_dir',
        target_folder/'test1.file',
        target_folder/'test2.file'
    ]
    for i, path in enumerate(target_paths):
        if i == 0:
            path.mkdir()
        else:
            path.touch()
    count: int = syncutils.write_symlinks(
        target_folder, link_folder
    )
    created_links: list[Path] = sorted(
        link_folder.glob('*'),
        key=lambda p: p.name
    )
    # Test the number of symlinks created
    assert count == len(target_paths)
    # Test that links are correct
    for l, t in zip(created_links, target_paths):
        assert l.readlink() == t
    # Test supplying link name
    link_name_list: tuple[str] = tuple([
        "custom0.link", "custom1.link", "custom2.link"
    ])
    syncutils.write_symlinks(
        target_folder, link_folder,
        link_name_list
    )
    for l, t in zip(
        sorted(
            link_folder.glob('custom*'),
            key=lambda p: p.name),
        target_paths
    ):
        assert l.readlink() == t
    # Test incorrect type link name
    with pytest.raises(TypeError):
        syncutils.write_symlinks(
            target_folder, link_folder,
            link_names=1
        )
    # Test incorrect length link name
    with pytest.raises(TypeError):
        syncutils.write_symlinks(
            target_folder, link_folder,
            link_names=tuple([])
        )


# @pytest.mark.only
def test_write_symlink(
        tmp_path: Generator[Path, None, None]
) -> None:
    target_folder: Path = tmp_path/'source_folder'
    target_folder.mkdir(parents=True)
    link_folder: Path = tmp_path/'link_folder'
    target_paths: list[Path] = [
        target_folder/'test0_dir',
        target_folder/'test1.file'
    ]
    link_paths: list[Path] = [
        link_folder/'test0_dir',
        link_folder/'test1.file'
    ]
    for i, path in enumerate(target_paths):
        if i == 0:
            path.mkdir()
        else:
            path.touch()
    for target in target_paths:
        syncutils.write_symlink(
            target, link_folder,
            target.name
        )
    created_links: list[Path] = sorted(
        link_folder.glob('*'),
        key=lambda p: p.name
    )
    # Test that links are correctly named
    assert created_links == link_paths
    # Test that paths are symlinks
    for l in created_links:
        assert l.is_symlink()
    # Test that links are correct
    for l, src in zip(created_links, target_paths):
        assert l.readlink() == src
    # Test that error is raised if existing incorrect links are found
    wrong_link: Path = link_paths[0]
    wrong_link.unlink()
    wrong_link.symlink_to(target_paths[-1])
    with pytest.raises(FileExistsError):
        syncutils.write_symlink(
            target_folder, link_folder,
            target.name
        )

# @pytest.mark.only
@pytest.mark.parametrize(
    "arg1, arg2, arg3",
    [
        pytest.param(
            "str", Path(""), "", id="wrong_target_type"
        ),
        pytest.param(
            Path(""), int(1), "", id="wrong_link_type"
        ),
        pytest.param(
            Path(""), Path(""), float(1), id="wrong_name_type"
        )
    ]
)
def test_write_symlink_argument_types(
    arg1: any, arg2: any, arg3: any
) -> None:
    # Test argument types
    with pytest.raises(TypeError):
        syncutils.write_symlink(
            arg1, arg2, arg3
        )
