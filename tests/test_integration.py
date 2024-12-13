import pytest
from pathlib import Path

from crontest.crontest import parse_args, eval_source_file

def test_arg_num():
    # Not enough arguments
    args = ["crontest.py"]
    with pytest.raises(IndexError) as excinfo:
        parse_args(args)
        assert str(excinfo.value) == "Must have exactly 2 arguments"

    # Too many arguments
    args = ["crontest.py", "first", "second", "third"]
    with pytest.raises(IndexError) as excinfo:
        parse_args(args)
        assert str(excinfo.value) == "Must have exactly 2 arguments"

def test_find_folders():
    # Recognizes directories that exist
    args = ["chrontest.py", "tests/sourcedir", "tests/targetdir"]
    source, target = parse_args(args)

    assert source == Path("tests/sourcedir") 
    assert target == Path("tests/targetdir")

    # Rejects bad source dir
    args = ["chrontest.py", "fake/sourcedir", "tests/targetdir"]

    with pytest.raises(FileNotFoundError) as excinfo:
        parse_args(args)
        assert str(excinfo.value) == "Source folder does not exist"

    # Rejects bad target dir
    args = ["chrontest.py", "test/sourcedir", "fake/targetdir"]

    with pytest.raises(FileNotFoundError) as excinfo:
        parse_args(args)
        assert str(excinfo.value) == "Target folder does not exist"

def test_file_eval():
    args = ["chrontest.py", "tests/sourcedir", "tests/targetdir"]
    source, target = parse_args(args)

    # Accepts a file that doesn't exist in target
    assert eval_source_file(
        Path("tests/sourcedir/docone.csv"),
        target
    ) == True

    # Rejects a file that does exist in target, same name, different hash
    assert eval_source_file(
        Path("tests/sourcedir/doctwo.csv"),
        target
    ) == False

    # Rejects a file that does exist in target, same hash, different name
    assert eval_source_file(
        Path("tests/sourcedir/docfour.csv"),
        target
    ) == False
    

def test_misc():
    args = ["chrontest.py", "tests/sourcedir", "tests/targetdir"]

    source, target = parse_args(args)

    files = [file.name for file in source.iterdir()]

    assert files == ["docfour.csv", "docone.csv", "doctwo.csv"]
