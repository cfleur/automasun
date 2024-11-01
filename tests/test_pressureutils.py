from io import StringIO
from pathlib import Path

from ..modules import pressureutils

# @pytest.fixture
# def mock_config():
#     return {
#         'pressure': {
#             'raw_pressure_folder': temp_path
#         }
#     }

# def test_generate_unparsed_file_list() -> None:
#     mock_config = """
# """

def test_preprocess_case_log_file(tmp_path):
    content: str = '='
    file: Path = tmp_path/'tmp_raw_file.txt'
    file.write_text(content)
    preprocessed_file: StringIO = pressureutils.preprocess_case_log_file(
        file
    )
    assert preprocessed_file.read() == ' '
