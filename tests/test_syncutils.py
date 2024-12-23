from pathlib import Path
from typing import Generator, Tuple, Union

import pytest

from ..modules import syncutils
from .fixtures import(
    mock_target_folder
)


# @pytest.mark.only
def test_write_symlinks(
        mock_target_folder: Tuple[Path, list[Path], Path, list[Path]]
) -> None:
    link_folder, _, target_folder, target_paths = mock_target_folder
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
    # Test supplying link names
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
        assert l.is_symlink()
        assert l.readlink() == t


# @pytest.mark.only
@pytest.mark.parametrize(
    "link_names",
    [
        pytest.param(1, id="wrong_link_names_type"),
        pytest.param(tuple([]), id="wrong_link_names_length")
    ]
)
def test_write_symlinks_arguement_types(
        link_names: Union[int, tuple],
        mock_target_folder: Tuple[Path, list[Path], Path, list[Path]]
) -> None:
    link_folder, _, target_folder, _ = mock_target_folder
    # Test argument type and length
    with pytest.raises(TypeError):
        syncutils.write_symlinks(
            target_folder, link_folder,
            link_names
        )


# @pytest.mark.only
def test_write_symlink(
        mock_target_folder: Tuple[Path, list[Path], Path, list[Path]]
) -> None:
    link_folder, link_paths, _, target_paths = mock_target_folder
    for target in target_paths:
        syncutils.write_symlink(
            target, link_folder
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
    correct_target: Path = target_paths[0]
    wrong_target: Path = target_paths[-1]
    link: Path = link_paths[0]
    link.unlink()
    link.symlink_to(wrong_target)
    del link
    with pytest.raises(FileExistsError):
        syncutils.write_symlink(
            correct_target, link_folder
        )
    # Test that error is raised if target is not found
    fake_target: Path = Path('fake path')
    with pytest.raises(FileNotFoundError):
        syncutils.write_symlink(
            fake_target, link_folder
        )

# @pytest.mark.only
@pytest.mark.parametrize(
    "arg1, arg2, arg3",
    [
        pytest.param(
            "str", Path(""), "", id="wrong_target_type"
        ),
        pytest.param(
            Path(""), int(1), None, id="wrong_link_type"
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
